def validate_is_postgresql(v: str) -> bool:
    if 'postgresql://' in v:
        return True

    else:
        raise ValueError("Quadrant chat supports only postgresql")
