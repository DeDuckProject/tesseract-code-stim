from .noise_utils import append_1q, append_2q
from .noise_cfg import NoiseCfg, NO_NOISE


# This file contains the functions for encoding the state |++0000> as described in Fig. 9a of that paper

def encode_sub_circuit_quad(circuit, ancilla, qubits, cfg: NoiseCfg = NO_NOISE):
    append_2q(circuit, "CNOT", qubits[0], ancilla, phase="enc", cfg=cfg) # Flag qubit
    append_2q(circuit, "CNOT", qubits[0], qubits[1], phase="enc", cfg=cfg)
    append_2q(circuit, "CNOT", qubits[0], qubits[2], phase="enc", cfg=cfg)
    append_2q(circuit, "CNOT", qubits[0], qubits[3], phase="enc", cfg=cfg)
    append_2q(circuit, "CNOT", qubits[0], ancilla, phase="enc", cfg=cfg) # Flag qubit

def add_cnot_gates(circuit, start1, start2, num_gates=4, cfg: NoiseCfg = NO_NOISE):
    """
    Adds CNOT gates to the circuit.

    Parameters:
    - circuit: The quantum circuit object to modify.
    - start1: The starting index for the first qubit in the CNOT pairs.
    - start2: The starting index for the second qubit in the CNOT pairs.
    - num_gates: The number of CNOT gates to append (default is 4).
    """
    for i in range(num_gates):
        append_2q(circuit, "CNOT", start1 + i, start2 + i, phase="enc", cfg=cfg)

def encode_manual_fig9a(circuit, cfg: NoiseCfg = NO_NOISE):
    # Here we encode the state |++0000> as can be seen in Fig. 9a of that paper
    # initialize qubits:
    append_1q(circuit, "H", 0, phase="enc", cfg=cfg)
    append_1q(circuit, "H", 1, phase="enc", cfg=cfg)
    append_1q(circuit, "H", 2, phase="enc", cfg=cfg)
    append_1q(circuit, "H", 3, phase="enc", cfg=cfg)
    append_1q(circuit, "H", 4, phase="enc", cfg=cfg)
    append_1q(circuit, "H", 8, phase="enc", cfg=cfg)
    append_1q(circuit, "H", 12, phase="enc", cfg=cfg)

    encode_sub_circuit_quad(circuit, 20, [4, 5, 6, 7], cfg=cfg)
    encode_sub_circuit_quad(circuit, 21, [8, 9, 10, 11], cfg=cfg)
    encode_sub_circuit_quad(circuit, 22, [12, 13, 14, 15], cfg=cfg)

    add_cnot_gates(circuit, 0, 16, cfg=cfg) # working on ancilla qubits as flag qubits
    add_cnot_gates(circuit, 0, 4, cfg=cfg)
    add_cnot_gates(circuit, 0, 8, cfg=cfg)
    add_cnot_gates(circuit, 0, 12, cfg=cfg)
    add_cnot_gates(circuit, 0, 16, cfg=cfg) # working on ancilla qubits as flag qubits

    append_1q(circuit, "R", 18, phase="enc", cfg=cfg)
    append_1q(circuit, "R", 19, phase="enc", cfg=cfg) # Reset ancillas 18,19 since their role is done and we need them for the following
    append_1q(circuit, "H", 19, phase="enc", cfg=cfg)
    append_2q(circuit, "CNOT", 19, 18, phase="enc", cfg=cfg) # cnot to flag qubit
    append_2q(circuit, "CNOT", 19, 0, phase="enc", cfg=cfg) # measuring stabilizer
    append_2q(circuit, "CNOT", 19, 1, phase="enc", cfg=cfg) # measuring stabilizer
    append_2q(circuit, "CNOT", 19, 2, phase="enc", cfg=cfg) # measuring stabilizer
    append_2q(circuit, "CNOT", 19, 3, phase="enc", cfg=cfg) # measuring stabilizer
    append_2q(circuit, "CNOT", 19, 18, phase="enc", cfg=cfg) # cnot to flag qubit 