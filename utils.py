from typing import Any, List


def exclude_keys(dictionary: dict, exclude_keys: List[Any]):
    for key in exclude_keys:
        dictionary.pop(key, None)


def string_strips(string: str) -> str:
    return string.strip(' ').strip("\n").strip("\t")
