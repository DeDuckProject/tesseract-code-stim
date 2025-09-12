import numpy as np
import matplotlib.pyplot as plt
from tesseract_sim.run import run_simulation_ec_experiment
from tesseract_sim.noise.noise_cfg import NoiseCfg
import os
from typing import Callable, Dict, List, TypeVar, Tuple, Literal
import argparse

T = TypeVar('T')  # Type of experiment result

def sweep_results(
    experiment_fn: Callable[[int, int, NoiseCfg], T],
    rounds: List[int],
    noise_levels: List[float],
    shots: int,
    cfg_builder: Callable[[float], NoiseCfg],
    apply_pauli_frame: bool = True,
    encoding_mode: Literal['9a', '9b'] = '9b'
) -> Dict[float, List[T]]:
    """
    Sweeps over rounds and noise levels, collecting full experiment results.

    Args:
        experiment_fn: Function that runs an experiment (returns tuple)
        rounds: List of round counts to sweep
        noise_levels: List of noise levels to sweep
        shots: Number of shots per data point
        cfg_builder: Function that creates a NoiseCfg from a noise level

    Returns:
        Dictionary mapping noise levels to lists of result tuples (one per round)
    """
    results: Dict[float, List[Tuple[int, int, int]]] = {}

    for noise in noise_levels:
        noise_config = cfg_builder(noise)
        tuples = []

        for r in rounds:
            print(f"Processing rounds={r}, noise={noise}")
            result = experiment_fn(rounds=r, shots=shots, cfg=noise_config, apply_pauli_frame=apply_pauli_frame, encoding_mode=encoding_mode)
            tuples.append(result)

        results[noise] = tuples

    return results

def plot_curve(
    rounds: List[int],
    data: Dict[float, List[float]],
    title: str,
    ylabel: str,
    out_path: str
) -> None:
    """Plots and saves a single curve from sweep data."""
    plt.figure(figsize=(12, 8))
    
    for noise, rates in data.items():
        plt.plot(rounds, rates, marker='o', label=f'EC Noise Rate={noise:.4f}')
    
    plt.xlabel('Number of Rounds')
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True)
    plt.legend()
    
    plt.savefig(out_path)
    print(f"Plot saved to {out_path}")
    plt.close()


def plot_ec_experiment(
    rounds: List[int],
    noise_levels: List[float],
    shots: int,
    out_dir: str,
    apply_pauli_frame: bool = True,
    encoding_mode: Literal['9a', '9b'] = '9b',
    sweep_channel_noise: bool = False
) -> None:
    """Plots both EC acceptance and logical check rates for the EC experiment."""
    # One sweep collecting full results
    if sweep_channel_noise:
        cfg_builder = lambda noise: NoiseCfg(ec_active=False, channel_noise_level=noise, channel_noise_type="DEPOLARIZE1")
    else:
        cfg_builder = lambda noise: NoiseCfg(ec_active=True, ec_rate_1q=noise, ec_rate_2q=noise, channel_noise_level=0.0)
    
    raw_results = sweep_results(
        run_simulation_ec_experiment,
        rounds, noise_levels, shots,
        cfg_builder,
        apply_pauli_frame=apply_pauli_frame,
        encoding_mode=encoding_mode
    )

    # Derive EC acceptance rate from raw results
    ec_data = {
        noise: [t[0]/shots for t in tuples]  # ec_accept/shots
        for noise, tuples in raw_results.items()
    }

    noise_type = "Channel" if sweep_channel_noise else "EC"
    plot_curve(
        rounds, ec_data,
        title=f"{noise_type} Acceptance vs Rounds (EC Experiment)",
        ylabel="EC Acceptance Rate",
        out_path=os.path.join(out_dir, f'acceptance_rates_{"channel" if sweep_channel_noise else "ec"}_noise_ec_experiment.png')
    )

    # Derive logical check rate from same raw results - normalized by acceptance
    logical_data = {
        noise: [
            t[1]/t[0] if t[0] > 0 else 0.0  # logical_pass/accepted (conditional probability)
            for t in tuples
        ]
        for noise, tuples in raw_results.items()
    }

    plot_curve(
        rounds, logical_data,
        title=f"Logical Check Success vs Rounds (EC Experiment) - {noise_type} Noise",
        ylabel="Logical Success Rate | Accepted",
        out_path=os.path.join(out_dir, f'logical_rates_{"channel" if sweep_channel_noise else "ec"}_noise_ec_experiment.png')
    )

def main():
    parser = argparse.ArgumentParser(description="Generate acceptance rate plots for tesseract experiments")
    parser.add_argument('--experiments', type=int, nargs='+', choices=[2], default=[2],
                      help='Which experiments to plot (currently only 2 is supported)')
    parser.add_argument('--shots', type=int, default=10000,
                      help='Number of shots per data point')
    parser.add_argument('--out-dir', type=str, default='../plots',
                      help='Output directory for plots')
    parser.add_argument('--apply_pauli_frame', type=bool, default=False, help='Perform final correction - apply the measured Pauli frame. The error correction rounds and measurements (besides the actual correction at the end) happen regardless, based on the number of rounds.')
    parser.add_argument('--encoding-mode', type=str, choices=['9a', '9b'], default='9a', help='Encoding mode')
    parser.add_argument('--sweep-channel-noise', action='store_true', help='Sweep channel noise instead of EC noise. Channel noise acts once after encoding and before the error correction rounds.')
    args = parser.parse_args()

    # Combine detailed lower rounds with higher rounds
    rounds = list(range(1, 11)) + [20, 30, 40, 50]
    noise_levels = np.linspace(0.0000, 0.01, 30)  # 30 points between 0 and 1%
    
    os.makedirs(args.out_dir, exist_ok=True)

    print(args.experiments)
    if 2 in args.experiments:
        plot_ec_experiment(rounds, noise_levels, args.shots, args.out_dir, args.apply_pauli_frame, args.encoding_mode, args.sweep_channel_noise)

if __name__ == "__main__":
    main() 