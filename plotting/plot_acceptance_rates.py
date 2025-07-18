import numpy as np
import matplotlib.pyplot as plt
from tesseract_sim.run import run_simulation
from tesseract_sim.noise_cfg import NoiseCfg
import os

def plot_acceptance_rates():
    # Combine detailed lower rounds with higher rounds
    rounds = list(range(1, 11)) + [20, 30, 40, 50]
    noise_levels_channel = [0, 0.001, 0.01, 0.05, 0.1, 0.2, 0.3]
    # noise_levels_gates = [0.001, 0.01, 0.05, 0.1, 0.2, 0.3]
    noise_levels_gates = np.linspace(0.0000, 0.01, 30)
    shots = 10000  # Number of shots per data point
    
    plt.figure(figsize=(12, 8))
    
    for noise in noise_levels_gates:
        acceptance_rates = []
        
        # Configure noise for the EC phase only
        noise_config = NoiseCfg(
            ec_active=True,
            ec_rate_1q=noise,
            ec_rate_2q=noise
        )

        for r in rounds:
            print(f"Processing rounds={r}, noise={noise} (EC only)")  # Progress indicator
            accept_count, _ = run_simulation(rounds=r, shots=shots, cfg=noise_config)
            acceptance_rate = accept_count / shots
            acceptance_rates.append(acceptance_rate)
        
        plt.plot(rounds, acceptance_rates, marker='o', label=f'EC Noise Rate={noise}')
    
    plt.xlabel('Number of Rounds')
    plt.ylabel('Acceptance Rate')
    plt.title('Acceptance Rate vs. Number of Rounds for Different EC Noise Levels')
    plt.grid(True)
    plt.legend()
    
    # Save to plots folder
    output_filename = os.path.join('../plots', 'acceptance_rates_ec_noise.png')
    plt.savefig(output_filename)
    print(f"Plot saved to {output_filename}")
    plt.close()

if __name__ == "__main__":
    plot_acceptance_rates() 