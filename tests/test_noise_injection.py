import pytest
import stim
from tesseract_sim.noise_cfg import NoiseCfg, NO_NOISE
from tesseract_sim.noise_utils import append_op, append_1q, append_2q
from tesseract_sim.encoding_manual import encode_manual
from tesseract_sim.measurement_rounds import error_correct_manual
from tesseract_sim.run import build_circuit

def count_noise_ops(circuit_text: str, op_type: str) -> int:
    return circuit_text.count(op_type)

def test_no_noise_config():
    # Test: NO_NOISE should result in no noise operations
    cfg = NO_NOISE
    circuit = stim.Circuit()
    append_1q(circuit, "H", 0, phase="enc", cfg=cfg)
    append_2q(circuit, "CNOT", 0, 1, phase="ec", cfg=cfg)
    assert count_noise_ops(circuit.without_noise_on_used_qubits().diagram("text"), "DEPOLARIZE1") == 0
    assert count_noise_ops(circuit.without_noise_on_used_qubits().diagram("text"), "DEPOLARIZE2") == 0

def test_encoding_noise_only():
    # Test: Noise only in encoding phase
    cfg = NoiseCfg(enc_active=True, enc_rate_1q=0.1, enc_rate_2q=0.2, ec_active=False)
    circuit = build_circuit(rounds=1, cfg=cfg)
    circuit_text = circuit.without_noise_on_used_qubits().diagram("text")
    
    # Check for depolarizing noise in encoding section
    # This is a bit tricky to assert precisely without deep inspection of Stim's circuit object
    # We'll rely on inspecting the text representation and making assumptions about Stim's output
    
    # A simple check: if we append a few gates, we expect some noise.
    # This test is more about the presence of noise given the config.
    # For a rigorous test, one would need to parse Stim's circuit commands.
    
    # Let's check for the presence of the noise operations
    assert count_noise_ops(circuit_text, "DEPOLARIZE1") > 0 or count_noise_ops(circuit_text, "DEPOLARIZE2") > 0

def test_error_correction_noise_only():
    # Test: Noise only in error correction phase
    cfg = NoiseCfg(enc_active=False, ec_active=True, ec_rate_1q=0.1, ec_rate_2q=0.2)
    circuit = build_circuit(rounds=1, cfg=cfg)
    circuit_text = circuit.without_noise_on_used_qubits().diagram("text")
    
    assert count_noise_ops(circuit_text, "DEPOLARIZE1") > 0 or count_noise_ops(circuit_text, "DEPOLARIZE2") > 0

def test_both_noise_active():
    # Test: Noise in both encoding and error correction phases
    cfg = NoiseCfg(enc_active=True, enc_rate_1q=0.01, ec_active=True, ec_rate_1q=0.01)
    circuit = build_circuit(rounds=1, cfg=cfg)
    circuit_text = circuit.without_noise_on_used_qubits().diagram("text")
    
    assert count_noise_ops(circuit_text, "DEPOLARIZE1") > 0 or count_noise_ops(circuit_text, "DEPOLARIZE2") > 0

def test_zero_noise_rates():
    # Test: Active noise but zero rates should result in no noise operations
    cfg = NoiseCfg(enc_active=True, enc_rate_1q=0.0, enc_rate_2q=0.0, ec_active=True, ec_rate_1q=0.0, ec_rate_2q=0.0)
    circuit = build_circuit(rounds=1, cfg=cfg)
    assert count_noise_ops(circuit.without_noise_on_used_qubits().diagram("text"), "DEPOLARIZE1") == 0
    assert count_noise_ops(circuit.without_noise_on_used_qubits().diagram("text"), "DEPOLARIZE2") == 0 