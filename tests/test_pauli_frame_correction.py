import stim
import numpy as np
from tesseract_sim.run import build_circuit_experiment2
from tesseract_sim.decoder_manual import run_manual_error_correction_exp2
from tesseract_sim.noise_cfg import NO_NOISE

def test_single_x_error_correction():
    """Test that a single X error on a Z-basis measurement qubit gets corrected by the Pauli frame."""
    # Build circuit with no noise during encoding/EC
    circuit = build_circuit_experiment2(rounds=1, cfg=NO_NOISE)
    
    # Inject a single X error on qubit 8 (first qubit measured in Z basis)
    circuit.append("X", [8])
    
    # Run simulation
    ec_accept, logical_pass, logical_fail = run_manual_error_correction_exp2(circuit, shots=100, rounds=1)
    
    # All shots should be accepted since we only have a correctable error
    assert ec_accept == 100, f"Expected all shots accepted, got {ec_accept}"
    # All shots should pass logical check after Pauli frame correction
    assert logical_pass == 100, f"Expected all shots to pass logical check, got {logical_pass}"
    assert logical_fail == 0, f"Expected no logical failures, got {logical_fail}"

def test_single_z_error_correction():
    """Test that a single Z error on an X-basis measurement qubit gets corrected by the Pauli frame."""
    # Build circuit with no noise during encoding/EC
    circuit = build_circuit_experiment2(rounds=1, cfg=NO_NOISE)
    
    # Inject a single Z error on qubit 0 (first qubit measured in X basis)
    circuit.append("Z", [0])
    
    # Run simulation
    ec_accept, logical_pass, logical_fail = run_manual_error_correction_exp2(circuit, shots=100, rounds=1)
    
    # All shots should be accepted since we only have a correctable error
    assert ec_accept == 100, f"Expected all shots accepted, got {ec_accept}"
    # All shots should pass logical check after Pauli frame correction
    assert logical_pass == 100, f"Expected all shots to pass logical check, got {logical_pass}"
    assert logical_fail == 0, f"Expected no logical failures, got {logical_fail}"

def test_no_noise_perfect_state():
    """Test that with no noise at all, we get perfect acceptance and logical pass rates."""
    # Build circuit with no noise and no injected errors
    circuit = build_circuit_experiment2(rounds=1, cfg=NO_NOISE)
    
    # Run simulation
    ec_accept, logical_pass, logical_fail = run_manual_error_correction_exp2(circuit, shots=100, rounds=1)
    
    # All shots should be accepted
    assert ec_accept == 100, f"Expected all shots accepted, got {ec_accept}"
    # All shots should pass logical check
    assert logical_pass == 100, f"Expected all shots to pass logical check, got {logical_pass}"
    assert logical_fail == 0, f"Expected no logical failures, got {logical_fail}" 