import stim

measurement_operators_rows = [
    [0,1,2,3],
    [4,5,6,7],
    [8,9,10,11],
    [12,13,14,15]
]

measurement_operators_columns = [
    [0,4,8,12],
    [1,5,9,13],
    [2,6,10,14],
    [3,7,11,15]
]

def encode_sub_circuit_quad(circuit, ancilla, qubits):
    circuit.append("CNOT", [qubits[0], ancilla]) # Flag qubit
    circuit.append("CNOT", [qubits[0], qubits[1]])
    circuit.append("CNOT", [qubits[0], qubits[2]])
    circuit.append("CNOT", [qubits[0], qubits[3]])
    circuit.append("CNOT", [qubits[0], ancilla]) # Flag qubit

def add_cnot_gates(circuit, start1, start2, num_gates=4):
    """
    Adds CNOT gates to the circuit.

    Parameters:
    - circuit: The quantum circuit object to modify.
    - start1: The starting index for the first qubit in the CNOT pairs.
    - start2: The starting index for the second qubit in the CNOT pairs.
    - num_gates: The number of CNOT gates to append (default is 4).
    """
    for i in range(num_gates):
        circuit.append("CNOT", [start1 + i, start2 + i])

def encode_manual(circuit):
    # Here we encode the state |++0000> as can be seen in Fig. 9 of that paper
    # initialize qubits:
    circuit.append("H", [0,1,2,3,4,8,12])

    encode_sub_circuit_quad(circuit, 20, [4, 5, 6, 7])
    encode_sub_circuit_quad(circuit, 21, [8, 9, 10, 11])
    encode_sub_circuit_quad(circuit, 22, [12, 13, 14, 15])

    add_cnot_gates(circuit, 0, 16) # working on ancilla qubits as flag qubits
    add_cnot_gates(circuit, 0, 4)
    add_cnot_gates(circuit, 0, 8)
    add_cnot_gates(circuit, 0, 12)
    add_cnot_gates(circuit, 0, 16) # working on ancilla qubits as flag qubits

    circuit.append("R", [18, 19]) # Reset ancillas 18,19 since their role is done and we need them for the following
    circuit.append("H", [19])
    circuit.append("CNOT", [19, 18]) # cnot to flag qubit
    circuit.append("CNOT", [19, 0]) # measuring stabilizer
    circuit.append("CNOT", [19, 1]) # measuring stabilizer
    circuit.append("CNOT", [19, 2]) # measuring stabilizer
    circuit.append("CNOT", [19, 3]) # measuring stabilizer
    circuit.append("CNOT", [19, 18]) # cnot to flag qubit 