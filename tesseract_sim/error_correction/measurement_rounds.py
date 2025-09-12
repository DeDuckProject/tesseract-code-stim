from tesseract_sim.common.code_commons import measurement_operators_rows, measurement_operators_columns
from tesseract_sim.noise.noise_utils import append_1q, append_2q
from tesseract_sim.noise.noise_cfg import NoiseCfg, NO_NOISE


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

    append_1q(circuit, "H", x_ancilla, phase="ec", cfg=cfg)  # x ancilla should be in |+>

    append_2q(circuit, "CNOT", data_qubits[0], z_ancilla, phase="ec", cfg=cfg)
    append_2q(circuit, "CNOT", x_ancilla, data_qubits[1], phase="ec", cfg=cfg)
    append_2q(circuit, "CNOT", data_qubits[1], z_ancilla, phase="ec", cfg=cfg)
    append_2q(circuit, "CNOT", x_ancilla, data_qubits[0], phase="ec", cfg=cfg)
    append_2q(circuit, "CNOT", data_qubits[2], z_ancilla, phase="ec", cfg=cfg)
    append_2q(circuit, "CNOT", x_ancilla, data_qubits[3], phase="ec", cfg=cfg)
    append_2q(circuit, "CNOT", data_qubits[3], z_ancilla, phase="ec", cfg=cfg)
    append_2q(circuit, "CNOT", x_ancilla, data_qubits[2], phase="ec", cfg=cfg)

    # changing x ancilla to computational basis for future measurement:
    append_1q(circuit, "H", x_ancilla, phase="ec", cfg=cfg)

    # In stim, the order of measurements in a single M command matters for rec targeting.
    # M x_ancilla, z_ancilla means x is rec(-2), z is rec(-1)
    append_1q(circuit, "M", x_ancilla, phase="ec", cfg=cfg)
    append_1q(circuit, "M", z_ancilla, phase="ec", cfg=cfg)


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
    Measures X and Z stabilizers for each of thx§e 4 columns.
    """
    _, x_ancilla, z_ancilla = get_qubits_and_ancillas()
    for col in measurement_operators_columns:
        measure_x_z_stabilizer(circuit, col, x_ancilla, z_ancilla, cfg=cfg)


def error_correct_manual(circuit, rounds=3, cfg: NoiseCfg = NO_NOISE):
    for i in range(rounds):
        error_correction_round_rows(circuit, cfg=cfg)
        error_correction_round_columns(circuit, cfg=cfg)
        circuit.append_operation("TICK")


def measure_logical_operators_for_8_3_2_color_code(circuit, participating_qubits: list[int], ancillas: list[int], measurement_basis: str,
                                                   cfg: NoiseCfg = NO_NOISE):
    """
    Measures the logical operators for the 8-3-2 color code.
    """

    if measurement_basis == "X":
        for q in participating_qubits:
            append_1q(circuit, "H", q, phase="meas", cfg=cfg)
    elif measurement_basis == "Z":
        pass
    else:
        raise ValueError(f"Invalid measurement basis: {measurement_basis}")
    
    for q in participating_qubits:
        append_1q(circuit, "M", q, phase="meas", cfg=cfg)

def measure_logical_operators_tesseract(circuit, cfg: NoiseCfg = NO_NOISE):
    """
    Measures the logical operators for the tesseract code.

    We implement the following: (cited from the paper):
    "Of course, transversal X and Z measurements, followed by classical decoding, can be used to destructively measure all of the logical X or Z operators fault tolerantly.
    Interestingly, there is also a simple procedure for measuring half the logical qubits in the X basis and half in the Z basis.
    For example, to measure Z, X, Z, X, Z, X, apply row-transversal CNOT gates from row 1 to row 4, and row 2 to row 3;
    then measure each qubit in the top half in the X basis, and each in the bottom in the Z basis.
    As shown in Fig. 5(b), the CNOT gates divide the logical qubits between two [[8, 3, 2]] color codes.
    Although these codes only have distance two, they have distance four in the direction that matters (Z distance four for the top half, X distance four for the bottom), so one can reliably decode the measurement results.
    We will use this measurement procedure in the repeated error correction experiments below."
    """
    
    # First we split the code into two parts, each is a block of the [[8,3,2]] color code.

    # Apply CNOTS between row 1 and 4
    for i in range(4):
        append_2q(circuit, "CNOT", i, i + 12, phase="meas", cfg=cfg)

    # Apply CNOTS between row 2 and 3
    for i in range(4):
        append_2q(circuit, "CNOT", i + 4, i + 8, phase="meas", cfg=cfg)

    # Measure the top half in the X basis
    measure_logical_operators_for_8_3_2_color_code(circuit, participating_qubits=[0, 1, 2, 3, 4, 5, 6, 7], ancillas=[16, 17], measurement_basis="X", cfg=cfg)

    # Measure the bottom half in the Z basis
    measure_logical_operators_for_8_3_2_color_code(circuit, participating_qubits=[8, 9, 10, 11, 12, 13, 14, 15], ancillas=[16, 17], measurement_basis="Z", cfg=cfg)

    circuit.append_operation("TICK")