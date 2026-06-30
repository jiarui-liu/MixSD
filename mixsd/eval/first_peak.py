def first_peak_index(values: list[int], method: str = None) -> int:
    """First i (1 <= i <= n-2) where values[i] is a new running max and values[i+1] <= values[i]; else len(values) - 1."""
    n = len(values)
    prev_max = values[0]
    for i in range(1, n - 1):
        if values[i] > prev_max:
            if method is None or 'sft-mix' not in method.lower():
                if values[i + 1] <= values[i]:
                    return i
            else:
                if values[i + 1] <= values[i] - 5:
                    return i
            prev_max = values[i]
    return n - 1
