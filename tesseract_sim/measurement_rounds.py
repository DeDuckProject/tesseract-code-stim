import stim
from .encoding_manual import measurement_operators_rows, measurement_operators_columns
from .noise_utils import append_1q, append_2q
from .noise_cfg import NoiseCfg, NO_NOISE

def get_qubits_and_ancillas():
    """
    the two ancilla qubits are for the X and Z measurements, respectively.
    """
    return list(range(16)), 16, 17


def measure_x_z_stabilizer(circuit, data_qubits, x_ancilla, z_ancilla, cfg: NoiseCfg = NO_NOISE):
    """
    Appends a circuit to measure X and Z stabilizers on data_qubits.
    Based on Fig 4(d) of the paper.
    X stabilizer is measured on x_ancilla.
    Z stabilizer is measured on z_ancilla. The Z measurement also acts as a flag for the X measurement.
    """
    # Reset for fresh ancillas
    append_1q(circuit, "R", x_ancilla, phase="ec", cfg=cfg)
    append_1q(circuit, "R", z_ancilla, phase="ec", cfg=cfg)

    append_1q(circuit, "H", x_ancilla, phase="ec", cfg=cfg)
    for q in data_qubits:
        append_2q(circuit, "CNOT", x_ancilla, q, phase="ec", cfg=cfg)
    for q in data_qubits:
        append_2q(circuit, "CNOT", q, z_ancilla, phase="ec", cfg=cfg)
    append_1q(circuit, "H", x_ancilla, phase="ec", cfg=cfg)

    # In stim, the order of measurements in a single M command matters for rec targeting.
    # M x_ancilla, z_ancilla means x is rec(-2), z is rec(-1)
    append_2q(circuit, "M", x_ancilla, z_ancilla, phase="ec", cfg=cfg)

def error_correction_round_rows(circuit, cfg: NoiseCfg = NO_NOISE):
    """
    Appends one round of row-based stabilizer measurements to the circuit.
    Measures X and Z stabilizers for each of the 4 rows.
    """
    _, x_ancilla, z_ancilla = get_qubits_and_ancillas()
    for row in measurement_operators_rows:
        measure_x_z_stabilizer(circuit, row, x_ancilla, z_ancilla, cfg=cfg)


def error_correction_round_columns(circuit, cfg: NoiseCfg = NO_NOISE):
    """
    Appends one round of column-based stabilizer measurements to the circuit.
    Measures X and Z stabilizers for each of the 4 columns.
    """
    _, x_ancilla, z_ancilla = get_qubits_and_ancillas()
    for col in measurement_operators_columns:
        measure_x_z_stabilizer(circuit, col, x_ancilla, z_ancilla, cfg=cfg)


def error_correct_manual(circuit, rounds=3, cfg: NoiseCfg = NO_NOISE):
    for i in range(rounds):
        error_correction_round_rows(circuit, cfg=cfg)
        error_correction_round_columns(circuit, cfg=cfg) 