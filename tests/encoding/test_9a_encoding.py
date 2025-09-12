from tesseract_sim.run import build_circuit_ec_experiment
from tesseract_sim.error_correction.decoder_manual import run_manual_error_correction
from tesseract_sim.noise.noise_cfg import NO_NOISE

def test_9a_encoding_no_noise_perfect_state():
    """Test that 9a encoding (|++0000>) with only Z checks gives perfect results with no noise."""
    # Build circuit with 9a encoding and no noise
    circuit = build_circuit_ec_experiment(rounds=1, cfg=NO_NOISE, encoding_mode='9a')
    
    # Run simulation with 9a encoding mode (appropriate for 9a encoding)
    ec_accept, logical_pass, logical_fail = run_manual_error_correction(
        circuit, shots=100, rounds=1, encoding_mode='9a'
    )
    
    # All shots should be accepted
    assert ec_accept == 100, f"Expected all shots accepted, got {ec_accept}"
    # All shots should pass logical check (only Z3, Z5 are checked)
    assert logical_pass == 100, f"Expected all shots to pass logical check, got {logical_pass}"
    assert logical_fail == 0, f"Expected no logical failures, got {logical_fail}"

def test_9a_encoding_no_error_correction():
    """Test that 9a encoding works even without error correction rounds."""
    # Build circuit with 9a encoding and no error correction
    circuit = build_circuit_ec_experiment(rounds=0, cfg=NO_NOISE, encoding_mode='9a')
    
    # Run simulation with 9a encoding mode
    ec_accept, logical_pass, logical_fail = run_manual_error_correction(
        circuit, shots=100, rounds=0, encoding_mode='9a'
    )
    
    # All shots should be accepted
    assert ec_accept == 100, f"Expected all shots accepted, got {ec_accept}"
    # All shots should pass logical check
    assert logical_pass == 100, f"Expected all shots to pass logical check, got {logical_pass}"
    assert logical_fail == 0, f"Expected no logical failures, got {logical_fail}"

def test_9a_encoding_without_pauli_correction():
    """Test that 9a encoding works without Pauli frame correction."""
    # Build circuit with 9a encoding
    circuit = build_circuit_ec_experiment(rounds=1, cfg=NO_NOISE, encoding_mode='9a')
    
    # Run simulation without Pauli correction
    ec_accept, logical_pass, logical_fail = run_manual_error_correction(
        circuit, shots=100, rounds=1, apply_pauli_frame=False, encoding_mode='9a'
    )
    
    # All shots should be accepted
    assert ec_accept == 100, f"Expected all shots accepted, got {ec_accept}"
    # All shots should pass logical check
    assert logical_pass == 100, f"Expected all shots to pass logical check, got {logical_pass}"
    assert logical_fail == 0, f"Expected no logical failures, got {logical_fail}"

def test_9a_encoding_multiple_rounds():
    """Test that 9a encoding works with multiple error correction rounds."""
    # Build circuit with 9a encoding and multiple rounds
    circuit = build_circuit_ec_experiment(rounds=3, cfg=NO_NOISE, encoding_mode='9a')
    
    # Run simulation with 9a encoding mode
    ec_accept, logical_pass, logical_fail = run_manual_error_correction(
        circuit, shots=100, rounds=3, encoding_mode='9a'
    )
    
    # All shots should be accepted
    assert ec_accept == 100, f"Expected all shots accepted, got {ec_accept}"
    # All shots should pass logical check
    assert logical_pass == 100, f"Expected all shots to pass logical check, got {logical_pass}"
    assert logical_fail == 0, f"Expected no logical failures, got {logical_fail}"
