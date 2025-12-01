# current actual file that I have locally
from pathlib import Path
from typing import Dict, Sequence

import math
import numpy as np

from app.schemas import Decision

#  Qiskit imports for VQC-style model 
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

# PennyLane imports (for QNN-style model) 
import pennylane as qml

# paths and constants
DECISIONS: Sequence[Decision] = ["BUY", "HOLD", "SELL"]

ROOT_DIR = Path(__file__).resolve().parents[3]
MODELS_DIR = ROOT_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

QNN_WEIGHTS_PATH = MODELS_DIR / "quantum_qnn_weights.npy"

# We'll lazily load weights the first time we need them
_QNN_WEIGHTS: np.ndarray | None = None


def _softmax(logits: np.ndarray) -> np.ndarray:
    logits = np.array(logits, dtype=float)
    logits = logits - np.max(logits)
    exp = np.exp(logits)
    return exp / np.sum(exp)


def _prepare_angles(features: np.ndarray, num_qubits: int = 2) -> np.ndarray:
    """
    Take the raw feature vector and turn it into a small set of angles
    suitable for driving quantum rotations.

    - Flatten to 1D
    - Pad/trim to num_qubits
    - Squash with tanh to keep values in a stable range
    - Scale to [-pi, pi]
    """
    x = np.array(features, dtype=float).ravel()

    if x.size < num_qubits:
        x = np.pad(x, (0, num_qubits - x.size), mode="constant")
    else:
        x = x[:num_qubits]

    x = np.tanh(x) * math.pi
    return x


def _map_probs_2qubits_to_decisions(probs: np.ndarray) -> Dict[Decision, float]:
    """
    Map 2-qubit measurement probabilities (length-4 vector: [p00,p01,p10,p11])
    onto 3 decision classes BUY/HOLD/SELL.

    Example mapping:
      - BUY  <- |00>
      - HOLD <- |01>
      - SELL <- |10> or |11>
    """
    probs = np.asarray(probs, dtype=float).ravel()
    if probs.size != 4:
        raise ValueError(f"Expected 4 probabilities for 2 qubits, got {probs.size}")

    p00, p01, p10, p11 = probs.tolist()

    p_buy = p00
    p_hold = p01
    p_sell = p10 + p11

    total = p_buy + p_hold + p_sell
    if total <= 0:
        return {"BUY": 1 / 3, "HOLD": 1 / 3, "SELL": 1 / 3}

    return {
        "BUY": float(p_buy / total),
        "HOLD": float(p_hold / total),
        "SELL": float(p_sell / total),
    }


# Qiskit VQC-style model (still untrained baseline)
def _qiskit_vqc_probs(features: np.ndarray) -> np.ndarray:
    """
    Build a tiny 2-qubit parameterized circuit, encode features as rotations,
    and simulate its statevector using Qiskit. Return the 4 outcome probabilities.
    """
    num_qubits = 2
    angles = _prepare_angles(features, num_qubits=num_qubits)

    qc = QuantumCircuit(num_qubits)
    # Simple angle encoding
    qc.ry(angles[0], 0)
    qc.ry(angles[1], 1)
    # A bit of entanglement
    qc.cz(0, 1)

    # measurements; use Statevector to get probabilities directly.
    state = Statevector.from_instruction(qc)
    probs = state.probabilities()  # length-4 array
    return probs


def quantum_vqc_predict(features: np.ndarray) -> Dict[Decision, float]:
    """
    Quantum Variational Classifier (simulated) using Qiskit.

    This is a very small, fixed-parameter circuit:
      - encodes features as Ry rotations
      - applies an entangling CZ gate
      - uses the resulting state probabilities as a nonlinear feature map
      - maps those probabilities to BUY/HOLD/SELL.
    """
    probs_4 = _qiskit_vqc_probs(features)
    decision_probs = _map_probs_2qubits_to_decisions(probs_4)
    return decision_probs


# PennyLane-based trained QNN

# A tiny device with 2 qubits; we reuse it for inference
_pl_dev = qml.device("default.qubit", wires=2)


@qml.qnode(_pl_dev)
def _pl_qnn_circuit(angles, weights):
    """
    Simple QNode for inference:

      - encodes angles as Ry rotations
      - applies CZ entanglement
      - applies trainable Ry rotations with parameters "weights"
      - returns the full probability distribution over 2 qubits
    """
    # Feature encoding
    qml.RY(angles[0], wires=0)
    qml.RY(angles[1], wires=1)

    # Entanglement
    qml.CZ(wires=[0, 1])

    # Trainable layer
    qml.RY(weights[0], wires=0)
    qml.RY(weights[1], wires=1)

    return qml.probs(wires=[0, 1])


def _load_qnn_weights() -> np.ndarray:
    """
    Load trained weights for the quantum QNN from disk.
    If the file is missing, raise a clear error message.
    """
    global _QNN_WEIGHTS
    if _QNN_WEIGHTS is not None:
        return _QNN_WEIGHTS

    if not QNN_WEIGHTS_PATH.exists():
        raise RuntimeError(
            f"Quantum QNN weights not found at {QNN_WEIGHTS_PATH}. "
            f"Run the training script (train_quantum_qnn.py) first."
        )

    _QNN_WEIGHTS = np.load(QNN_WEIGHTS_PATH)
    return _QNN_WEIGHTS


def quantum_qnn_predict(features: np.ndarray) -> Dict[Decision, float]:
    """
    Quantum Neural Network (simulated) using PennyLane, *with trained weights*.

    - Loads trainable parameters from models/quantum_qnn_weights.npy.
    - Runs the QNode on the given features.
    - Maps 2-qubit probabilities to BUY/HOLD/SELL.
    """
    weights = _load_qnn_weights()
    angles = _prepare_angles(features, num_qubits=2)

    # QNode expects plain numpy arrays and returns a length-4 array
    probs_4 = _pl_qnn_circuit(angles, weights)
    decision_probs = _map_probs_2qubits_to_decisions(probs_4)
    return decision_probs
