import numpy as np
import matplotlib.pyplot as plt
from tesseract_sim.run import run_simulation_experiment1, run_simulation_experiment2
from tesseract_sim.noise_cfg import NoiseCfg
import os
from typing import Callable, Dict, List, Any, TypeVar, Tuple, Literal
import argparse

T = TypeVar('T')  # Type of experiment result

def sweep_results(
    experiment_fn: Callable[[int, int, NoiseCfg], T],
    rounds: List[int],
    noise_levels: List[float],
    shots: int,
    cfg_builder: Callable[[float], NoiseCfg],
    correct_pauli: bool = True,
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
            result = experiment_fn(rounds=r, shots=shots, cfg=noise_config, correct_pauli=correct_pauli, encoding_mode=encoding_mode)
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

def plot_experiment1(
    rounds: List[int],
    noise_levels: List[float],
    shots: int,
    out_dir: str,
    correct_pauli: bool = True
) -> None:
    """Plots acceptance rates for experiment 1."""
    # One sweep collecting full results
    raw_results = sweep_results(
        run_simulation_experiment1,
        rounds, noise_levels, shots,
        lambda noise: NoiseCfg(ec_active=True, ec_rate_1q=noise, ec_rate_2q=noise, channel_noise_level=0.0),
        correct_pauli=correct_pauli
    )

    # Derive acceptance rate from raw results
    data = {
        noise: [t[0]/shots for t in tuples]  # accept_count/shots
        for noise, tuples in raw_results.items()
    }

    plot_curve(
        rounds, data,
        title="EC Acceptance vs Rounds (Experiment 1)",
        ylabel="Acceptance Rate",
        out_path=os.path.join(out_dir, 'acceptance_rates_ec_noise_exp1.png')
    )

def plot_experiment2(
    rounds: List[int],
    noise_levels: List[float],
    shots: int,
    out_dir: str,
    correct_pauli: bool = True,
    encoding_mode: Literal['9a', '9b'] = '9b'
) -> None:
    """Plots both EC acceptance and logical check rates for experiment 2."""
    # One sweep collecting full results
    raw_results = sweep_results(
        run_simulation_experiment2,
        rounds, noise_levels, shots,
        lambda noise: NoiseCfg(ec_active=True, ec_rate_1q=noise, ec_rate_2q=noise, channel_noise_level=0.0),
        correct_pauli=correct_pauli,
        encoding_mode=encoding_mode
    )

    # Derive EC acceptance rate from raw results
    ec_data = {
        noise: [t[0]/shots for t in tuples]  # ec_accept/shots
        for noise, tuples in raw_results.items()
    }

    plot_curve(
        rounds, ec_data,
        title="EC Acceptance vs Rounds (Experiment 2)",
        ylabel="EC Acceptance Rate",
        out_path=os.path.join(out_dir, 'acceptance_rates_ec_noise_exp2.png')
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
        title="Logical Check Success vs Rounds (Experiment 2)",
        ylabel="Logical Success Rate | Accepted",
        out_path=os.path.join(out_dir, 'logical_rates_ec_noise_exp2.png')
    )

def main():
    parser = argparse.ArgumentParser(description="Generate acceptance rate plots for tesseract experiments")
    parser.add_argument('--experiments', type=int, nargs='+', choices=[1, 2], default=[1, 2],
                      help='Which experiments to plot (1, 2, or both)')
    parser.add_argument('--shots', type=int, default=10000,
                      help='Number of shots per data point')
    parser.add_argument('--out-dir', type=str, default='../plots',
                      help='Output directory for plots')
    parser.add_argument('--correct-pauli', type=bool, default=False, help='Correct the Pauli frame')
    # parser.add_argument('--correct-pauli', type=bool, default=True, help='Correct the Pauli frame')
    # parser.add_argument('--encoding-mode', type=Literal['9a', '9b'], default='9b', help='Encoding mode')
    parser.add_argument('--encoding-mode', type=str, choices=['9a', '9b'], default='9a', help='Encoding mode')
    args = parser.parse_args()

    # Combine detailed lower rounds with higher rounds
    rounds = list(range(1, 11)) + [20, 30, 40, 50]
    noise_levels = np.linspace(0.0000, 0.01, 30)  # 30 points between 0 and 1%
    
    os.makedirs(args.out_dir, exist_ok=True)

    print(args.experiments)
    # Temp disable experiment1
    # if 1 in args.experiments:
    #     plot_experiment1(rounds, noise_levels, args.shots, args.out_dir)
    if 2 in args.experiments:
        plot_experiment2(rounds, noise_levels, args.shots, args.out_dir, args.correct_pauli, args.encoding_mode)

if __name__ == "__main__":
    main() 