def compare_aligned_lines(line_start, line_compare, consider_spaces=True):
    matches = []
    compared_elements = 0

    for char_start, char_compare in zip(line_start, line_compare):
        # Match!
        if char_start == char_compare and char_start != "|":
            # False match, just two spaces aligned
            if char_start == " ":
                matches.append(" ")
            else:
                matches.append(1)
                compared_elements += 1

        # Mismatch but between a separator ("|" or "-") and a space
        elif char_start in "|-" and char_compare == " ":
            matches.append(" ")
            if consider_spaces:
                compared_elements += 0.2

        # Mismatch: note vs. "|", "-", or space
        elif char_compare in "|- ":
            matches.append(" ")
            compared_elements += 1

        # Mismatch: interpretation difference (h vs. b)
        elif (char_start == "h" and char_compare == "b") or (char_start == "b" and char_compare == "h"):
            matches.append(0.5)
            compared_elements += 1

        else:
            matches.append(0)
            compared_elements += 1

    similarity_score = sum_numeric_elements(matches) / compared_elements if compared_elements > 0 else 0
    return similarity_score, matches

def compare_aligned_lines_intervals(line_start, line_compare, direction_start, direction_compare, consider_spaces=True):
    matches = []
    compared_elements = 0
    start_note_count = 0
    compare_note_count = 0

    for char_n, (char_start, char_compare) in enumerate(zip(line_start, line_compare)):
        dir_start = direction_start[start_note_count] if start_note_count < len(direction_start) else ""
        dir_compare = direction_compare[compare_note_count] if compare_note_count < len(direction_compare) else ""

        # Match!
        if char_start == char_compare and char_start != "|" and dir_start == dir_compare:
            # False match, just two spaces aligned
            if char_start == " ":
                matches.append(" ")

            # Actual match
            else:
                matches.append(1)
                compared_elements += 1
            if char_start.isdigit():
                start_note_count += 1
            if char_compare.isdigit():
                compare_note_count += 1

        # Mismatch: separation symbol ("|" or "-") vs. space
        elif (char_start in "|-" and char_compare == " "):
            matches.append(" ")
            if consider_spaces:
                compared_elements += 0.5

        # Mismatch: note against "|", "-", or space
        elif char_compare in "|- ":
            matches.append(" ")
            compared_elements += 1

            if char_start.isdigit():
                start_note_count += 1

        # Mismatch: interpretation difference (1 vs. 2, but same direction)
        elif ((char_start == "1" and char_compare == "2") or (
                char_start == "2" and char_compare == "1")) and dir_start == dir_compare:
            matches.append(0.5)
            compared_elements += 1
            start_note_count += 1
            compare_note_count += 1

        else:
            matches.append(0)
            compared_elements += 1
            if char_start.isdigit():
                start_note_count += 1
            if char_compare.isdigit():
                compare_note_count += 1

    matches.insert(0, 1)  # Equivalent to `array_unshift($matches, 1)`
    compared_elements += 1
    similarity_score = sum_numeric_elements(matches) / compared_elements if compared_elements > 0 else 0
    print("matches")
    print(matches)
    print("compared_elements")
    print(compared_elements)
    print("compared_elements_ar")
    print(compared_elements_ar)
    return similarity_score, matches

def sum_numeric_elements(arr):
    """Sums only numeric elements in a list."""
    return sum(el for el in arr if isinstance(el, (int, float)))

def trim_sequences(seq1, seq2):
    """Trims leading and trailing '|' characters from aligned sequences."""

    first_non_gap_index = 0
    last_non_gap_index = len(seq1) - 1

    # Find the first non-'|' character
    if seq1[0] == "|":
        for i, char in enumerate(seq1):
            if char != "|":
                first_non_gap_index = i
                break

    # Find the last non-'|' character
    if seq1[-1] == "|":
        for i in range(len(seq1) - 1, -1, -1):
            if seq1[i] != "|":
                last_non_gap_index = i
                break

    # Return trimmed sequences
    return seq1[first_non_gap_index:last_non_gap_index + 1], seq2[first_non_gap_index:last_non_gap_index + 1]

