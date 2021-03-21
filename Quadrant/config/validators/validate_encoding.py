import codecs


def validate_encoding(value: str):
    try:
        codecs.lookup(value)

    except LookupError:
        raise ValueError("Invalid logs encoding")

    return True
