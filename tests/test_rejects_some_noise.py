from tesseract_sim import run_simulation_experiment2
from tesseract_sim.noise_cfg import NoiseCfg

def test_rejects_some_noise():
    """
    Given some noise, the simulation should reject at least one shot.
    This is a probabilistic test, but with high enough noise and shots,
    it's virtually guaranteed to have rejections.
    """
    noise_config = NoiseCfg(ec_active=True, ec_rate_1q=0.01)
    ec_accept, logical_pass, logical_fail = run_simulation_experiment2(
        rounds=2,
        shots=1000,
        cfg=noise_config,
        correct_pauli=False,  # Use False to match experiment1 behavior
        encoding_mode='9a'    # Use 9a to match experiment1 behavior
    )
    reject_count = 1000 - ec_accept
    assert reject_count > 0 