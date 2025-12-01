from pathlib import Path
import time
import json

import numpy as onp  # ordinary numpy for I/O
import pennylane as qml
import pennylane.numpy as np  # autograd-compatible numpy

from app import config
from app.data.load_data import load_or_build_all_data
from app.models.quantum import _prepare_angles, QNN_WEIGHTS_PATH


ROOT_DIR = Path(__file__).resolve().parents[1]
MODELS_DIR = ROOT_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
TRAIN_TIMES_PATH = MODELS_DIR / "train_times.json"

# Label encoding
def _encode_labels_to_one_hot(labels):
    """
    Map string labels BUY/HOLD/SELL to one-hot vectors [1,0,0], [0,1,0], [0,0,1].
    """
    mapping = {"BUY": 0, "HOLD": 1, "SELL": 2}
    idx = [mapping[l] for l in labels]
    one_hot = np.zeros((len(labels), 3))
    for i, j in enumerate(idx):
        one_hot[i, j] = 1.0
    return one_hot


def load_training_data(max_samples: int = 2000):
    """
    Load feature matrix X and one-hot labels Y for training the QNN.
    We subsample to max_samples for speed.
    """
    print("Loading data for quantum QNN training...")
    df = load_or_build_all_data()

    X = df[config.FEATURE_COLS].values.astype(float)
    y_str = df["label"].values

    # one-hot encode
    Y = _encode_labels_to_one_hot(y_str)

    # subsample for speed (optional)
    n = min(max_samples, X.shape[0])
    X = X[:n]
    Y = Y[:n]

    print(f"Using {n} samples for quantum training.")
    return X, Y



# QNode and model
dev = qml.device("default.qubit", wires=2)


@qml.qnode(dev, interface="autograd")
def qnn_circuit(angles, weights):
    """
    Same structure as inference QNN:

      - encode angles as RY rotations
      - CZ entanglement
      - trainable RY layer
    """
    qml.RY(angles[0], wires=0)
    qml.RY(angles[1], wires=1)
    qml.CZ(wires=[0, 1])
    qml.RY(weights[0], wires=0)
    qml.RY(weights[1], wires=1)
    return qml.probs(wires=[0, 1])


def qnn_forward(x, weights):
    """
    x: raw feature vector (shape (F,))
    weights: trainable parameters (shape (2,))
    returns: 3-prob vector (BUY, HOLD, SELL)
    """
    angles = _prepare_angles(x, num_qubits=2)
    probs4 = qnn_circuit(angles, weights)  # length-4

    # map to 3 classes analytically, keeping it differentiable
    p00, p01, p10, p11 = probs4[0], probs4[1], probs4[2], probs4[3]
    p_buy = p00
    p_hold = p01
    p_sell = p10 + p11
    total = p_buy + p_hold + p_sell
    return np.stack([p_buy / total, p_hold / total, p_sell / total])


def cross_entropy(preds, targets):
    """
    preds: (3,) probabilities
    targets: (3,) one-hot
    """
    eps = 1e-8
    preds = np.clip(preds, eps, 1.0 - eps)
    return -np.sum(targets * np.log(preds))


def cost(weights, X, Y):
    """
    Average cross-entropy over a batch.
    """
    losses = []
    for x, y in zip(X, Y):
        p = qnn_forward(x, weights)
        losses.append(cross_entropy(p, y))
    return np.mean(np.stack(losses))



# Training loop

def train_qnn(
    num_epochs: int = 15,
    stepsize: float = 0.2,
    max_samples: int = 2000,
):
    X, Y = load_training_data(max_samples=max_samples)

    # Initialize weights small random
    weights = np.array([0.1, -0.1], requires_grad=True)

    opt = qml.GradientDescentOptimizer(stepsize=stepsize)

    for epoch in range(num_epochs):
        weights, current_cost = opt.step_and_cost(lambda w: cost(w, X, Y), weights)
        print(f"Epoch {epoch+1}/{num_epochs} - cost: {current_cost:.4f}")

    # Convert to plain numpy and save
    final_weights = onp.array(weights, dtype=float)
    QNN_WEIGHTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    onp.save(QNN_WEIGHTS_PATH, final_weights)
    print(f"Saved trained QNN weights to {QNN_WEIGHTS_PATH}")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[0]
    print(f"Running quantum QNN training from {root}")

    t0 = time.time()
    train_qnn()
    t_qnn = time.time() - t0
    print(f"[Timing] Quantum QNN training time: {t_qnn:.3f} seconds")

    if TRAIN_TIMES_PATH.exists():
        try:
            existing = json.load(TRAIN_TIMES_PATH.open("r"))
        except Exception:
            existing = {}
    else:
        existing = {}

    existing["quantum_qnn"] = t_qnn
    with TRAIN_TIMES_PATH.open("w") as f:
        json.dump(existing, f, indent=2)

    print(f"[Timing] Saved training times to {TRAIN_TIMES_PATH}")