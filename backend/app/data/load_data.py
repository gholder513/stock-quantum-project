from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
import yfinance as yf

from app import config


# -----------------------------------------------------------
# Paths
# -----------------------------------------------------------
# This file lives at: backend/app/data/load_data.py
# parents:
#   0 -> data
#   1 -> app
#   2 -> backend (locally) or /app (in container)
BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"
DATA_DIR = BACKEND_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# Download raw data for one ticker
def download_raw_data(ticker: str) -> pd.DataFrame:
    """
    Download daily OHLCV data for a single ticker from Yahoo Finance.
    Cache it in data/raw/<TICKER>_START_END.csv.
    """
    raw_path = RAW_DIR / f"{ticker}_{config.START_DATE}_{config.END_DATE}.csv"
    if raw_path.exists():
        df = pd.read_csv(raw_path)
        return df

    print(f"Downloading data for {ticker} from Yahoo Finance...")
    df = yf.download(
        ticker,
        start=config.START_DATE,
        end=config.END_DATE,
        auto_adjust=False,
        progress=False,
    )

    # Ensure DataFrame
    df = pd.DataFrame(df)

    if df.empty:
        raise ValueError(f"No data downloaded for ticker {ticker}")

    # Flatten possible MultiIndex columns from yfinance
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Normalize column names (strip spaces)
    df.columns = [str(c).strip() for c in df.columns]

    # Ensure we have "Adj Close"
    if "Adj Close" not in df.columns:
        if "Close" in df.columns:
            df["Adj Close"] = df["Close"]
        else:
            raise ValueError(f"'Adj Close' (or 'Close') column not found for {ticker}")

    # Ensure we have "Volume"
    if "Volume" not in df.columns:
        raise ValueError(f"'Volume' column not found for {ticker}")

    # Make Date a column
    df.reset_index(inplace=True)
    if "Date" not in df.columns:
        if isinstance(df.index, pd.DatetimeIndex):
            df["Date"] = df.index
        else:
            raise ValueError(f"No 'Date' column or DatetimeIndex for {ticker}")

    # Normalize Date and add ticker
    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
    df["ticker"] = ticker

    df.to_csv(raw_path, index=False)
    return df



# Feature engineering + labels for one ticker
def build_features_and_labels(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add engineered features and BUY/HOLD/SELL labels to a raw OHLCV df.

    Uses only:
        - daily_return
        - ma_5
        - ma_10
        - momentum_14
        - volume_zscore_20
    """
    df = df.copy()

    # Ensure Date exists and sorted
    if "Date" not in df.columns:
        raise ValueError("Expected 'Date' column in dataframe")
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")

    # Make sure Adj Close & Volume are proper 1-D Series
    if "Adj Close" not in df.columns:
        raise ValueError("'Adj Close' column missing before feature engineering")
    if "Volume" not in df.columns:
        raise ValueError("'Volume' column missing before feature engineering")

    adj = df["Adj Close"]
    if isinstance(adj, pd.DataFrame):
        adj = adj.iloc[:, 0]

    vol = df["Volume"]
    if isinstance(vol, pd.DataFrame):
        vol = vol.iloc[:, 0]

    df["Adj Close"] = pd.to_numeric(adj, errors="coerce")
    df["Volume"] = pd.to_numeric(vol, errors="coerce")

    # Daily return
    df["daily_return"] = df["Adj Close"].pct_change()

    # Moving averages
    df["ma_5"] = df["Adj Close"].rolling(window=5, min_periods=5).mean()
    df["ma_10"] = df["Adj Close"].rolling(window=10, min_periods=10).mean()

    # Momentum (14-day simple momentum)
    df["momentum_14"] = df["Adj Close"] - df["Adj Close"].shift(14)

    # 4. Volume z-score over last 20 days
    vol_rolling_mean = df["Volume"].rolling(window=20, min_periods=20).mean()
    vol_rolling_std = df["Volume"].rolling(window=20, min_periods=20).std()
    df["volume_zscore_20"] = (df["Volume"] - vol_rolling_mean) / vol_rolling_std.replace(
        0, np.nan
    )

    # Label creation
    H = config.LABEL_HORIZON_DAYS
    future_price = df["Adj Close"].shift(-H)
    current_price = df["Adj Close"]
    future_return = (future_price - current_price) / current_price

    # Assigning labels
    df["label"] = "HOLD"
    df.loc[future_return > config.BUY_THRESHOLD, "label"] = "BUY"
    df.loc[future_return < config.SELL_THRESHOLD, "label"] = "SELL"

    # Drop rows where any feature or label is undefined
    cols_needed = ["Adj Close", "Volume"] + config.FEATURE_COLS + ["label"]
    missing_cols = [c for c in cols_needed if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns after feature engineering: {missing_cols}")

    df = df.dropna(subset=cols_needed)

    if df.empty:
        raise ValueError("All rows dropped after removing NaNs; not enough data.")

    # Convert Date back to ISO string for consistency
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

    return df


def build_or_load_processed_ticker(ticker: str) -> pd.DataFrame:
    """
    Return processed data (features + labels) for a single ticker,
    caching it in data/processed/<TICKER>_features_labels.csv
    
    Only load existing files, don't download in production.
    """
    processed_path = PROCESSED_DIR / f"{ticker}_features_labels.csv"
    if processed_path.exists():
        return pd.read_csv(processed_path)

    # Don't download in production (raises error instead)
    raise FileNotFoundError(
        f"Processed data not found at {processed_path}. "
        f"Please run data processing locally and commit the files to Git."
    )


def load_or_build_all_data(tickers: List[str] = None) -> pd.DataFrame:
    """
    Load processed data for all tickers from disk and concatenate into one DataFrame.
    
    MODIFIED: Only loads existing files, never downloads fresh data.
    This prevents memory issues on deployment platforms.
    """
    import traceback

    if tickers is None:
        tickers = config.TICKERS

    # Check if processed directory has files
    processed_files = list(PROCESSED_DIR.glob("*_features_labels.csv"))
    
    if not processed_files:
        raise RuntimeError(
            f"No processed data files found in {PROCESSED_DIR}. "
            f"Please run data processing locally first and commit the CSV files to Git."
        )

    print(f"Found {len(processed_files)} processed data files in {PROCESSED_DIR}")

    frames = []
    for t in tickers:
        try:
            processed_path = PROCESSED_DIR / f"{t}_features_labels.csv"
            if processed_path.exists():
                print(f"Loading ticker {t} from {processed_path.name}...")
                df_t = pd.read_csv(processed_path)
                frames.append(df_t)
            else:
                print(f"Warning: No processed file found for ticker {t}, skipping...")
        except Exception as e:
            print(f"Error loading {t}: {e!r}")
            traceback.print_exc()

    if not frames:
        raise RuntimeError("No data could be loaded from any ticker.")

    full_df = pd.concat(frames, ignore_index=True)
    full_df["Date"] = full_df["Date"].astype(str)

    print(f"Loaded {len(full_df)} total rows from {len(frames)} tickers")
    return full_df