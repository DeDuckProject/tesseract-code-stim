from typing_extensions import deprecated

import stim

# general circuit helper functions:
def append_stabilizer(circuit, pauli_type, targets):
    """Append a multi-qubit Pauli product measurement to the circuit."""
    pauli_targets = []
    for t in targets:
        if pauli_type == 'X':
            pauli_targets.append(stim.target_x(t))
        elif pauli_type == 'Z':
            pauli_targets.append(stim.target_z(t))
        # Add a combiner for each qubit except the last one
        pauli_targets.append(stim.target_combiner())

    # Remove the last combiner (no combiner after the final target)
    pauli_targets.pop()

    # Append the MPP operation with the constructed targets
    circuit.append("MPP", pauli_targets)
    circuit.append("TICK")


def append_detector(circuit, index1, index2):
    """Append a DETECTOR instruction with two recorded targets."""
    circuit.append("DETECTOR", [
        stim.target_rec(index1),
        stim.target_rec(index2)
    ])


# Tesseract code circuit parts:

#Code stabilizer definitions:
# X-type stabilizers
x_stabilizers = [
    [0, 1, 2, 3, 4, 5, 6, 7],
    [4, 5, 6, 7, 8, 9, 10, 11],
    [8, 9, 10, 11, 12, 13, 14, 15],
    [0, 1, 4, 5, 8, 9, 12, 13],
    [1, 2, 5, 6, 9, 10, 13, 14],
]

# Z-type stabilizers
z_stabilizers = [
    [0, 1, 2, 3, 4, 5, 6, 7],
    [4, 5, 6, 7, 8, 9, 10, 11],
    [8, 9, 10, 11, 12, 13, 14, 15],
    [0, 1, 4, 5, 8, 9, 12, 13],
    [1, 2, 5, 6, 9, 10, 13, 14],
]

#Tesseract code circuit creation functions:

## Trying to create circuit from tableau based on stabilizer generators
# In order to encode some codeword in the codespace, I've used this reference:
# https://quantumcomputing.stackexchange.com/questions/32437/a-simple-way-of-encoding-qubit-in-stabilizer-codes-with-stim
def init_circuit(qubits=16, ancillas=0):
    circuit = stim.Circuit()
    # Adding qubit coordinates metadata for qubits
    for qubit in range(qubits):
        x = qubit % 4
        y = qubit // 4
        circuit.append_operation("QUBIT_COORDS", [qubit], [x, y])
    
    # Adding qubit coordinates metadata for ancillas
    for ancilla in range(ancillas):
        circuit.append_operation("QUBIT_COORDS", [qubits + ancilla], [5, ancilla])

    circuit.append_operation("TICK")
    return circuit


@deprecated("Use encode_manual_fig9a or encode_manual_fig9b instead")
def encode(circuit):
    # Encoding step: Measuring X and Z stabilizers:

    # Append X-type stabilizers
    for targets in x_stabilizers:
        append_stabilizer(circuit, 'X', targets)

    # Append Z-type stabilizers
    for targets in z_stabilizers:
        append_stabilizer(circuit, 'Z', targets)

    # print("Encoding complete.")


def channel(circuit, error_rate, noisy_qubits=list(range(16)), noise_type="X_ERROR"):
    # Noise channel: Adding errors with some probability
    circuit.append("TICK")
    circuit.append(noise_type, noisy_qubits, error_rate)
    circuit.append("TICK")

@deprecated("Use error_correct_manual instead")
def error_correction(circuit):
    # Error correction: Measuring the stabilizers again

    # Append X-type stabilizers
    for targets in x_stabilizers:
        append_stabilizer(circuit, 'X', targets)

    # Append Z-type stabilizers
    for targets in z_stabilizers:
        append_stabilizer(circuit, 'Z', targets)

    # Adding detectors for error syndrome extraction
    # Append DETECTOR instructions to matching measurements
    for i in range(10):
        append_detector(circuit, index1=-(10 - i), index2=-(20 - i))

    # Logical observables and corresponding observable indices
    logical_observables = [
        (['Z', [0, 4, 8, 12]], 0),
        (['Z', [0, 1, 2, 3]], 1),
        (['Z', [0, 1, 4, 5]], 2),
        (['Z', [5, 6, 9, 10]], 3),
        (['Z', [4, 5, 8, 9]], 4),
        (['Z', [1, 2, 5, 6]], 5),
    ]

    # Append logical observables
    for (pauli_type, targets), observable_index in logical_observables:
        # Append the stabilizer measurement
        append_stabilizer(circuit, pauli_type, targets)

        # Inline the OBSERVABLE_INCLUDE operation
        circuit.append("OBSERVABLE_INCLUDE", [stim.target_rec(-1)], observable_index)

    # print("Error correction complete.")
