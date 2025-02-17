def convert_to_float(value):
    """
    Function that converts the decimal sparator of a numeric field that has a comma or dot to float
    If it cannot convert ir returns a NONE
    """
    try:
        return float(value.replace(',', '.'))
    except (ValueError, AttributeError):
        return None