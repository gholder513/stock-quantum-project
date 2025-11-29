from app.models.classical import (
    train_and_save_random_forest,
    train_and_save_logreg,
    train_and_save_svm_linear,
)

if __name__ == "__main__":
    train_and_save_random_forest()
    train_and_save_logreg()
    train_and_save_svm_linear()
