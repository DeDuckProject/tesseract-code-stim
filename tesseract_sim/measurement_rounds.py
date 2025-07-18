import stim
from .encoding_manual import measurement_operators_rows, measurement_operators_columns

def get_qubits_and_ancillas():
    """
    the two ancilla qubits are for the X and Z measurements, respectively.
    """
    return list(range(16)), 16, 17


def measure_x_z_stabilizer(circuit, data_qubits, x_ancilla, z_ancilla):
    """
    Appends a circuit to measure X and Z stabilizers on data_qubits.
    Based on Fig 4(d) of the paper.
    X stabilizer is measured on x_ancilla.
    Z stabilizer is measured on z_ancilla. The Z measurement also acts as a flag for the X measurement.
    """
    circuit.append("H", x_ancilla)
    for q in data_qubits:
        circuit.append("CNOT", [x_ancilla, q])
    for q in data_qubits:
        circuit.append("CNOT", [q, z_ancilla])
    circuit.append("H", x_ancilla)

    # In stim, the order of measurements in a single M command matters for rec targeting.
    # M x_ancilla, z_ancilla means x is rec(-2), z is rec(-1)
    circuit.append("M", [x_ancilla, z_ancilla])
    circuit.append("R", [x_ancilla, z_ancilla])


def error_correction_round_rows(circuit):
    """
    Appends one round of row-based stabilizer measurements to the circuit.
    Measures X and Z stabilizers for each of the 4 rows.
    """
    _, x_ancilla, z_ancilla = get_qubits_and_ancillas()
    for row in measurement_operators_rows:
        measure_x_z_stabilizer(circuit, row, x_ancilla, z_ancilla)


def error_correction_round_columns(circuit):
    """
    Appends one round of column-based stabilizer measurements to the circuit.
    Measures X and Z stabilizers for each of the 4 columns.
    """
    _, x_ancilla, z_ancilla = get_qubits_and_ancillas()
    for col in measurement_operators_columns:
        measure_x_z_stabilizer(circuit, col, x_ancilla, z_ancilla)


def error_correct_manual(circuit, rounds=3):
    for i in range(rounds):
        error_correction_round_rows(circuit)
        error_correction_round_columns(circuit) 