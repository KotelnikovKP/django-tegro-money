from decimal import Decimal


def ftod(value, precision=15):
    """
        The function of converting the input value to Decimal with a given precision
    """
    if value is None:
        value = 0.00
    return Decimal(value).quantize(Decimal(10) ** -precision)
