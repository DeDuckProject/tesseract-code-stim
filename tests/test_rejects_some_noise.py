from tesseract_sim import run_simulation
from tesseract_sim.noise_cfg import NoiseCfg

def test_rejects_some_noise():
    """
    Given some noise, the simulation should reject at least one shot.
    This is a probabilistic test, but with high enough noise and shots,
    it's virtually guaranteed to have rejections.
    """
    noise_config = NoiseCfg(ec_active=True, ec_rate_1q=0.01)
    accept_count, reject_count = run_simulation(
        rounds=2,
        shots=1000,
        cfg=noise_config
    )
    assert reject_count > 0 