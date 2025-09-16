import stim
import numpy as np
from tesseract_sim.error_correction.correction_rules import correct_row_Z, correct_row_X, correct_column_Z, correct_column_X

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



def verify_final_state(shot_tail, frameX=None, frameZ=None, apply_pauli_frame = True, only_z_checks = False):
    """
    Verifies the final state measurements of both 8-3-2 color codes.

    For each 8-3-2 color code, we check the parity of specific gauge operators:
    - X₂: qubits 0^4 (gauge qubit, measured but ignored)
    - X₄: qubits 0^3 (parity check enforced)
    - X₆: qubits 0^1 (parity check enforced)
    - Z₁: qubits 8^12 (gauge qubit, measured but ignored)
    - Z₃: qubits 8^11 (parity check enforced)
    - Z₅: qubits 8^9 (parity check enforced)

    Returns the number of successful parity checks (0-4) for X₄, X₆, Z₃, Z₅.
    If only_z_checks=True, only checks Z₃, Z₅ (for 9a encoding with |++0000>).

    Sources:
    (1) The smallest interesting colour code - by Earl Campbell
        @https://earltcampbell.com/2016/09/26/the-smallest-interesting-colour-code/

    (2) Our main paper - Demonstration of quantum computation and error correction with a tesseract code
        @http://arxiv.org/abs/2409.04628: part III.E and Fig. 5(b) and the explanation in section II
        which is also cited in our function measure_logical_operators_tesseract

    Args:
        shot_tail: Last 16 measurements from the shot data (8 X measurements followed by 8 Z measurements)
        frameX: Array of X-basis Pauli frame corrections
        frameZ: Array of Z-basis Pauli frame corrections
        apply_pauli_frame: True if the Pauli frame corrections should be applied, False otherwise
        only_z_checks: If True, only check Z₃ and Z₅ parity (for 9a encoding with |++0000>)
    Returns:
        int: Number of successful parity checks (0-2 if only_z_checks, 0-4 otherwise)
    """
    # Make a copy to avoid modifying the original data
    corrected = shot_tail.copy()
    
    if apply_pauli_frame:
        if frameX is not None and frameZ is not None:
            # Top half measured in X basis - apply Z frame corrections (phase errors affect X measurements)
            for i in range(8):
                corrected[i] ^= (frameZ[i] & 1)

            # Bottom half measured in Z basis - apply X frame corrections (bit flips affect Z measurements)
            # Account for CNOT propagation: X errors on qubits 0-3 propagate to 12-15, and 4-7 propagate to 8-11
            for i in range(8, 16):
                # Direct X frame corrections for qubits 8-15
                corrected[i] ^= (frameX[i] & 1)

                """ These workarounds are needed because we actually need to apply the correction before measurement.
                A more complete and correct approach would be to branch insert the python error correction code before the final measurements
                See https://quantumcomputing.stackexchange.com/questions/22281/simulating-flag-qubits-and-conditional-branches-using-stim
                For more information.
                """
                # CNOT propagation: X errors from row 1 (0-3) propagate to row 4 (12-15)
                if 12 <= i <= 15:
                    source_qubit = i - 12  # qubit 12→0, 13→1, 14→2, 15→3
                    corrected[i] ^= (frameX[source_qubit] & 1)

                # CNOT propagation: X errors from row 2 (4-7) propagate to row 3 (8-11)
                if 8 <= i <= 11:
                    source_qubit = i - 4   # qubit 8→4, 9→5, 10→6, 11→7
                    corrected[i] ^= (frameX[source_qubit] & 1)

    # Calculate all operator parities for both 8-3-2 color codes
    # X measurements (top half, qubits 0-7)
    x2_parity = corrected[0] ^ corrected[4]  # X₂ gauge qubit - measured but ignored
    x4_parity = corrected[0] ^ corrected[3]  # X₄ parity check
    x6_parity = corrected[0] ^ corrected[1]  # X₆ parity check

    # Z measurements (bottom half, qubits 8-15)
    z1_parity = corrected[13] ^ corrected[9]  # Z₁ gauge qubit - measured but ignored
    z3_parity = corrected[13] ^ corrected[14]  # Z₃ parity check
    z5_parity = corrected[13] ^ corrected[12]   # Z₅ parity check

    # Count successful parity checks based on mode
    if only_z_checks:
        # For 9a encoding (|++0000>), only check Z parities since X measurements are irrelevant
        successful_checks = sum([
            z3_parity == 0,  # Z₃ parity check
            z5_parity == 0   # Z₅ parity check
        ])
    else:
        # For 9b encoding (|+0+0+0>), check all four parities
        successful_checks = sum([
            x4_parity == 0,  # X₄ parity check
            x6_parity == 0,  # X₆ parity check
            z3_parity == 0,  # Z₃ parity check
            z5_parity == 0   # Z₅ parity check
        ])

    return successful_checks

def run_manual_error_correction(circuit, shots, rounds, apply_pauli_frame = True, encoding_mode ='9b'):
    """
    Runs the full manual error correction simulation with final logical state verification.
    
    Args:
        circuit: The quantum circuit to simulate
        shots: Number of shots to run
        rounds: Number of error correction rounds
        apply_pauli_frame: Whether to apply Pauli frame corrections
        encoding_mode: '9a' or '9b' - determines measurement offset and which parity checks to perform
    
    Returns:
        tuple: (ec_accept, logical_shots_passed, average_percentage)
            - ec_accept: number of successful experiments (i.e all rounds of ec "accept")
            - logical_shots_passed: number of experiments when the final logical qubits measured had all qubits in the ideal state
            - average_percentage: average percentage of qubits measured correctly across all shots
    """
    # Calculate parameters based on encoding mode
    only_z_checks = (encoding_mode == '9a')
    measurement_offset = 0 if encoding_mode == '9a' else 2
    max_checks = 2 if only_z_checks else 4
    
    sampler = circuit.compile_sampler()
    shot_data_all = sampler.sample(shots=shots)

    ec_accept = 0
    logical_shots_passed = 0
    total_successful_checks = 0
    fractional_logical_passed = 0.0

    for shot_data in shot_data_all:
        # Process error correction rounds with appropriate measurement offset
        status, frameX, frameZ = process_shot(shot_data, rounds, measurement_offset=measurement_offset)

        if status == "accept":
            ec_accept += 1
            # For accepted shots, count successful parity checks
            successful_checks = verify_final_state(shot_data[-16:], frameX, frameZ, apply_pauli_frame, only_z_checks)
            total_successful_checks += successful_checks
            
            # Count shots where all parity checks pass
            if successful_checks == max_checks:
                logical_shots_passed += 1
            
            # Add fractional contribution for average percentage calculation
            fractional_logical_passed += successful_checks / max_checks

    # Calculate average percentage of qubits measured correctly
    average_percentage = fractional_logical_passed / ec_accept if ec_accept > 0 else None

    print(f"Correcting by Pauli frame → {apply_pauli_frame}")
    print(f"After EC rounds → {ec_accept}/{shots} accepted")
    checks_desc = "Z3,Z5" if only_z_checks else "X4,X6,Z3,Z5"
    print(f"Total successful parity checks ({checks_desc}) → {total_successful_checks}/{shots * max_checks}")
    if average_percentage is not None:
        print(f"Average percentage of checks passed → {average_percentage:.2%}")
    else:
        print(f"Average percentage of checks passed → N/A (no accepted shots)")
    print(f"Logical shots passed (all checks) → {logical_shots_passed}/{shots}")

    return ec_accept, logical_shots_passed, average_percentage 