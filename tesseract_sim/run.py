import argparse

from tesseract_sim.encoding.encoding_manual_9b import encode_manual_fig9b
from tesseract_sim.common.circuit_base import init_circuit, channel
from tesseract_sim.encoding.encoding_manual_9a import encode_manual_fig9a
from typing import Literal
from tesseract_sim.error_correction.measurement_rounds import error_correct_manual, measure_logical_operators_tesseract
from tesseract_sim.error_correction.decoder_manual import run_manual_error_correction
from tesseract_sim.noise.noise_cfg import NoiseCfg, NO_NOISE


def build_circuit_ec_experiment(rounds: int, cfg: NoiseCfg = NO_NOISE, encoding_mode: Literal['9a', '9b'] = '9b'):
    # Here we can use either Fig 9a encoding (|++0000>) or Fig 9b encoding (|+0+0+0>)
    # depending on the encoding_mode parameter.

    circuit = build_encoding_circuit(cfg, encoding_mode)
    # -----------------------------

    if cfg.channel_noise_level > 0:
        # Now, apply noise to the encoded state
        channel(circuit, cfg.channel_noise_level, noise_type=cfg.channel_noise_type)

    build_error_correction_circuit(cfg, circuit, rounds)

    return circuit


def build_error_correction_circuit(cfg, circuit, rounds):
    # Append the error correction rounds to the circuit
    error_correct_manual(circuit, rounds=rounds, cfg=cfg)
    measure_logical_operators_tesseract(circuit, cfg=cfg)


def build_encoding_circuit(cfg, encoding_mode):
    # We start with a fresh circuit
    circuit = init_circuit(qubits=16, ancillas=2)
    # First, prepare a valid encoded state based on encoding mode
    if encoding_mode == '9a':
        encode_manual_fig9a(circuit, cfg=cfg)
    elif encoding_mode == '9b':
        encode_manual_fig9b(circuit, cfg=cfg)
    else:
        raise ValueError(f"Invalid encoding_mode: {encoding_mode}. Must be '9a' or '9b'")
    return circuit


def run_simulation_ec_experiment(rounds: int, shots: int, cfg: NoiseCfg = NO_NOISE, apply_pauli_frame = True, encoding_mode: Literal['9a', '9b'] = '9b'):
    circuit = build_circuit_ec_experiment(rounds, cfg, encoding_mode=encoding_mode)

    print(f"--- Running Manual Error Correction Simulation (with Logical Check) ---")
    print(f"Rounds: {rounds}, Shots: {shots}, Encoding: Fig {encoding_mode}")
    
    return run_manual_error_correction(circuit, shots=shots, rounds=rounds, apply_pauli_frame=apply_pauli_frame, encoding_mode=encoding_mode)


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
    parser.add_argument("--channel-noise-level", type=float, default=0.0, help="Channel noise level between encoding and error correction.")
    parser.add_argument("--channel-noise-type", type=str, default="DEPOLARIZE1", help="Channel noise type (e.g., DEPOLARIZE1, X_ERROR, Z_ERROR).")
    parser.add_argument("--experiment", type=int, choices=[1], default=1, help="Which experiment to run (only 1 available)")
    parser.add_argument("--no-apply-pauli-frame", action="store_false", dest="apply_pauli_frame", help="Disable Pauli frame corrections during logical verification")
    parser.add_argument("--encoding-mode", type=str, choices=['9a', '9b'], default='9b', help="Encoding mode, based on Fig 9a or 9b in the paper")
    
    args = parser.parse_args()

    # Create NoiseCfg from command line arguments
    sim_cfg = NoiseCfg(
        enc_active=args.enc_active,
        enc_rate_1q=args.enc_rate_1q,
        enc_rate_2q=args.enc_rate_2q,
        ec_active=args.ec_active,
        ec_rate_1q=args.ec_rate_1q,
        ec_rate_2q=args.ec_rate_2q,
        channel_noise_level=args.channel_noise_level,
        channel_noise_type=args.channel_noise_type
    )


    run_simulation_ec_experiment(rounds=args.rounds, shots=args.shots, cfg=sim_cfg, apply_pauli_frame=args.apply_pauli_frame, encoding_mode=args.encoding_mode)