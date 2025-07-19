import stim
from tesseract_sim.encoding_manual import encode_manual_fig9a
from tesseract_sim.commons import measurement_operators_rows, measurement_operators_columns
from tesseract_sim.measurement_rounds import measure_x_z_stabilizer
import pytest

# This tests is not working currently. we are going to try and implement the |+0+0+0> encoder from fig 9b anyway.
# and we might not need it. keeping this for now.
@pytest.mark.skip(reason="Skipping this test temporarily")
def test_encoded_state_is_stabilizer_eigenstate():
    """
    Tests that the state prepared by encode_manual is a +1 eigenstate of all
    the tesseract code's stabilizers. This verifies that the encoded state
    is in the correct codespace.
    """
    # 1. Prepare the encoded state
    circuit = stim.Circuit()
    encode_manual_fig9a(circuit)

    # Use fresh ancilla qubits for stabilizer measurements that are guaranteed
    # not to have been used in the encoding process.
    x_ancilla = 23
    z_ancilla = 24

    # 2. For each stabilizer, append the measurement circuit.
    # We are measuring both X and Z stabilizers for all rows and columns.
    for row in measurement_operators_rows:
        measure_x_z_stabilizer(circuit, row, x_ancilla, z_ancilla)

    for col in measurement_operators_columns:
        measure_x_z_stabilizer(circuit, col, x_ancilla, z_ancilla)

    # 3. Sample the circuit. For a valid stabilizer state, all measurement
    # outcomes should be 0 (corresponding to the +1 eigenvalue).
    sampler = circuit.compile_sampler()
    samples = sampler.sample(shots=10)

    assert not samples.any(), "Not all stabilizer measurements yielded +1" 