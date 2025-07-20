import argparse
from .circuit_base import init_circuit, channel
from .encoding_manual_9a import encode_manual_fig9a
from .measurement_rounds import error_correct_manual
from .decoder_manual import run_manual_error_correction
from .noise_cfg import NoiseCfg, NO_NOISE

def build_circuit(rounds: int, cfg: NoiseCfg = NO_NOISE, channel_noise_level=0, channel_noise_type="DEPOLARIZE1"):
    # We start with a fresh circuit from your helper function 16 qubits for code + 2 ancillas for measurement
    circuit = init_circuit(qubits=16, ancillas=2)

    # First, prepare a valid encoded state
    encode_manual_fig9a(circuit, cfg=cfg)
    # -----------------------------

    if (channel_noise_level > 0):
        # Now, apply noise to the encoded state
        channel(circuit, channel_noise_level, noise_type=channel_noise_type)

    # Append the error correction rounds to the circuit
    error_correct_manual(circuit, rounds=rounds, cfg=cfg)
    
    return circuit

def run_simulation(rounds: int, shots: int, cfg: NoiseCfg = NO_NOISE):
    circuit = build_circuit(rounds, cfg)
    
    print(f"--- Running Manual Error Correction Simulation (Corrected) ---")
    print(f"Rounds: {rounds}, Shots: {shots}")
    
    return run_manual_error_correction(circuit, shots=shots, rounds=rounds)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run tesseract code simulation with configurable noise.")
    parser.add_argument("--rounds", type=int, default=3, help="Number of error correction rounds.")
    parser.add_argument("--shots", type=int, default=1000, help="Number of simulation shots.")
    parser.add_argument("--enc-active", action="store_true", help="Activate noise during encoding.")
    parser.add_argument("--enc-rate-1q", type=float, default=0.0, help="1-qubit noise rate for encoding.")
    parser.add_argument("--enc-rate-2q", type=float, default=0.0, help="2-qubit noise rate for encoding.")
    parser.add_argument("--ec-active", action="store_true", help="Activate noise during error correction rounds.")
    parser.add_argument("--ec-rate-1q", type=float, default=0.0, help="1-qubit noise rate for error correction.")
    parser.add_argument("--ec-rate-2q", type=float, default=0.0, help="2-qubit noise rate for error correction.")

    args = parser.parse_args()

    # Create NoiseCfg from command line arguments
    sim_cfg = NoiseCfg(
        enc_active=args.enc_active,
        enc_rate_1q=args.enc_rate_1q,
        enc_rate_2q=args.enc_rate_2q,
        ec_active=args.ec_active,
        ec_rate_1q=args.ec_rate_1q,
        ec_rate_2q=args.ec_rate_2q
    )

    run_simulation(rounds=args.rounds, shots=args.shots, cfg=sim_cfg)