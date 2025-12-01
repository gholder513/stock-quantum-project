from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from app import config
from app.data.load_data import load_or_build_all_data

# Project root: .../stock-quantum-project
ROOT_DIR = Path(__file__).resolve().parents[3]
MODELS_DIR = ROOT_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

RF_MODEL_PATH = MODELS_DIR / "random_forest.pkl"
LOGREG_MODEL_PATH = MODELS_DIR / "logreg.pkl"
SVM_MODEL_PATH = MODELS_DIR / "svm_linear.pkl"


def _train_test_split(df):
    X = df[config.FEATURE_COLS].values
    y = df["label"].values

    return train_test_split(
        X,
        y,
        test_size=0.2,
        shuffle=True,
        stratify=y,
        random_state=42,
    )


def train_and_save_random_forest() -> None:
    """
    Train a RandomForest classifier on the full (imbalanced) dataset and save it.
    """
    print("Loading data for training (Random Forest)...")
    df = load_or_build_all_data()

    print("Label distribution:")
    print(df["label"].value_counts())
    print("Label distribution (normalized):")
    print(df["label"].value_counts(normalize=True))

    X_train, X_test, y_train, y_test = _train_test_split(df)

    pipeline = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("clf", RandomForestClassifier(
                n_estimators=200,
                random_state=42,
                n_jobs=-1,
            )),
        ]
    )

    print("Training Random Forest...")
    pipeline.fit(X_train, y_train)

    acc = pipeline.score(X_test, y_test)
    print(f"Random Forest accuracy on held-out data: {acc:.3f}")

    joblib.dump(pipeline, RF_MODEL_PATH)
    print(f"Saved Random Forest model to {RF_MODEL_PATH}")


def train_and_save_logreg() -> None:
    """
    Train a multinomial Logistic Regression classifier and save it.
    """
    print("Loading data for training (Logistic Regression)...")
    df = load_or_build_all_data()

    X_train, X_test, y_train, y_test = _train_test_split(df)

    pipeline = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(
                multi_class="multinomial",
                max_iter=1000,
                n_jobs=-1,
                random_state=42,
            )),
        ]
    )

    print("Training Logistic Regression...")
    pipeline.fit(X_train, y_train)

    acc = pipeline.score(X_test, y_test)
    print(f"Logistic Regression accuracy on held-out data: {acc:.3f}")

    joblib.dump(pipeline, LOGREG_MODEL_PATH)
    print(f"Saved Logistic Regression model to {LOGREG_MODEL_PATH}")


def train_and_save_svm_linear() -> None:
    """
    Train a linear-kernel SVM (with probability estimates enabled) and save it.
    """
    print("Loading data for training (Linear SVM)...")
    df = load_or_build_all_data()

    X_train, X_test, y_train, y_test = _train_test_split(df)

    pipeline = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("clf", SVC(
                kernel="linear",
                probability=True,  # needed for predict_proba
                random_state=42,
            )),
        ]
    )

    print("Training Linear SVM...")
    pipeline.fit(X_train, y_train)

    acc = pipeline.score(X_test, y_test)
    print(f"Linear SVM accuracy on held-out data: {acc:.3f}")

    joblib.dump(pipeline, SVM_MODEL_PATH)
    print(f"Saved Linear SVM model to {SVM_MODEL_PATH}")


def get_random_forest_model():
    if not RF_MODEL_PATH.exists():
        train_and_save_random_forest()
    return joblib.load(RF_MODEL_PATH)


def get_logreg_model():
    if not LOGREG_MODEL_PATH.exists():
        train_and_save_logreg()
    return joblib.load(LOGREG_MODEL_PATH)


def get_svm_model():
    if not SVM_MODEL_PATH.exists():
        train_and_save_svm_linear()
    return joblib.load(SVM_MODEL_PATH)


if __name__ == "__main__":
    # Train all three classical models when this file is run directly
    train_and_save_random_forest()
    train_and_save_logreg()
    train_and_save_svm_linear()
