import stim
import numpy as np
from .correction_rules import correct_row_Z, correct_row_X, correct_column_Z, correct_column_X

def append_detector_on_last_n_measurements(circuit, num_measurements=4):
    circuit.append("DETECTOR", [
        stim.target_rec(-i) for i in range(1,num_measurements+1)
    ])

def process_shot(shot_data, rounds, measurement_offset=0):
    """
    Processes the measurement data for a single shot to apply the error correction logic.
    This function simulates the classical processing part of the decoder.
    Args:
        shot_data: The measurement data for a single shot
        rounds: The number of rounds to process
        measurement_offset: The offset of the measurements to start from.
            This is needed when we have measurements before the error correction rounds, for e.g., when encoding.
    """
    flagX = -1
    flagZ = -1
    frameX = np.zeros(16, dtype=np.uint8)
    frameZ = np.zeros(16, dtype=np.uint8)

    # Each round has 4 (rows) + 4 (cols) = 8 stabilizer measurements.
    # Each stabilizer measurement has 2 measurement outcomes (X and Z).
    measurements_per_round = 8 * 2
    
    for r in range(rounds):
        round_start_index = r * measurements_per_round + measurement_offset
        
        # --- Row Pass ---
        # The first 8 measurements are from the 4 row-stabilizers
        row_measurements = shot_data[round_start_index : round_start_index + 8]
        # X results are at even indices, Z at odd indices
        measX_rows = row_measurements[0::2]
        measZ_rows = row_measurements[1::2]

        # Correct Z errors based on X syndromes
        result = correct_row_Z(flagX, measX_rows.tolist(), frameZ)
        if isinstance(result, str) and result == "reject":
            return "reject", None, None
        flagX, _, frameZ = result

        # Correct X errors based on Z syndromes
        result = correct_row_X(flagZ, measZ_rows.tolist(), frameX)
        if isinstance(result, str) and result == "reject":
            return "reject", None, None
        flagZ, _, frameX = result

        # --- Column Pass ---
        # The next 8 measurements are from the 4 col-stabilizers
        col_measurements = shot_data[round_start_index + 8 : round_start_index + 16]
        measX_cols = col_measurements[0::2]
        measZ_cols = col_measurements[1::2]
        
        # Correct Z errors based on X syndromes
        result = correct_column_Z(flagX, measX_cols.tolist(), frameZ)
        if isinstance(result, str) and result == "reject":
            return "reject", None, None
        flagX, _, frameZ = result

        # Correct X errors based on Z syndromes
        result = correct_column_X(flagZ, measZ_cols.tolist(), frameX)
        if isinstance(result, str) and result == "reject":
            return "reject", None, None
        flagZ, _, frameX = result
        
    return "accept", frameX, frameZ


def run_manual_error_correction(circuit, shots, rounds):
    """
    Runs the full manual error correction simulation.
    """
    sampler = circuit.compile_sampler()
    shot_data_all = sampler.sample(shots=shots)
    
    accept_count = 0
    reject_count = 0
    
    for i in range(shots):
        shot_data = shot_data_all[i]
        status, _, _ = process_shot(shot_data, rounds)
        if status == "accept":
            accept_count += 1
        else:
            reject_count += 1
            
    print(f"Accepted: {accept_count}/{shots}")
    print(f"Rejected: {reject_count}/{shots}")
    print(f"Acceptance Rate: {accept_count/shots:.2%}")

    return accept_count, reject_count 

def verify_final_state(shot_tail):
    """
    Verifies the final state measurements of both 8-3-2 color codes.
    Args:
        shot_tail: Last 16 measurements from the shot data (8 X measurements followed by 8 Z measurements)
    Returns:
        bool: True if both parities are correct (0), False otherwise
    """
    # Top half measured in X basis - all 8 bits should XOR to 0
    top_parity = np.bitwise_xor.reduce(shot_tail[:8])
    # Bottom half measured in Z basis - all 8 bits should XOR to 0
    bottom_parity = np.bitwise_xor.reduce(shot_tail[8:])
    return top_parity == 0 and bottom_parity == 0

def run_manual_error_correction_exp2(circuit, shots, rounds):
    """
    Runs the full manual error correction simulation with final logical state verification.
    Returns counts of shots that pass error correction and logical verification.
    """
    sampler = circuit.compile_sampler()
    shot_data_all = sampler.sample(shots=shots)
    
    ec_accept = logical_pass = logical_fail = 0
    
    for shot_data in shot_data_all:
        # Skip the two ancilla measurements from encoding when processing EC rounds
        status, _, _ = process_shot(shot_data, rounds, measurement_offset=2)
        
        if status == "accept":
            ec_accept += 1
            # For accepted shots, verify the final logical state
            if verify_final_state(shot_data[-16:]):
                logical_pass += 1
            else:
                logical_fail += 1
                
    print(f"After EC rounds → {ec_accept}/{shots} accepted")
    print(f"Final logical check → {logical_pass}/{ec_accept} pass" if ec_accept > 0 else "No shots passed EC")
    print(f"Overall acceptance → {logical_pass/shots:.2%}")

    return ec_accept, logical_pass, logical_fail 