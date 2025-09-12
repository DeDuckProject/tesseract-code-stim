import stim
from typing_extensions import deprecated

from tesseract_sim.common.circuit_base import append_stabilizer, append_detector

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


@deprecated("Use encode_manual_fig9a or encode_manual_fig9b instead")
def encode_deprecated(circuit):
    # Encoding step: Measuring X and Z stabilizers:

    # Append X-type stabilizers
    for targets in x_stabilizers:
        append_stabilizer(circuit, 'X', targets)

    # Append Z-type stabilizers
    for targets in z_stabilizers:
        append_stabilizer(circuit, 'Z', targets)

    # print("Encoding complete.")
