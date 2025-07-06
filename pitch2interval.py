def note2interval(note):
    mapping = {
        "J": 32, "A": 30, "B": 29, "H": 28, "C": 27, "D": 25,
        "E": 23, "F": 22, "G": 20, "a": 18, "b": 17, "h": 16,
        "c": 15, "d": 13, "e": 11, "f": 10, "g": 8, "u": 6,
        "p": 5, "q": 4, "r": 2
    }
    return mapping.get(note, None)


def notes_to_intervals(notes_input, consider_plica=False):
    notes_input = notes_input.rstrip()

    for char in [" '", "'", " &039;", "&039;", "_h"]:
        notes_input = notes_input.replace(char, "")
    notes_input = notes_input.replace("_h", "b")

    for pitch in ["C", "F"]:
        for i in range(1, 7):
            notes_input = notes_input.replace(f"{pitch}{i} ", "").replace(f"{pitch}{i}", "")

    notes_input = notes_input.replace("\n", "|")

    if not consider_plica:
        notes_input = notes_input.replace("(", "").replace(")", "")

    intervals_string = ""
    length = len(notes_input)

    i = 0
    while i < length - 1:
        interval_str = ""
        if notes_input[i] == "|":
            pass  # Skip barlines
        elif notes_input[i] == "(":
            pass  # Skip opening plica
        elif notes_input[i + 1] == ")":
            intervals_string += ")"
        else:
            first_note = note2interval(notes_input[i - 1]) if notes_input[i] == ")" else note2interval(notes_input[i])

            if notes_input[i + 1] in [" ", "|", "("]:
                second_note = note2interval(notes_input[i + 2])
                intervals_string += notes_input[i + 1]  # Keep separator
            elif notes_input[i + 1] != ")":
                second_note = note2interval(notes_input[i + 1])

            if first_note is not None and second_note is not None:
                interval = first_note - second_note
                interval_str = f"+{interval}" if interval > 0 else ("=0" if interval == 0 else str(interval))

        intervals_string += interval_str
        i += 1
    return intervals_string.strip()
