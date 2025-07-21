import numpy as np
import matplotlib.pyplot as plt
from tesseract_sim.run import run_simulation_experiment1, run_simulation_experiment2
from tesseract_sim.noise_cfg import NoiseCfg
import os
from typing import Callable, Dict, List, Any, TypeVar, Tuple
import argparse

T = TypeVar('T')  # Type of experiment result

def sweep_metric(
    experiment_fn: Callable[[int, int, NoiseCfg], T],
    metric_fn: Callable[[T], float],
    rounds: List[int],
    noise_levels: List[float],
    shots: int,
    cfg_builder: Callable[[float], NoiseCfg]
) -> Dict[float, List[float]]:
    """
    Sweeps over rounds and noise levels, computing a metric for each combination.
    
    Args:
        experiment_fn: Function that runs an experiment (e.g. run_simulation_experiment1)
        metric_fn: Function that computes a metric from experiment results
        rounds: List of round counts to sweep
        noise_levels: List of noise levels to sweep
        shots: Number of shots per data point
        cfg_builder: Function that creates a NoiseCfg from a noise level
    
    Returns:
        Dictionary mapping noise levels to lists of metric values (one per round)
    """
    results: Dict[float, List[float]] = {}
    
    for noise in noise_levels:
        acceptance_rates = []
        noise_config = cfg_builder(noise)
        
        for r in rounds:
            print(f"Processing rounds={r}, noise={noise}")
            result = experiment_fn(rounds=r, shots=shots, cfg=noise_config)
            rate = metric_fn(result)
            acceptance_rates.append(rate)
        
        results[noise] = acceptance_rates
    
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
    out_dir: str
) -> None:
    """Plots acceptance rates for experiment 1."""
    data = sweep_metric(
        run_simulation_experiment1,
        lambda res: res[0]/shots,  # accept_count/shots
        rounds, noise_levels, shots,
        lambda noise: NoiseCfg(ec_active=True, ec_rate_1q=noise, ec_rate_2q=noise)
    )
    
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
    out_dir: str
) -> None:
    """Plots both EC acceptance and logical check rates for experiment 2."""
    # EC acceptance rate
    ec_data = sweep_metric(
        run_simulation_experiment2,
        lambda res: res[0]/shots,  # ec_accept/shots
        rounds, noise_levels, shots,
        lambda noise: NoiseCfg(ec_active=True, ec_rate_1q=noise, ec_rate_2q=noise)
    )
    
    plot_curve(
        rounds, ec_data,
        title="EC Acceptance vs Rounds (Experiment 2)",
        ylabel="EC Acceptance Rate",
        out_path=os.path.join(out_dir, 'acceptance_rates_ec_noise_exp2.png')
    )
    
    # Logical check rate (relative to total shots)
    logical_data = sweep_metric(
        run_simulation_experiment2,
        lambda res: res[1]/shots,  # logical_pass/shots
        rounds, noise_levels, shots,
        lambda noise: NoiseCfg(ec_active=True, ec_rate_1q=noise, ec_rate_2q=noise)
    )
    
    plot_curve(
        rounds, logical_data,
        title="Logical Check Success vs Rounds (Experiment 2)",
        ylabel="Logical Success Rate",
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
    args = parser.parse_args()

    # Combine detailed lower rounds with higher rounds
    rounds = list(range(1, 11)) + [20, 30, 40, 50]
    noise_levels = np.linspace(0.0000, 0.01, 30)  # 30 points between 0 and 1%
    
    os.makedirs(args.out_dir, exist_ok=True)
    
    if 1 in args.experiments:
        plot_experiment1(rounds, noise_levels, args.shots, args.out_dir)
    if 2 in args.experiments:
        plot_experiment2(rounds, noise_levels, args.shots, args.out_dir)

if __name__ == "__main__":
    main() 