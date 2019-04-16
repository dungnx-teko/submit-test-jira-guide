def simple_plus(a, b):
    if (not isinstance(a, int) or not isinstance(b, int)):
        raise TypeError
    return a + b


def simple_subtract(a, b):
    return a - b
