from tesseract_sim import run_simulation_ec_experiment
from tesseract_sim.noise.noise_cfg import NoiseCfg

def test_rejects_some_noise():
    """
    Given some noise, the simulation should reject at least one shot.
    This is a probabilistic test, but with high enough noise and shots,
    it's virtually guaranteed to have rejections.
    """
    noise_config = NoiseCfg(ec_active=True, ec_rate_1q=0.01)
    ec_accept, logical_pass, average_percentage = run_simulation_ec_experiment(
        rounds=2,
        shots=1000,
        cfg=noise_config,
        apply_pauli_frame=False,  # Use False to match experiment1 behavior
        encoding_mode='9a'    # Use 9a to match experiment1 behavior
    )
    reject_count = 1000 - ec_accept
    assert reject_count > 0 