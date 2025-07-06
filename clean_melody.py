import re

def clean_melody(s, ignore_plicas=True):
    s = s.replace('_h', 'b')
    s = s.replace('+a', 'u')
    s = s.replace('+b', 'p')
    s = s.replace('+h', 'q')
    s = s.replace('+c', 'r')
    s = s.replace('+d', 's')
    s = s.replace("*G", "J")

    # Remove specific characters
    for char in ["%", "/", "-", "[", "]", "'", "&039;"]:
        s = s.replace(char, "")

    # Remove patterns matching the regex
    s = re.sub(r"[CFGDA]\d ?|[bh]} ?", "", s, flags=re.IGNORECASE)

    # If ignoring plicas, remove parentheses
    if ignore_plicas:
        s = s.replace("(", "").replace(")", "")

    return s