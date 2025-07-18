import numpy as np
import matplotlib.pyplot as plt
from tesseract_sim.run import run_simulation
import os

def plot_acceptance_rates():
    # Combine detailed lower rounds with higher rounds
    rounds = list(range(1, 11)) + [20, 30, 40, 50]
    noise_levels = [0.001, 0.01, 0.05, 0.1, 0.2, 0.3]
    shots = 10000  # Number of shots per data point
    
    plt.figure(figsize=(12, 8))
    
    for noise in noise_levels:
        acceptance_rates = []
        for r in rounds:
            print(f"Processing rounds={r}, noise={noise}")  # Progress indicator
            accept_count, reject_count = run_simulation(r, shots, noise)
            acceptance_rate = accept_count / shots
            acceptance_rates.append(acceptance_rate)
        
        plt.plot(rounds, acceptance_rates, marker='o', label=f'Noise={noise}')
    
    plt.xlabel('Number of Rounds')
    plt.ylabel('Acceptance Rate')
    plt.title('Acceptance Rate vs Number of Rounds for Different Noise Levels')
    plt.grid(True)
    plt.legend()
    
    # Save to plots folder
    plt.savefig(os.path.join('plots', 'acceptance_rates.png'))
    plt.close()

if __name__ == "__main__":
    plot_acceptance_rates() 