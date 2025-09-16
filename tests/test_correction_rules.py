import pytest
import numpy as np
from tesseract_sim.error_correction.correction_rules import (
    correct_column_Z,
    correct_column_X,
    correct_row_Z,
    correct_row_X,
)


class TestUnflaggedTwoErrorRejection:
    """Test that all correction functions reject when flag=-1 and sum(meas)==2"""
    
    @pytest.mark.parametrize("meas_pattern", [
        [1, 1, 0, 0],
        [0, 0, 1, 1], 
        [1, 0, 1, 0],
        [0, 1, 0, 1],
        [1, 0, 0, 1],
        [0, 1, 1, 0]
    ])
    def test_correct_column_Z_unflagged_two_errors_reject(self, meas_pattern):
        """Test correct_column_Z rejects unflagged two-error patterns"""
        frameZ = np.zeros(16, dtype=np.uint8)
        result = correct_column_Z(-1, meas_pattern, frameZ)
        assert result == "reject"
        # Frame should remain unchanged
        assert np.array_equal(frameZ, np.zeros(16, dtype=np.uint8))
    
    @pytest.mark.parametrize("meas_pattern", [
        [1, 1, 0, 0],
        [0, 0, 1, 1], 
        [1, 0, 1, 0],
        [0, 1, 0, 1],
        [1, 0, 0, 1],
        [0, 1, 1, 0]
    ])
    def test_correct_column_X_unflagged_two_errors_reject(self, meas_pattern):
        """Test correct_column_X rejects unflagged two-error patterns"""
        frameX = np.zeros(16, dtype=np.uint8)
        result = correct_column_X(-1, meas_pattern, frameX)
        assert result == "reject"
        # Frame should remain unchanged
        assert np.array_equal(frameX, np.zeros(16, dtype=np.uint8))
    
    @pytest.mark.parametrize("meas_pattern", [
        [1, 1, 0, 0],
        [0, 0, 1, 1], 
        [1, 0, 1, 0],
        [0, 1, 0, 1],
        [1, 0, 0, 1],
        [0, 1, 1, 0]
    ])
    def test_correct_row_Z_unflagged_two_errors_reject(self, meas_pattern):
        """Test correct_row_Z rejects unflagged two-error patterns"""
        frameZ = np.zeros(16, dtype=np.uint8)
        result = correct_row_Z(-1, meas_pattern, frameZ)
        assert result == "reject"
        # Frame should remain unchanged
        assert np.array_equal(frameZ, np.zeros(16, dtype=np.uint8))
    
    @pytest.mark.parametrize("meas_pattern", [
        [1, 1, 0, 0],
        [0, 0, 1, 1], 
        [1, 0, 1, 0],
        [0, 1, 0, 1],
        [1, 0, 0, 1],
        [0, 1, 1, 0]
    ])
    def test_correct_row_X_unflagged_two_errors_reject(self, meas_pattern):
        """Test correct_row_X rejects unflagged two-error patterns"""
        frameX = np.zeros(16, dtype=np.uint8)
        result = correct_row_X(-1, meas_pattern, frameX)
        assert result == "reject"
        # Frame should remain unchanged
        assert np.array_equal(frameX, np.zeros(16, dtype=np.uint8))


class TestUnflaggedSingleErrorFlagging:
    """Test that single errors (sum==1 or 3) properly set flags when unflagged"""
    
    @pytest.mark.parametrize("error_pos", [0, 1, 2, 3])
    def test_correct_column_Z_flags_single_error(self, error_pos):
        """Test correct_column_Z flags the disagreeing position for single errors"""
        frameZ = np.zeros(16, dtype=np.uint8)
        meas_pattern = [0] * 4
        meas_pattern[error_pos] = 1  # Single disagreeing measurement
        
        flagX, measX, frameZ_out = correct_column_Z(-1, meas_pattern, frameZ)
        
        assert flagX == error_pos
        assert measX == meas_pattern
        assert np.array_equal(frameZ_out, frameZ)  # No frame correction yet
    
    @pytest.mark.parametrize("error_pos", [0, 1, 2, 3])
    def test_correct_column_Z_flags_triple_error(self, error_pos):
        """Test correct_column_Z flags the single non-disagreeing position for triple errors"""
        frameZ = np.zeros(16, dtype=np.uint8)
        meas_pattern = [1] * 4
        meas_pattern[error_pos] = 0  # Single non-disagreeing measurement
        
        flagX, measX, frameZ_out = correct_column_Z(-1, meas_pattern, frameZ)
        
        assert flagX == error_pos
        assert measX == meas_pattern
        assert np.array_equal(frameZ_out, frameZ)  # No frame correction yet
    
    @pytest.mark.parametrize("error_pos", [0, 1, 2, 3])
    def test_correct_column_X_flags_single_error(self, error_pos):
        """Test correct_column_X flags the disagreeing position for single errors"""
        frameX = np.zeros(16, dtype=np.uint8)
        meas_pattern = [0] * 4
        meas_pattern[error_pos] = 1
        
        flagZ, measZ, frameX_out = correct_column_X(-1, meas_pattern, frameX)
        
        assert flagZ == error_pos
        assert measZ == meas_pattern
        assert np.array_equal(frameX_out, frameX)
    
    @pytest.mark.parametrize("error_pos", [0, 1, 2, 3])
    def test_correct_row_Z_flags_single_error(self, error_pos):
        """Test correct_row_Z flags the disagreeing position for single errors"""
        frameZ = np.zeros(16, dtype=np.uint8)
        meas_pattern = [0] * 4
        meas_pattern[error_pos] = 1
        
        flagX, measX, frameZ_out = correct_row_Z(-1, meas_pattern, frameZ)
        
        assert flagX == error_pos
        assert measX == meas_pattern
        assert np.array_equal(frameZ_out, frameZ)
    
    @pytest.mark.parametrize("error_pos", [0, 1, 2, 3])
    def test_correct_row_X_flags_single_error(self, error_pos):
        """Test correct_row_X flags the disagreeing position for single errors"""
        frameX = np.zeros(16, dtype=np.uint8)
        meas_pattern = [0] * 4
        meas_pattern[error_pos] = 1
        
        flagZ, measZ, frameX_out = correct_row_X(-1, meas_pattern, frameX)
        
        assert flagZ == error_pos
        assert measZ == meas_pattern
        assert np.array_equal(frameX_out, frameX)


class TestFlaggedSingleErrorCorrection:
    """Test frame corrections when flag is already set and single error occurs"""
    
    @pytest.mark.parametrize("flag_row", [0, 1, 2, 3])
    @pytest.mark.parametrize("error_col", [0, 1, 2, 3])
    def test_correct_column_Z_flagged_single_correction(self, flag_row, error_col):
        """Test correct_column_Z applies Z correction when flagged"""
        frameZ = np.zeros(16, dtype=np.uint8)
        meas_pattern = [0] * 4
        meas_pattern[error_col] = 1
        
        flagX, measX, frameZ_out = correct_column_Z(flag_row, meas_pattern, frameZ)
        
        assert flagX == -1  # Flag should be cleared
        assert measX == meas_pattern
        expected_frame = np.zeros(16, dtype=np.uint8)
        expected_frame[4 * flag_row + error_col] = 1  # Z correction at flagged position
        assert np.array_equal(frameZ_out, expected_frame)
    
    @pytest.mark.parametrize("flag_row", [0, 1, 2, 3])
    @pytest.mark.parametrize("error_col", [0, 1, 2, 3])
    def test_correct_column_X_flagged_single_correction(self, flag_row, error_col):
        """Test correct_column_X applies X correction when flagged"""
        frameX = np.zeros(16, dtype=np.uint8)
        meas_pattern = [0] * 4
        meas_pattern[error_col] = 1
        
        flagZ, measZ, frameX_out = correct_column_X(flag_row, meas_pattern, frameX)
        
        assert flagZ == -1  # Flag should be cleared
        assert measZ == meas_pattern
        expected_frame = np.zeros(16, dtype=np.uint8)
        expected_frame[4 * flag_row + error_col] = 1  # X correction at flagged position
        assert np.array_equal(frameX_out, expected_frame)
    
    @pytest.mark.parametrize("flag_col", [0, 1, 2, 3])
    @pytest.mark.parametrize("error_row", [0, 1, 2, 3])
    def test_correct_row_Z_flagged_single_correction(self, flag_col, error_row):
        """Test correct_row_Z applies Z correction when flagged"""
        frameZ = np.zeros(16, dtype=np.uint8)
        meas_pattern = [0] * 4
        meas_pattern[error_row] = 1
        
        flagX, measX, frameZ_out = correct_row_Z(flag_col, meas_pattern, frameZ)
        
        assert flagX == -1  # Flag should be cleared
        assert measX == meas_pattern
        expected_frame = np.zeros(16, dtype=np.uint8)
        expected_frame[4 * error_row + flag_col] = 1  # Z correction at flagged position
        assert np.array_equal(frameZ_out, expected_frame)
    
    @pytest.mark.parametrize("flag_col", [0, 1, 2, 3])
    @pytest.mark.parametrize("error_row", [0, 1, 2, 3])
    def test_correct_row_X_flagged_single_correction(self, flag_col, error_row):
        """Test correct_row_X applies X correction when flagged"""
        frameX = np.zeros(16, dtype=np.uint8)
        meas_pattern = [0] * 4
        meas_pattern[error_row] = 1
        
        flagZ, measZ, frameX_out = correct_row_X(flag_col, meas_pattern, frameX)
        
        assert flagZ == -1  # Flag should be cleared
        assert measZ == meas_pattern
        expected_frame = np.zeros(16, dtype=np.uint8)
        expected_frame[4 * error_row + flag_col] = 1  # X correction at flagged position
        assert np.array_equal(frameX_out, expected_frame)


class TestFlaggedSpecialTwoErrorPatterns:
    """Test handling of special two-error patterns when flagged"""
    
    @pytest.mark.parametrize("flag_row", [0, 1, 2, 3])
    @pytest.mark.parametrize("pattern", [[0, 0, 1, 1], [1, 1, 0, 0]])
    def test_correct_column_Z_flagged_special_patterns(self, flag_row, pattern):
        """Test correct_column_Z handles special two-error patterns when flagged"""
        frameZ = np.zeros(16, dtype=np.uint8)
        
        flagX, measX, frameZ_out = correct_column_Z(flag_row, pattern, frameZ)
        
        assert flagX == -1  # Flag should be cleared
        assert measX == pattern
        expected_frame = np.zeros(16, dtype=np.uint8)
        # ZZII pattern on flagged row
        expected_frame[4 * flag_row] = 1
        expected_frame[4 * flag_row + 1] = 1
        assert np.array_equal(frameZ_out, expected_frame)
    
    @pytest.mark.parametrize("flag_row", [0, 1, 2, 3])
    @pytest.mark.parametrize("pattern", [[0, 0, 1, 1], [1, 1, 0, 0]])
    def test_correct_column_X_flagged_special_patterns(self, flag_row, pattern):
        """Test correct_column_X handles special two-error patterns when flagged"""
        frameX = np.zeros(16, dtype=np.uint8)
        
        flagZ, measZ, frameX_out = correct_column_X(flag_row, pattern, frameX)
        
        assert flagZ == -1  # Flag should be cleared
        assert measZ == pattern
        expected_frame = np.zeros(16, dtype=np.uint8)
        # XXII pattern on flagged row
        expected_frame[4 * flag_row] = 1
        expected_frame[4 * flag_row + 1] = 1
        assert np.array_equal(frameX_out, expected_frame)
    
    @pytest.mark.parametrize("flag_col", [0, 1, 2, 3])
    @pytest.mark.parametrize("pattern", [[0, 0, 1, 1], [1, 1, 0, 0]])
    def test_correct_row_Z_flagged_special_patterns(self, flag_col, pattern):
        """Test correct_row_Z handles special two-error patterns when flagged"""
        frameZ = np.zeros(16, dtype=np.uint8)
        
        flagX, measX, frameZ_out = correct_row_Z(flag_col, pattern, frameZ)
        
        assert flagX == -1  # Flag should be cleared
        assert measX == pattern
        expected_frame = np.zeros(16, dtype=np.uint8)
        # ZZII pattern on flagged column
        expected_frame[4 * 0 + flag_col] = 1  # Row 0
        expected_frame[4 * 1 + flag_col] = 1  # Row 1
        assert np.array_equal(frameZ_out, expected_frame)
    
    @pytest.mark.parametrize("flag_col", [0, 1, 2, 3])
    @pytest.mark.parametrize("pattern", [[0, 0, 1, 1], [1, 1, 0, 0]])
    def test_correct_row_X_flagged_special_patterns(self, flag_col, pattern):
        """Test correct_row_X handles special two-error patterns when flagged"""
        frameX = np.zeros(16, dtype=np.uint8)
        
        flagZ, measZ, frameX_out = correct_row_X(flag_col, pattern, frameX)
        
        assert flagZ == -1  # Flag should be cleared
        assert measZ == pattern
        expected_frame = np.zeros(16, dtype=np.uint8)
        # XXII pattern on flagged column
        expected_frame[4 * 0 + flag_col] = 1  # Row 0
        expected_frame[4 * 1 + flag_col] = 1  # Row 1
        assert np.array_equal(frameX_out, expected_frame)


class TestFlaggedInvalidTwoErrorRejection:
    """Test rejection of invalid two-error patterns when flagged"""
    
    @pytest.mark.parametrize("flag_row", [0, 1, 2, 3])
    @pytest.mark.parametrize("pattern", [
        [1, 0, 1, 0],
        [0, 1, 0, 1], 
        [1, 0, 0, 1],
        [0, 1, 1, 0]
    ])
    def test_correct_column_Z_flagged_invalid_patterns_reject(self, flag_row, pattern):
        """Test correct_column_Z rejects invalid two-error patterns when flagged"""
        frameZ = np.zeros(16, dtype=np.uint8)
        result = correct_column_Z(flag_row, pattern, frameZ)
        assert result == "reject"
        assert np.array_equal(frameZ, np.zeros(16, dtype=np.uint8))  # Frame should remain unchanged
    
    @pytest.mark.parametrize("flag_row", [0, 1, 2, 3])
    @pytest.mark.parametrize("pattern", [
        [1, 0, 1, 0],
        [0, 1, 0, 1], 
        [1, 0, 0, 1],
        [0, 1, 1, 0]
    ])
    def test_correct_column_X_flagged_invalid_patterns_reject(self, flag_row, pattern):
        """Test correct_column_X rejects invalid two-error patterns when flagged"""
        frameX = np.zeros(16, dtype=np.uint8)
        result = correct_column_X(flag_row, pattern, frameX)
        assert result == "reject"
        assert np.array_equal(frameX, np.zeros(16, dtype=np.uint8))  # Frame should remain unchanged
    
    @pytest.mark.parametrize("flag_col", [0, 1, 2, 3])
    @pytest.mark.parametrize("pattern", [
        [1, 0, 1, 0],
        [0, 1, 0, 1], 
        [1, 0, 0, 1],
        [0, 1, 1, 0]
    ])
    def test_correct_row_Z_flagged_invalid_patterns_reject(self, flag_col, pattern):
        """Test correct_row_Z rejects invalid two-error patterns when flagged"""
        frameZ = np.zeros(16, dtype=np.uint8)
        result = correct_row_Z(flag_col, pattern, frameZ)
        assert result == "reject"
        assert np.array_equal(frameZ, np.zeros(16, dtype=np.uint8))  # Frame should remain unchanged
    
    @pytest.mark.parametrize("flag_col", [0, 1, 2, 3])
    @pytest.mark.parametrize("pattern", [
        [1, 0, 1, 0],
        [0, 1, 0, 1], 
        [1, 0, 0, 1],
        [0, 1, 1, 0]
    ])
    def test_correct_row_X_flagged_invalid_patterns_reject(self, flag_col, pattern):
        """Test correct_row_X rejects invalid two-error patterns when flagged"""
        frameX = np.zeros(16, dtype=np.uint8)
        result = correct_row_X(flag_col, pattern, frameX)
        assert result == "reject"
        assert np.array_equal(frameX, np.zeros(16, dtype=np.uint8))  # Frame should remain unchanged


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_all_zeros_no_correction_needed(self):
        """Test that all-zero measurements don't trigger corrections"""
        frameZ = np.zeros(16, dtype=np.uint8)
        frameX = np.zeros(16, dtype=np.uint8)
        pattern = [0, 0, 0, 0]
        
        # All functions should return unchanged state for all-zero pattern
        result_col_z = correct_column_Z(-1, pattern, frameZ.copy())
        result_col_x = correct_column_X(-1, pattern, frameX.copy())
        result_row_z = correct_row_Z(-1, pattern, frameZ.copy())
        result_row_x = correct_row_X(-1, pattern, frameX.copy())
        
        # Should return tuple with unchanged flag and frame for no errors
        assert result_col_z[0] == -1 and result_col_z[1] == pattern and np.array_equal(result_col_z[2], frameZ)
        assert result_col_x[0] == -1 and result_col_x[1] == pattern and np.array_equal(result_col_x[2], frameX)
        assert result_row_z[0] == -1 and result_row_z[1] == pattern and np.array_equal(result_row_z[2], frameZ)
        assert result_row_x[0] == -1 and result_row_x[1] == pattern and np.array_equal(result_row_x[2], frameX)
    
    def test_all_ones_no_correction_needed(self):
        """Test that all-one measurements don't trigger corrections"""
        frameZ = np.zeros(16, dtype=np.uint8)
        frameX = np.zeros(16, dtype=np.uint8)
        pattern = [1, 1, 1, 1]
        
        # All functions should return unchanged state for all-one pattern
        result_col_z = correct_column_Z(-1, pattern, frameZ.copy())
        result_col_x = correct_column_X(-1, pattern, frameX.copy())
        result_row_z = correct_row_Z(-1, pattern, frameZ.copy())
        result_row_x = correct_row_X(-1, pattern, frameX.copy())
        
        # Should return tuple with unchanged flag and frame for no disagreement
        assert result_col_z[0] == -1 and result_col_z[1] == pattern and np.array_equal(result_col_z[2], frameZ)
        assert result_col_x[0] == -1 and result_col_x[1] == pattern and np.array_equal(result_col_x[2], frameX)
        assert result_row_z[0] == -1 and result_row_z[1] == pattern and np.array_equal(result_row_z[2], frameZ)
        assert result_row_x[0] == -1 and result_row_x[1] == pattern and np.array_equal(result_row_x[2], frameX)
    
    @pytest.mark.parametrize("flag_val", [0, 1, 2, 3])
    def test_flagged_all_zeros_no_correction(self, flag_val):
        """Test flagged state with all-zero measurements clears flag"""
        frameZ = np.zeros(16, dtype=np.uint8)
        frameX = np.zeros(16, dtype=np.uint8)
        pattern = [0, 0, 0, 0]
        
        result_col_z = correct_column_Z(flag_val, pattern, frameZ.copy())
        result_col_x = correct_column_X(flag_val, pattern, frameX.copy())
        result_row_z = correct_row_Z(flag_val, pattern, frameZ.copy())
        result_row_x = correct_row_X(flag_val, pattern, frameX.copy())
        
        # Flag should be cleared, frame unchanged
        assert result_col_z[0] == -1 and result_col_z[1] == pattern and np.array_equal(result_col_z[2], frameZ)
        assert result_col_x[0] == -1 and result_col_x[1] == pattern and np.array_equal(result_col_x[2], frameX)
        assert result_row_z[0] == -1 and result_row_z[1] == pattern and np.array_equal(result_row_z[2], frameZ)
        assert result_row_x[0] == -1 and result_row_x[1] == pattern and np.array_equal(result_row_x[2], frameX)
    
    def test_frame_accumulation(self):
        """Test that corrections accumulate in the frame"""
        frameZ = np.zeros(16, dtype=np.uint8)
        frameZ[5] = 2  # Pre-existing correction
        
        pattern = [0, 1, 0, 0]  # Single error at position 1
        flagX, measX, frameZ_out = correct_column_Z(1, pattern, frameZ)  # Flag row 1
        
        expected_frame = np.zeros(16, dtype=np.uint8)
        expected_frame[5] = 3  # 2 + 1 = 3 (accumulated correction at position 4*1+1=5)
        
        assert flagX == -1
        assert np.array_equal(frameZ_out, expected_frame)
