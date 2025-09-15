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


# TODO this test should pass. running many rounds with noise should converge to a completely mixed state (verify), which would yield fidelity=0.5 or 50% logical similarity
def disabled_test_ec_experiment_noise_converges_to_half():
    """
    Test that with many rounds and shots, the average percentage converges to around 0.5.
    This tests the statistical expectation that roughly half the shots should pass.
    """
    shots = 100
    rounds = 10
    
    # Configure moderate noise during error correction
    cfg = NoiseCfg(
        ec_active=True,
        ec_rate_1q=0.002,  # 0.2% error rate on 1-qubit gates
        ec_rate_2q=0.004   # 0.4% error rate on 2-qubit gates
    )
    
    ec_accept, logical_pass, average_percentage = run_simulation_ec_experiment(
        rounds=rounds, shots=shots, cfg=cfg, encoding_mode='9a'
    )

    print("average_percentage", average_percentage)
    # With many shots and rounds, average should converge to around 0.5
    # Allow for statistical variation with a reasonable tolerance
    assert 0.4 <= average_percentage <= 0.6, f"Average percentage {average_percentage} should be close to 0.5 with many shots"
    assert logical_pass > 0, "Some shots should pass logical verification"
    assert logical_pass < shots, "Not all shots should pass with noise" 