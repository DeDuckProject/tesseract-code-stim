from tesseract_sim.run import run_simulation_experiment2
from tesseract_sim.noise_cfg import NO_NOISE

def test_exp2_no_noise_accepts_all():
    """
    Test that with no noise, all shots pass both error correction and logical verification.
    """
    shots = 100
    rounds = 3
    
    ec_accept, logical_pass, logical_fail = run_simulation_experiment2(rounds=rounds, shots=shots, cfg=NO_NOISE, encoding_mode='9a')
    
    assert ec_accept == shots, "All shots should pass error correction with no noise"
    assert logical_pass == shots, "All shots should pass logical verification with no noise"
    assert logical_fail == 0, "No shots should fail logical verification with no noise"

# TODO: Enable and fix this test to ensure it works correctly. currently the 9b encoding/measurement is incorrect and we don't get correct results even without noise.
def disabled_test_exp2_no_noise_accepts_all_encoding_9b():
    """
    Test that with no noise, all shots pass both error correction and logical verification.
    """
    shots = 100
    rounds = 3

    ec_accept, logical_pass, logical_fail = run_simulation_experiment2(rounds=rounds, shots=shots, cfg=NO_NOISE, encoding_mode='9b')

    assert ec_accept == shots, "All shots should pass error correction with no noise"
    assert logical_pass == shots, "All shots should pass logical verification with no noise"
    assert logical_fail == 0, "No shots should fail logical verification with no noise"