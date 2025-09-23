import numpy as np
import matplotlib.pyplot as plt
from tesseract_sim.run import run_simulation_ec_experiment
from tesseract_sim.noise.noise_cfg import NoiseCfg
import os
from typing import Callable, Dict, List, TypeVar, Tuple, Literal
import argparse
from datetime import datetime
import time

# Add imports for capturing the CLI invocation
import sys, shlex

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

def compute_logical_success_rate(raw_results: Dict[float, List[Tuple[int, int, float]]]) -> Dict[float, List[float]]:
    """Extract logical success rates from raw results. Logical success == all qubits are measured with the correct results.
    
    Args:
        raw_results: Dict mapping noise levels to lists of (accepted, logical_pass, avg_fidelity) tuples
        
    Returns:
        Dict mapping noise levels to lists of logical success rates (logical_pass/accepted)
    """
    return {
        noise: [
            t[1]/t[0] if t[0] > 0 else 0.0  # logical_pass/accepted (conditional probability)
            for t in tuples
        ]
        for noise, tuples in raw_results.items()
    }

def compute_average_fidelity(raw_results: Dict[float, List[Tuple[int, int, float]]]) -> Dict[float, List[float]]:
    """Extract average fidelity values from raw results.
    
    Args:
        raw_results: Dict mapping noise levels to lists of (accepted, logical_pass, avg_fidelity) tuples
        
    Returns:
        Dict mapping noise levels to lists of average fidelity values
    """
    return {
        noise: [t[2] for t in tuples]  # avg_fidelity
        for noise, tuples in raw_results.items()
    }

def plot_curve(
    rounds: List[int],
    data: Dict[float, List[float]],
    title: str,
    ylabel: str,
    out_path: str,
    xlim: Tuple[float, float] = None,
    ylim: Tuple[float, float] = None,
    comparison_data: Dict[float, List[float]] = None,
    comparison_label: str = None
) -> None:
    """Plots and saves a single curve from sweep data.
    
    Args:
        comparison_data: Optional second dataset for comparison (plotted with dashed lines)
        comparison_label: Label suffix for comparison data
    """
    plt.figure(figsize=(12, 8))
    
    # Plot main data with solid lines
    for noise, rates in data.items():
        plt.plot(rounds, rates, marker='o', linestyle='-', 
                label=f'EC Noise Rate={noise:.4f}')
    
    # Plot comparison data with dashed lines if provided
    if comparison_data is not None:
        for noise, rates in comparison_data.items():
            plt.plot(rounds, rates, marker='s', linestyle='--', 
                    label=f'EC Noise Rate={noise:.4f} ({comparison_label})')
    
    plt.xlabel('Number of Rounds')
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True)
    plt.legend()
    
    # Set axis limits if provided
    if xlim is not None:
        plt.xlim(xlim)
    if ylim is not None:
        plt.ylim(ylim)
    
    plt.savefig(out_path)
    print(f"Plot saved to {out_path}")
    plt.close()


def write_experiment_metadata(
    out_dir: str,
    rounds: List[int],
    noise_levels: List[float],
    shots: int,
    apply_pauli_frame: bool,
    encoding_mode: str,
    sweep_channel_noise: bool,
    runtime_seconds: float = None,
    ec_rate_1q: float = None,
    ec_rate_2q: float = None,
    meas_error_rate: float = 0.0,
    channel_noise_rate: float = None,
    comparison_mode: bool = False
) -> None:
    """Write experiment metadata to a text file."""
    metadata_path = os.path.join(out_dir, "experiment_metadata.txt")
    
    with open(metadata_path, 'w') as f:
        f.write("Tesseract EC Experiment Metadata\n")
        f.write("=" * 35 + "\n\n")
        # Record when and how this script was invoked
        f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Command-line: {shlex.join(sys.argv)}\n\n")
        if runtime_seconds is not None:
            hours = int(runtime_seconds // 3600)
            minutes = int((runtime_seconds % 3600) // 60)
            seconds = runtime_seconds % 60
            f.write(f"Total runtime: {hours:02d}:{minutes:02d}:{seconds:06.3f} ({runtime_seconds:.3f} seconds)\n")
        f.write("\n")
        
        f.write("Experiment Parameters:\n")
        f.write("-" * 20 + "\n")
        f.write(f"Rounds: {rounds}\n")
        f.write(f"Noise levels: {list(noise_levels)}\n")
        f.write(f"Shots per data point: {shots}\n")
        f.write(f"Apply Pauli frame correction: {apply_pauli_frame}\n")
        f.write(f"Encoding mode: {encoding_mode}\n")
        f.write(f"Sweep channel noise: {sweep_channel_noise}\n")
        f.write(f"Measurement error rate: {meas_error_rate}\n")
        f.write(f"Comparison mode: {comparison_mode}\n")
        
        # Report if using fixed rates vs sweep
        use_fixed_rates = (ec_rate_1q is not None and ec_rate_2q is not None) or channel_noise_rate is not None
        if use_fixed_rates:
            f.write(f"Mode: Fixed noise rates\n")
            if ec_rate_1q is not None:
                f.write(f"EC 1Q rate (fixed): {ec_rate_1q}\n")
            if ec_rate_2q is not None:
                f.write(f"EC 2Q rate (fixed): {ec_rate_2q}\n")
            if channel_noise_rate is not None:
                f.write(f"Channel noise rate (fixed): {channel_noise_rate}\n")
        else:
            f.write(f"Mode: Sweeping noise rates\n")
        
        if sweep_channel_noise:
            f.write(f"Noise configuration: Sweeping channel noise only\n")
            f.write(f"  - Channel noise type: DEPOLARIZE1\n")
            f.write(f"  - Channel noise applied: After encoding, before EC rounds\n")
            f.write(f"  - EC procedures: Noiseless\n")
            f.write(f"  - Encoding/Decoding: Noiseless\n")
        else:
            f.write(f"Noise configuration: Sweeping EC/decoding noise\n")
            f.write(f"  - EC noise applied: During error correction rounds and decoding\n")
            f.write(f"  - EC 1Q rate: Swept parameter\n")
            f.write(f"  - EC 2Q rate: Swept parameter (same as 1Q)\n")
            f.write(f"  - Channel noise: None (0.0)\n")
            f.write(f"  - Encoding: Noiseless\n")
    
    print(f"Metadata saved to {metadata_path}")

def _run_and_process(
    rounds: List[int],
    noise_levels: List[float],
    shots: int,
    cfg_builder: Callable[[float], NoiseCfg],
    encoding_mode: Literal['9a', '9b'],
    apply_pauli_frame: bool
) -> Tuple[Dict[float, List[float]], Dict[float, List[float]], Dict[float, List[float]]]:
    """
    Helper to run the EC experiment and process its results.
    Returns EC acceptance, logical success, and average fidelity.
    """
    raw_results = sweep_results(
        run_simulation_ec_experiment,
        rounds, noise_levels, shots,
        cfg_builder,
        apply_pauli_frame=apply_pauli_frame,
        encoding_mode=encoding_mode
    )

    ec_data = {
        noise: [t[0]/shots for t in tuples]
        for noise, tuples in raw_results.items()
    }

    logical_data = compute_logical_success_rate(raw_results)

    fidelity_data = compute_average_fidelity(raw_results)

    return ec_data, logical_data, fidelity_data

def plot_metric(
    rounds: List[int],
    datasets: Dict[str, Dict[float, List[float]]],
    title: str,
    ylabel: str,
    out_path: str,
    xlim: Tuple[float, float] = None,
    ylim: Tuple[float, float] = None,
    styles: Dict[str, Tuple[str, str]] = None
) -> None:
    """
    Plots and saves a single metric (e.g., acceptance, logical success, fidelity)
    from sweep data, with optional comparison.
    """
    plt.figure(figsize=(12, 8))
    # Assign consistent colors per noise value
    all_noises = set()
    for dataset in datasets.values():
        all_noises.update(dataset.keys())
    sorted_noises = sorted(all_noises)
    prop_cycle = plt.rcParams.get('axes.prop_cycle')
    colors = prop_cycle.by_key().get('color', []) if prop_cycle else []
    color_map = {noise: colors[i % len(colors)] for i, noise in enumerate(sorted_noises)}

    # Plot each labeled dataset
    for label, dataset in datasets.items():
        linestyle, marker = styles.get(label, ('-', 'o')) if styles else ('-', 'o')
        for noise, rates in dataset.items():
            plt.plot(
                rounds,
                rates,
                color=color_map.get(noise),
                linestyle=linestyle,
                marker=marker,
                label=f'{noise:.4f} ({label})'
            )
    
    plt.xlabel('Number of Rounds')
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True)
    plt.legend()
    
    # Set axis limits if provided
    if xlim is not None:
        plt.xlim(xlim)
    if ylim is not None:
        plt.ylim(ylim)
    
    plt.savefig(out_path)
    print(f"Plot saved to {out_path}")
    plt.close()


def plot_ec_experiment(
    rounds: List[int],
    noise_levels: List[float],
    shots: int,
    base_out_dir: str,
    apply_pauli_frame: bool = True,
    encoding_mode: Literal['9a', '9b'] = '9b',
    sweep_channel_noise: bool = False,
    ec_rate_1q: float = None,
    ec_rate_2q: float = None,
    meas_error_rate: float = 0.0,
    channel_noise_rate: float = None,
    comparison_mode: bool = False
) -> None:
    """Plots EC experiment curves, optionally comparing with/without Pauli-frame correction."""
    start_time = time.time()
    # Create timestamped output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = "_comparison" if comparison_mode else ""
    out_dir = os.path.join(base_out_dir, f"ec_experiment_{timestamp}{suffix}")
    os.makedirs(out_dir, exist_ok=True)

    # Determine if we're using fixed rates or sweeping
    use_fixed_rates = (ec_rate_1q is not None and ec_rate_2q is not None) or channel_noise_rate is not None
    
    if use_fixed_rates:
        # Use fixed rates - ignore noise_levels sweep
        if sweep_channel_noise:
            fixed_channel_rate = channel_noise_rate if channel_noise_rate is not None else 0.0
            cfg_builder = lambda _: NoiseCfg(
                ec_active=False, 
                channel_noise_level=fixed_channel_rate, 
                channel_noise_type="DEPOLARIZE1",
                meas_active=meas_error_rate > 0,
                meas_error_rate=meas_error_rate
            )
            noise_levels = [fixed_channel_rate]  # Single point for fixed rate
        else:
            fixed_1q = ec_rate_1q if ec_rate_1q is not None else 0.0
            fixed_2q = ec_rate_2q if ec_rate_2q is not None else 0.0
            cfg_builder = lambda _: NoiseCfg(
                ec_active=True, 
                ec_rate_1q=fixed_1q, 
                ec_rate_2q=fixed_2q, 
                channel_noise_level=0.0,
                meas_active=meas_error_rate > 0,
                meas_error_rate=meas_error_rate
            )
            noise_levels = [max(fixed_1q, fixed_2q)]  # Single point for plotting
    else:
        # Use original sweep behavior
        if sweep_channel_noise:
            cfg_builder = lambda noise: NoiseCfg(
                ec_active=False, 
                channel_noise_level=noise, 
                channel_noise_type="DEPOLARIZE1",
                meas_active=meas_error_rate > 0,
                meas_error_rate=meas_error_rate
            )
        else:
            cfg_builder = lambda noise: NoiseCfg(
                ec_active=True, 
                ec_rate_1q=noise, 
                ec_rate_2q=noise, 
                channel_noise_level=0.0,
                meas_active=meas_error_rate > 0,
                meas_error_rate=meas_error_rate
            )
    
    # Run sweeping and processing in helper
    ec_main, log_main, fid_main = _run_and_process(
        rounds, noise_levels, shots, cfg_builder, encoding_mode, apply_pauli_frame
    )

    # Prepare datasets and styles
    if comparison_mode:
        ec_comp, log_comp, fid_comp = _run_and_process(
            rounds, noise_levels, shots, cfg_builder, encoding_mode, not apply_pauli_frame
        )
        labels = ['with correction', 'without correction']
        datasets_accept = {
            labels[0]: ec_main,
            labels[1]: ec_comp,
        }
        datasets_logical = {
            labels[0]: log_main,
            labels[1]: log_comp,
        }
        datasets_fidelity = {
            labels[0]: fid_main,
            labels[1]: fid_comp,
        }
        styles = {
            labels[0]: ('-', 'o'),
            labels[1]: ('--', 's'),
        }
    else:
        label = 'with correction' if apply_pauli_frame else 'without correction'
        datasets_accept = {label: ec_main}
        datasets_logical = {label: log_main}
        datasets_fidelity = {label: fid_main}
        styles = {label: ('-', 'o')}

    # Plot each metric
    max_rounds = max(rounds)
    x_range = (0, max_rounds)
    noise_type = "Channel" if sweep_channel_noise else "EC"

    plot_metric(
        rounds, datasets_accept,
        title=f"{noise_type} Acceptance vs Rounds (EC Experiment){' - Comparison' if comparison_mode else ''}",
        ylabel="EC Acceptance Rate",
        out_path=os.path.join(out_dir, 'acceptance_rates_ec_experiment.png'),
        xlim=x_range, ylim=(-0.01, 1.01), styles=styles
    )
    plot_metric(
        rounds, datasets_logical,
        title=f"Logical Check Success vs Rounds (EC Experiment) - {noise_type} Noise{' - Comparison' if comparison_mode else ''}",
        ylabel="Logical Success Rate | Accepted",
        out_path=os.path.join(out_dir, 'logical_rates_ec_experiment.png'),
        xlim=x_range, ylim=(-0.01, 1.01), styles=styles
    )
    plot_metric(
        rounds, datasets_fidelity,
        title=f"Average Fidelity vs Rounds (EC Experiment) - {noise_type} Noise{' - Comparison' if comparison_mode else ''}",
        ylabel="Average Fidelity",
        out_path=os.path.join(out_dir, 'fidelity_rates_ec_experiment.png'),
        xlim=x_range, ylim=(0.45, 1.01), styles=styles
    )

    # Write final metadata with runtime
    runtime_seconds = time.time() - start_time
    write_experiment_metadata(
        out_dir, rounds, noise_levels, shots,
        apply_pauli_frame, encoding_mode, sweep_channel_noise,
        runtime_seconds=runtime_seconds,
        ec_rate_1q=ec_rate_1q, ec_rate_2q=ec_rate_2q,
        meas_error_rate=meas_error_rate, channel_noise_rate=channel_noise_rate,
        comparison_mode=comparison_mode
    )
    print(f"All experiment files saved to: {out_dir}")
    print(f"Total experiment runtime: {runtime_seconds:.1f} seconds")

def str_to_bool(v):
    """Convert string to boolean for argparse."""
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def main():
    # Define defaults
    default_rounds = list(range(1, 11)) + [15, 20]
    default_noise_levels = list(np.linspace(0.0000, 0.01, 10))
    
    parser = argparse.ArgumentParser(description="Generate acceptance rate plots for tesseract experiments")
    parser.add_argument('--experiments', type=int, nargs='+', choices=[2], default=[2],
                      help='Which experiments to plot (currently only 2 is supported)')
    parser.add_argument('--shots', type=int, default=10000,
                      help='Number of shots per data point')
    parser.add_argument('--out-dir', type=str, default='./plots',
                      help='Base output directory for plots (timestamped subdirectory will be created)')
    parser.add_argument('--apply_pauli_frame', type=str_to_bool, default=False, help='Perform final correction - apply the measured Pauli frame. The error correction rounds and measurements (besides the actual correction at the end) happen regardless, based on the number of rounds.')
    parser.add_argument('--encoding-mode', type=str, choices=['9a', '9b'], default='9a', help='Encoding mode')
    parser.add_argument('--sweep-channel-noise', action='store_true', help='Sweep channel noise instead of EC noise. Channel noise acts once after encoding and before the error correction rounds.')
    parser.add_argument('--rounds', type=int, nargs='+', default=default_rounds,
                      help=f'List of EC rounds to sweep (e.g. 1 10 20 30). Default: {default_rounds}')
    parser.add_argument('--noise-levels', type=float, nargs='+', default=default_noise_levels,
                      help=f'List of noise rates to sweep (e.g. 0.05 0.1 0.2). Default: 10 points from 0.0 to 0.01')
    parser.add_argument('--ec-rate-1q', type=float, default=None,
                      help='Single-qubit gate error rate for EC operations (overrides noise-levels sweep)')
    parser.add_argument('--ec-rate-2q', type=float, default=None,
                      help='Two-qubit gate error rate for EC operations (overrides noise-levels sweep)')
    parser.add_argument('--meas-error-rate', type=float, default=0.0,
                      help='Measurement error rate (SPAM error)')
    parser.add_argument('--channel-noise-rate', type=float, default=None,
                      help='Channel noise rate (overrides noise-levels sweep when using --sweep-channel-noise)')
    parser.add_argument('--comparison-mode', action='store_true',
                      help='Run comparison between experiments with and without apply_pauli_frame')
    args = parser.parse_args()

    # Use configurable values
    rounds = args.rounds
    noise_levels = args.noise_levels
    
    os.makedirs(args.out_dir, exist_ok=True)

    print(args.experiments)
    if 2 in args.experiments:
        plot_ec_experiment(
            rounds, noise_levels, args.shots, args.out_dir, 
            args.apply_pauli_frame, args.encoding_mode, args.sweep_channel_noise,
            args.ec_rate_1q, args.ec_rate_2q, args.meas_error_rate, args.channel_noise_rate,
            args.comparison_mode
        )

if __name__ == "__main__":
    main() 