import pytest
from tesseract_sim.run import build_encoding_circuit, build_error_correction_circuit
from tesseract_sim.error_correction.decoder_manual import run_manual_error_correction
from tesseract_sim.noise.noise_cfg import NO_NOISE

# TODO these tests are not working correctly for 9b encoding/measurement. need to fix that with 9b and without the only_z_checks flag.

# All 16 data qubits in the tesseract code
DATA_QUBITS = list(range(16))
PAULI_GATES = ['X', 'Z', 'Y']


@pytest.mark.parametrize("qubit_index", DATA_QUBITS)
@pytest.mark.parametrize("pauli_gate", PAULI_GATES)
def test_single_pauli_error_correction(qubit_index, pauli_gate):
    """
    Test that a single Pauli error on any data qubit gets corrected by the error correction round.
    
    This test covers all combinations of:
    - 16 data qubits (0-15) 
    - 3 Pauli operators (X, Z, Y)
    
    For each combination, we verify that:
    1. The error correction round accepts the correction (ec_accept = 100%)
    2. The logical state is recovered after Pauli frame correction (logical_pass = 100%)
    3. No logical failures occur (logical_fail = 0%)
    """
    # Build encoding circuit with no noise
    circuit = build_encoding_circuit(NO_NOISE, '9a')
    
    # Inject the specified Pauli error on the specified qubit
    circuit.append(pauli_gate, [qubit_index])
    
    # Build error correction circuit
    build_error_correction_circuit(NO_NOISE, circuit, rounds=3)
    
    # Run simulation with 9a encoding mode (appropriate for |++0000>)
    ec_accept, logical_pass, average_percentage = run_manual_error_correction(
        circuit, shots=5, rounds=1, encoding_mode='9a'
    )
    
    # All shots should be accepted since single errors are correctable
    assert ec_accept == 5, (
        f"Expected all shots accepted for {pauli_gate} error on qubit {qubit_index}, "
        f"got {ec_accept}/5 accepted"
    )
    
    # All shots should pass logical check after Pauli frame correction
    assert logical_pass == 5, (
        f"Expected all shots to pass logical check for {pauli_gate} error on qubit {qubit_index}, "
        f"got {logical_pass}/5 passed"
    )
    
    # Average percentage should be 100% for perfect correction
    assert average_percentage == 1.0, (
        f"Expected 100% average success rate for {pauli_gate} error on qubit {qubit_index}, "
        f"got {average_percentage:.2%}"
    )


def test_no_noise_perfect_state():
    """Test that with no noise at all, we get perfect acceptance and logical pass rates."""
    # Build encoding circuit with no noise
    circuit = build_encoding_circuit(NO_NOISE, '9a')
    
    # Build error correction circuit (no injected errors)
    build_error_correction_circuit(NO_NOISE, circuit, rounds=1)
    
    # Run simulation with 9a encoding mode (appropriate for |++0000>)
    ec_accept, logical_pass, average_percentage = run_manual_error_correction(circuit, shots=100, rounds=1, encoding_mode='9a')
    
    # All shots should be accepted
    assert ec_accept == 100, f"Expected all shots accepted, got {ec_accept}"
    # All shots should pass logical check
    assert logical_pass == 100, f"Expected all shots to pass logical check, got {logical_pass}"
    assert average_percentage == 1.0, f"Expected 100% average success rate, got {average_percentage:.2%}"


# Legacy individual tests for backward compatibility and specific debugging
def test_single_x_error_correction():
    """Test that a single X error on a Z-basis measurement qubit gets corrected by the Pauli frame."""
    # Build encoding circuit with no noise
    circuit = build_encoding_circuit(NO_NOISE, '9a')
    
    # Inject a single X error on qubit 8 (first qubit measured in Z basis)
    circuit.append("X", [8])
    
    # Build error correction circuit
    build_error_correction_circuit(NO_NOISE, circuit, rounds=1)
    
    # Run simulation with 9a encoding mode (appropriate for |++0000>)
    ec_accept, logical_pass, average_percentage = run_manual_error_correction(circuit, shots=100, rounds=1, encoding_mode='9a')
    
    # All shots should be accepted since we only have a correctable error
    assert ec_accept == 100, f"Expected all shots accepted, got {ec_accept}"
    # All shots should pass logical check after Pauli frame correction
    assert logical_pass == 100, f"Expected all shots to pass logical check, got {logical_pass}"
    assert average_percentage == 1.0, f"Expected 100% average success rate, got {average_percentage:.2%}"


def test_single_z_error_correction():
    """Test that a single Z error on an X-basis measurement qubit gets corrected by the Pauli frame."""
    # Build encoding circuit with no noise
    circuit = build_encoding_circuit(NO_NOISE, '9a')
    
    # Inject a single Z error on qubit 0 (first qubit measured in X basis)
    circuit.append("Z", [0])
    
    # Build error correction circuit
    build_error_correction_circuit(NO_NOISE, circuit, rounds=1)
    
    # Run simulation with 9a encoding mode (appropriate for |++0000>)
    ec_accept, logical_pass, average_percentage = run_manual_error_correction(circuit, shots=100, rounds=1, encoding_mode='9a')
    
    # All shots should be accepted since we only have a correctable error
    assert ec_accept == 100, f"Expected all shots accepted, got {ec_accept}"
    # All shots should pass logical check after Pauli frame correction
    assert logical_pass == 100, f"Expected all shots to pass logical check, got {logical_pass}"
    assert average_percentage == 1.0, f"Expected 100% average success rate, got {average_percentage:.2%}" 