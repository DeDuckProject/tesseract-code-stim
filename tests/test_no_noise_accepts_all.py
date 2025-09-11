from tesseract_sim import run_simulation_ec_experiment
from tesseract_sim.noise.noise_cfg import NO_NOISE

def test_no_noise_accepts_all():
    """
    Given no noise, the simulation should accept all shots.
    """
    ec_accept, logical_pass, logical_fail = run_simulation_ec_experiment(
        rounds=1, 
        shots=100, 
        cfg=NO_NOISE,
        apply_pauli_frame=False,  # Use False to match experiment1 behavior
        encoding_mode='9a'    # Use 9a to match experiment1 behavior
    )
    assert ec_accept == 100
    # With no noise, all accepted shots should pass logical checks
    assert logical_pass == 100
    assert logical_fail == 0 