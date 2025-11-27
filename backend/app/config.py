from typing import List

# Universe of tickers will add back and expand to 200 later
TICKERS: List[str] = [
    "AAPL",
    "MSFT",
    # "GOOG",
    # "AMZN",
    # "TSLA",
]

START_DATE = "2015-01-01"
END_DATE = "2020-12-31"

# Labeling configuration
LABEL_HORIZON_DAYS = 10      # look-ahead window
BUY_THRESHOLD = 0.05          # +1%
SELL_THRESHOLD = -0.05        # -1%

# Features used for model training
FEATURE_COLS = [
    "daily_return",
    "ma_5",
    "ma_10",
    "momentum_14",
    "volume_zscore_20",
]
