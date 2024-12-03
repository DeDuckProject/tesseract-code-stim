import stim
import numpy as np
import pymatching

# Counting errors using pymatching to create a decoder
def count_logical_errors(circuit: stim.Circuit, num_shots: int, noiseless_reference_circuit: stim.Circuit=None) -> int:
    # Sample the circuit.
    sampler = circuit.compile_detector_sampler()
    detection_events, observable_flips = sampler.sample(num_shots, separate_observables=True)

    if (noiseless_reference_circuit):
        # Configure a decoder using a reference noiseless circuit.
        # this prevents pymatching from knowing which errors happened in case we simulate them explicitly 
        # https://quantumcomputing.stackexchange.com/questions/32560/using-deterministic-errors-in-stim-detector-circuit-and-decoding-with-pymatching
        detector_error_model = noiseless_reference_circuit.detector_error_model(decompose_errors=True)
    else:
        # Configure a decoder using the circuit.
        detector_error_model = circuit.detector_error_model(decompose_errors=True)
    matcher = pymatching.Matching.from_detector_error_model(detector_error_model)

    # Run the decoder.
    predictions = matcher.decode_batch(detection_events)

    # Count the mistakes.
    num_errors = 0
    for shot in range(num_shots):
        actual_for_shot = observable_flips[shot]
        predicted_for_shot = predictions[shot]
        if not np.array_equal(actual_for_shot, predicted_for_shot):
            num_errors += 1
    return num_errors
#%%
