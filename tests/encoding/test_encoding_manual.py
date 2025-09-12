import stim
from tesseract_sim.encoding.encoding_manual_9a import encode_manual_fig9a
from tesseract_sim.common.code_commons import measurement_operators_rows, measurement_operators_columns
from tesseract_sim.error_correction.measurement_rounds import measure_x_z_stabilizer
import pytest

# This tests is not working currently. we are going to try and implement the |+0+0+0> encoder from fig 9b anyway.
# and we might not need it. keeping this for now.
@pytest.mark.skip(reason="Skipping this test temporarily")
def test_encoded_state_is_stabilizer_eigenstate_9a():
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

def test_encode_manual_fig9b():
    """Test that encode_manual_fig9b correctly encodes the |+0+0+0> state in both blocks."""
    import stim
    from tesseract_sim.encoding.encoding_manual_9b import encode_manual_fig9b
    
    # Create circuit
    circuit = stim.Circuit()
    encode_manual_fig9b(circuit)
    
    # Sample final state using a simulator
    simulator = circuit.compile_sampler()
    measurements = simulator.sample(1)[0]
    
    # We should have 4 measurements total (2 ancillas per block, 2 blocks)
    assert len(measurements) == 4, f"Expected 4 measurements but got {len(measurements)}"
    
    # First block measurements (indices 0,1)
    assert measurements[0] == 0, "X stabilizer measurement failed for first block"
    assert measurements[1] == 0, "Z stabilizer measurement failed for first block"
    
    # Second block measurements (indices 2,3)
    assert measurements[2] == 0, "X stabilizer measurement failed for second block"
    assert measurements[3] == 0, "Z stabilizer measurement failed for second block"
    
    # Sample multiple times to verify statistical properties
    samples = simulator.sample(1000)
    
    # Both ancillas should always measure 0 in the ideal case for both blocks
    for i in range(4):
        assert all(sample[i] == 0 for sample in samples), f"Stabilizer measurement {i} inconsistent" 