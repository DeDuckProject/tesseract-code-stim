import matplotlib.pyplot as plt
import numpy as np



######################################################################################################
# Plotting detection probability = probability of having at least 1 error
def run_simulation(circuit, channel, error_correction, error_rate, shots=10000):
    # Apply noise channel with the specified error rate
    channel(circuit, error_rate)

    # Perform error correction
    error_correction(circuit)

    # Compile the circuit and run the simulation
    sampler = circuit.compile_detector_sampler()
    samples = sampler.sample(shots=shots)

    # Calculate the detection probability (fraction of shots with any detection event)
    detection_events = np.any(samples, axis=1)
    detection_probability = np.mean(detection_events)

    return detection_probability

def plot_detection_probability(error_rates, detection_probabilities):
    plt.figure(figsize=(10, 6))
    plt.plot(error_rates, detection_probabilities, marker='o', linestyle='-')
    plt.xlabel("Error Rate")
    plt.ylabel("Detection Probability")
    plt.title("Detection Probability vs. Error Rate")
    plt.grid(True)
    plt.show()


######################################################################################################
# Calculating and plotting fidelity (calculation probably incorrect - it is just a starting point)

def calculate_fidelity(circuit, channel, error_correction, error_rate, shots=10000):
    # Apply noise channel and error correction
    channel(circuit, error_rate)
    error_correction(circuit)

    # TODO not sure if this is correct. we don't decode here so how do we know if we have a logical 0? also
    # Logical measurement in the Z basis (ideal state is |0>_L)
    circuit.append("M", list(range(16)))
    sampler = circuit.compile_sampler()
    samples = sampler.sample(shots=shots)

    # Count the fraction of samples where the logical state is measured as |0>_L
    logical_measurements = np.sum(samples, axis=1) % 2  # Parity check
    fidelity = np.mean(logical_measurements == 0)  # Fraction of times we get logical |0>
    return fidelity

def plot_fidelity(error_rates, fidelities):
    plt.figure(figsize=(10, 6))
    plt.plot(error_rates, fidelities, marker='o', linestyle='-')
    plt.xlabel("Error Rate")
    plt.ylabel("Fidelity")
    plt.title("Fidelity vs. Error Rate")
    plt.grid(True)
    plt.show()