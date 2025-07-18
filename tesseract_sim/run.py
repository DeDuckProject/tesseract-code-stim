from .circuit_base import init_circuit, channel
from .encoding_manual import encode_manual
from .measurement_rounds import error_correct_manual
from .decoder_manual import run_manual_error_correction

def build_circuit(rounds, noise_level, noise_type="X_ERROR"):
    # We start with a fresh circuit from your helper function 16 qubits for code + 2 ancillas for measurement
    circuit = init_circuit(qubits=18)

    # First, prepare a valid encoded state
    encode_manual(circuit)
    # -----------------------------

    # Now, apply noise to the encoded state
    channel(circuit, noise_level, noise_type=noise_type)

    # Append the error correction rounds to the circuit
    error_correct_manual(circuit, rounds=rounds)
    
    return circuit

def run_simulation(rounds, shots, noise_level, noise_type="X_ERROR"):
    circuit = build_circuit(rounds, noise_level, noise_type)
    
    print(f"--- Running Manual Error Correction Simulation (Corrected) ---")
    print(f"Rounds: {rounds}, Shots: {shots}, Noise: {noise_level}")
    
    return run_manual_error_correction(circuit, shots=shots, rounds=rounds)


if __name__ == "__main__":
    run_simulation(3, 1000, 0.1)