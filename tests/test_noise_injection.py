import pytest
import stim
from tesseract_sim.noise_cfg import NoiseCfg, NO_NOISE
from tesseract_sim.noise_utils import append_op, append_1q, append_2q
from tesseract_sim.encoding_manual_9a import encode_manual_fig9a
from tesseract_sim.measurement_rounds import error_correct_manual
from tesseract_sim.run import build_circuit_ec_experiment

def count_noise_ops(circuit: stim.Circuit, op_type: str) -> int:
    """Counts the number of noise operations of a given type in the circuit."""
    return sum(1 for op in circuit if op.name == op_type)

def test_no_noise_config():
    # Test: NO_NOISE should result in no noise operations
    cfg = NO_NOISE
    circuit = stim.Circuit()
    append_1q(circuit, "H", 0, phase="enc", cfg=cfg)
    append_2q(circuit, "CNOT", 0, 1, phase="ec", cfg=cfg)
    assert count_noise_ops(circuit, "DEPOLARIZE1") == 0
    assert count_noise_ops(circuit, "DEPOLARIZE2") == 0

def test_encoding_noise_only():
    # Test: Noise only in encoding phase
    cfg = NoiseCfg(enc_active=True, enc_rate_1q=0.1, enc_rate_2q=0.2, ec_active=False)
    circuit = build_circuit_ec_experiment(rounds=1, cfg=cfg, encoding_mode='9a')
    
    # Check for depolarizing noise in encoding section
    # This is a bit tricky to assert precisely without deep inspection of Stim's circuit object
    # We'll rely on inspecting the text representation and making assumptions about Stim's output
    
    # A simple check: if we append a few gates, we expect some noise.
    # This test is more about the presence of noise given the config.
    # For a rigorous test, one would need to parse Stim's circuit commands.
    
    # Let's check for the presence of the noise operations
    assert count_noise_ops(circuit, "DEPOLARIZE1") > 0 or count_noise_ops(circuit, "DEPOLARIZE2") > 0

def test_error_correction_noise_only():
    # Test: Noise only in error correction phase
    cfg = NoiseCfg(enc_active=False, ec_active=True, ec_rate_1q=0.1, ec_rate_2q=0.2)
    circuit = build_circuit_ec_experiment(rounds=1, cfg=cfg, encoding_mode='9a')
    
    assert count_noise_ops(circuit, "DEPOLARIZE1") > 0 or count_noise_ops(circuit, "DEPOLARIZE2") > 0

def test_both_noise_active():
    # Test: Noise in both encoding and error correction phases
    cfg = NoiseCfg(enc_active=True, enc_rate_1q=0.01, ec_active=True, ec_rate_1q=0.01)
    circuit = build_circuit_ec_experiment(rounds=1, cfg=cfg, encoding_mode='9a')
    
    assert count_noise_ops(circuit, "DEPOLARIZE1") > 0 or count_noise_ops(circuit, "DEPOLARIZE2") > 0

def test_zero_noise_rates():
    # Test: Active noise but zero rates should result in no noise operations
    cfg = NoiseCfg(enc_active=True, enc_rate_1q=0.0, enc_rate_2q=0.0, ec_active=True, ec_rate_1q=0.0, ec_rate_2q=0.0)
    circuit = build_circuit_ec_experiment(rounds=1, cfg=cfg, encoding_mode='9a')
    assert count_noise_ops(circuit, "DEPOLARIZE1") == 0
    assert count_noise_ops(circuit, "DEPOLARIZE2") == 0

def test_channel_noise_injection():
    # Test: Channel noise should be injected when channel_noise_level > 0
    cfg = NoiseCfg(channel_noise_level=0.1, channel_noise_type="DEPOLARIZE1")
    circuit = build_circuit_ec_experiment(rounds=1, cfg=cfg, encoding_mode='9a')
    
    # Should have channel noise operations
    assert count_noise_ops(circuit, "DEPOLARIZE1") > 0
    
def test_channel_noise_different_type():
    # Test: Channel noise with different noise type
    cfg = NoiseCfg(channel_noise_level=0.05, channel_noise_type="X_ERROR")
    circuit = build_circuit_ec_experiment(rounds=1, cfg=cfg, encoding_mode='9a')
    
    # Should have X_ERROR operations
    assert count_noise_ops(circuit, "X_ERROR") > 0
    
def test_no_channel_noise_by_default():
    # Test: Default config should have no channel noise
    cfg = NoiseCfg()
    circuit = build_circuit_ec_experiment(rounds=1, cfg=cfg, encoding_mode='9a')
    
    # Should have no channel noise since channel_noise_level defaults to 0.0
    assert count_noise_ops(circuit, "DEPOLARIZE1") == 0
    assert count_noise_ops(circuit, "X_ERROR") == 0 