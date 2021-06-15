import numpy as np
import numba


@numba.njit(nogil=True)
def equal(a1, a2):
    acc = 0
    for y in range(a1.shape[0]):
        for x in range(a1.shape[1]):
            for i in range(a1.shape[2]):
                acc = np.abs(a1[y, x, i] - a2[y, x, i])
                if acc:
                    return (False, y, x, i)
    return (True, y, x, i)

@numba.njit
def find_match(needle, haystack):
    assert len(needle.shape) == 3
    assert len(haystack.shape) == 3
    for i in range(2):
        assert needle.shape[i] <= haystack.shape[i]
    assert needle.shape[-1] == haystack.shape[-1]
    matches = []
    killers = set()
    for y_shift in range(haystack.shape[0] - needle.shape[0]):
        for x_shift in range(haystack.shape[1] - needle.shape[1]):
            killed = False
            for killer in killers:
                y, x, i = killer
                killed = haystack[y_shift + y, x_shift + x, i] != needle[y, x, i]
                if killed:
                    break
            if killed:
                continue
            found, y, x, i = equal(haystack[y_shift:y_shift+needle.shape[0], x_shift:x_shift+needle.shape[1]], needle)
            if found:
                matches.append((y_shift, x_shift))
            else:
                killers.add((y, x, i))
    return matches
