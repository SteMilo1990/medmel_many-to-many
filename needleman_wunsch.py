import numpy as np
from numba import njit

@njit(cache=True)
def needleman_wunsch(seq1, seq2, match=1, mismatch=-1, gap=-1):
    nx, ny = len(seq1), len(seq2)

    # Initialize scoring matrix with gap penalties
    F = np.zeros((nx + 1, ny + 1), dtype=np.int32)
    F[:, 0] = np.arange(0, (nx + 1) * gap, gap, dtype=np.int32)
    F[0, :] = np.arange(0, (ny + 1) * gap, gap, dtype=np.int32)

    # Fill the scoring matrix (vectorized)
    for i in range(1, nx + 1):
        for j in range(1, ny + 1):
            match_score = match if seq1[i - 1] == seq2[j - 1] else mismatch
            match_score += F[i - 1, j - 1]
            delete = F[i - 1, j] + gap
            insert = F[i, j - 1] + gap
            F[i, j] = max(match_score, delete, insert)

    # Traceback phase
    i, j = nx, ny
    aligned_seq1 = []
    aligned_seq2 = []

    while i > 0 or j > 0:
        current_score = F[i, j]
        if i > 0 and j > 0 and current_score == F[i - 1, j - 1] + (match if seq1[i - 1] == seq2[j - 1] else mismatch):
            aligned_seq1.append(seq1[i - 1])
            aligned_seq2.append(seq2[j - 1])
            i -= 1
            j -= 1
        elif i > 0 and current_score == F[i - 1, j] + gap:
            aligned_seq1.append(seq1[i - 1])
            aligned_seq2.append('-')
            i -= 1
        else:
            aligned_seq1.append('-')
            aligned_seq2.append(seq2[j - 1])
            j -= 1

    return ''.join(aligned_seq1[::-1]), ''.join(aligned_seq2[::-1])

def needleman_wunsch___SLOW(seq1, seq2, match=1, mismatch=-1, gap=-1):
    nx, ny = len(seq1), len(seq2)

    # Initialize scoring matrix
    F = np.zeros((nx + 1, ny + 1), dtype=int)

    # Initialize first row and column (gap penalties)
    F[:, 0] = np.arange(0, (nx + 1) * gap, gap)
    F[0, :] = np.arange(0, (ny + 1) * gap, gap)

    # Fill the scoring matrix
    for i in range(1, nx + 1):
        for j in range(1, ny + 1):
            match_score = F[i - 1, j - 1] + (match if seq1[i - 1] == seq2[j - 1] else mismatch)
            delete = F[i - 1, j] + gap
            insert = F[i, j - 1] + gap
            F[i, j] = max(match_score, delete, insert)

    # Traceback
    i, j = nx, ny
    aligned_seq1, aligned_seq2 = [], []

    while i > 0 or j > 0:
        current_score = F[i, j]

        if i > 0 and j > 0 and (current_score == F[i - 1, j - 1] + (match if seq1[i - 1] == seq2[j - 1] else mismatch)):
            aligned_seq1.append(seq1[i - 1])
            aligned_seq2.append(seq2[j - 1])
            i -= 1
            j -= 1
        elif i > 0 and current_score == F[i - 1, j] + gap:
            aligned_seq1.append(seq1[i - 1])
            aligned_seq2.append('-')
            i -= 1
        else:
            aligned_seq1.append('-')
            aligned_seq2.append(seq2[j - 1])
            j -= 1

    return aligned_seq1, aligned_seq2


def needleman_wunsch_____(x, y, match=1, mismatch=1, gap=1):
    nx = len(x)
    ny = len(y)

    # Initialize matrices
    F = np.zeros((nx + 1, ny + 1))  # Scoring matrix
    P = np.zeros((nx + 1, ny + 1))  # Traceback matrix

    # Fill first column (gap penalties)
    for i in range(1, nx + 1):
        F[i, 0] = -i * gap
        P[i, 0] = 2  # Up (gap in y)

    # Fill first row (gap penalties)
    for j in range(1, ny + 1):
        F[0, j] = -j * gap
        P[0, j] = 3  # Left (gap in x)

    # Fill matrices
    for i in range(1, nx + 1):
        for j in range(1, ny + 1):
            match_score = match if x[i - 1] == y[j - 1] else -mismatch
            choices = [
                F[i - 1, j - 1] + match_score,  # Diagonal (match/mismatch)
                F[i - 1, j] - gap,  # Up (gap in y)
                F[i, j - 1] - gap   # Left (gap in x)
            ]
            F[i, j] = max(choices)

            # Assign traceback directions: 1 = diagonal, 2 = up, 3 = left
            P[i, j] = choices.index(F[i, j]) + 1

    # Traceback
    i, j = nx, ny
    rx, ry = [], []

    while i > 0 or j > 0:
        if P[i, j] == 1:  # Diagonal
            rx.append(x[i - 1])
            ry.append(y[j - 1])
            i -= 1
            j -= 1
        elif P[i, j] == 2:  # Up
            rx.append(x[i - 1])
            ry.append('-')
            i -= 1
        elif P[i, j] == 3:  # Left
            rx.append('-')
            ry.append(y[j - 1])
            j -= 1

    # Reverse the sequences since we built them backwards
    return rx[::-1], ry[::-1]


# # Example usage:
# seq1 = "Gianna salta sul muro"
# seq2 = "Ho incontrato Gianna che saltava sui muri"
# seq1 = "a b cd edc fed"
# seq2 = "h aG ah aG G Gh d a b cd edc fed c ch ah 'h aG G F a ccd c ded c h ahcG G F Ga ah a a(G)'"

# start_time = time.time()
# # alignment1, alignment2, score = needleman_wunsch(seq1, seq2, match_score=1, mismatch_score=-5, gap_penalty=-14)
# # print(alignment1)
# # print(alignment2)
# # print("Alignment Score:", score)
# #
# res = nw(seq1, seq2, match=1, mismatch=9, gap=5)
# end_time = time.time()
# print(res)
# print(f"Tempo di esecuzione: {(end_time - start_time)} secondi ({(end_time - start_time)*60000/60} minuti)")