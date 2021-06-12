def file_size_caster(value: str) -> int:
    """
    Here's example of how you define sizes:
    1024 (by default its taken as bits size)
    100b (bytes)
    100k (kilobytes)
    10M (megabytes)
    1G (gigabytes)
    1T (terabytes)
    :param value:
    :return:
    """

    multipliers_table = {
        "": 1,
        "b": 8,
        "k": 8*1024,
        "M": 8*1024*1024,
        "G": 8*1024*1024*1024,
        "T": 8*1024*1024*1024*1024,
    }
    numbers, size_multiplier = value[:-1], value[-1]
    if not numbers.isdecimal():
        raise ValueError("Size variable must have only number part and 1 character representing a size multiplier")

    if size_multiplier.isdigit():
        size_multiplier = ""
        numbers = value

    multiplier = multipliers_table.get(size_multiplier, 1)
    return int(numbers)*multiplier
