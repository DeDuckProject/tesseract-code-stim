# Reference code for correcting Z error in column:
def correct_column_Z(flagX: int, measX, frameZ):
    if flagX == -1:  # no row flagged already
        if sum(measX) == 2:
            return "reject"
        if sum(measX) in (1, 3):
            if sum(measX) == 1:
                # Disagreeing measurement is 1 -> flag the index of 1
                flagX = measX.index(1)
            else:
                # Disagreeing measurement is 0 -> flag the index of 0
                flagX = measX.index(0)
    else:  # row flagX in (0, 1, 2, 3) flagged
        if sum(measX) in (1, 3):
            if sum(measX) == 1:
                col = measX.index(1)
            else:
                col = measX.index(0)
            frameZ[4 * flagX + col] += 1  # Z correction
        if sum(measX) == 2:
            if measX in ([0, 0, 1, 1], [1, 1, 0, 0]):
                frameZ[[4 * flagX, 4 * flagX + 1]] += 1  # ZZII on flagged row
            else:
                return "reject"
        flagX = -1
    return flagX, measX, frameZ

# Deduced from above example:
# TODO test following correction - I went over them manually and they look ok. and make sense as far as I understand
def correct_column_X(flagZ, measZ, frameX):
    if flagZ == -1:  # No row flagged already
        if sum(measZ) == 2:
            return "reject"
        if sum(measZ) in (1, 3):
            if sum(measZ) == 1:
                flagZ = measZ.index(1)
            else:
                flagZ = measZ.index(0)
    else:  # Row flagZ in (0, 1, 2, 3) flagged
        if sum(measZ) in (1, 3):
            if sum(measZ) == 1:
                col = measZ.index(1)
            else:
                col = measZ.index(0)
            frameX[4 * flagZ + col] += 1  # Apply X correction
        elif sum(measZ) == 2:
            if measZ in ([0, 0, 1, 1], [1, 1, 0, 0]):
                frameX[[4 * flagZ, 4 * flagZ + 1]] += 1  # XXII on flagged row
            else:
                return "reject"
        flagZ = -1
    return flagZ, measZ, frameX

def correct_row_Z(flagX, measX, frameZ):
    if flagX == -1:  # No column flagged already
        if sum(measX) == 2:
            return "reject"
        if sum(measX) in (1, 3):
            if sum(measX) == 1:
                flagX = measX.index(1)
            else:
                flagX = measX.index(0)
    else:  # Column flagX in (0, 1, 2, 3) flagged
        if sum(measX) in (1, 3):
            if sum(measX) == 1:
                row = measX.index(1)
            else:
                row = measX.index(0)
            frameZ[4 * row + flagX] += 1  # Apply Z correction
        elif sum(measX) == 2:
            if measX in ([0, 0, 1, 1], [1, 1, 0, 0]):
                frameZ[[4 * 0 + flagX, 4 * 1 + flagX]] += 1  # ZZII on flagged column. multiplication by 0 is for readability.
            else:
                return "reject"
        flagX = -1
    return flagX, measX, frameZ

def correct_row_X(flagZ, measZ, frameX):
    if flagZ == -1:  # No column flagged already
        if sum(measZ) == 2:
            return "reject"
        if sum(measZ) in (1, 3):
            if sum(measZ) == 1:
                flagZ = measZ.index(1)
            else:
                flagZ = measZ.index(0)
    else:  # Column flagZ in (0, 1, 2, 3) flagged
        if sum(measZ) in (1, 3):
            if sum(measZ) == 1:
                row = measZ.index(1)
            else:
                row = measZ.index(0)
            frameX[4 * row + flagZ] += 1  # Apply X correction
        elif sum(measZ) == 2:
            if measZ in ([0, 0, 1, 1], [1, 1, 0, 0]):
                frameX[[4 * 0 + flagZ, 4 * 1 + flagZ]] += 1  # XXII on flagged column. multiplication by 0 is for readability.
            else:
                return "reject"
        flagZ = -1
    return flagZ, measZ, frameX 