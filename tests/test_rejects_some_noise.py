from tesseract_sim import run_simulation

def test_rejects_some_noise():
    """
    Given some noise, the simulation should reject at least one shot.
    This is a probabilistic test, but with high enough noise and shots,
    it's virtually guaranteed to have rejections.
    """
    accept_count, reject_count = run_simulation(
        rounds=1,
        shots=1000,
        noise_level=0.1 
    )
    assert reject_count > 0 