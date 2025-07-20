from tesseract_sim import run_simulation_experiment1
from tesseract_sim.noise_cfg import NO_NOISE

def test_no_noise_accepts_all():
    """
    Given no noise, the simulation should accept all shots.
    """
    accept_count, reject_count = run_simulation_experiment1(
        rounds=1, 
        shots=100, 
        cfg=NO_NOISE
    )
    assert reject_count == 0
    assert accept_count == 100 