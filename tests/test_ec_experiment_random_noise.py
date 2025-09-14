from tesseract_sim.run import run_simulation_ec_experiment
from tesseract_sim.noise.noise_cfg import NoiseCfg

def test_ec_experiment_noise_rejects_some():
    """
    Test that with noise, some shots fail either error correction or logical verification.
    """
    shots = 100
    rounds = 3
    
    # Configure noise during error correction
    cfg = NoiseCfg(
        ec_active=True,
        ec_rate_1q=0.01,  # 1% error rate on 1-qubit gates
        ec_rate_2q=0.02   # 2% error rate on 2-qubit gates
    )
    
    ec_accept, logical_pass, average_percentage = run_simulation_ec_experiment(rounds=rounds, shots=shots, cfg=cfg, encoding_mode='9a')
    
    # With noise, we expect some shots to fail, but not all
    assert 0 < logical_pass < shots, "Some shots should pass with noise, but not all"
    assert average_percentage < 1.0, "Average percentage should be less than 100% with noise"
    assert ec_accept > logical_pass, "Some shots that pass EC should fail logical verification" 