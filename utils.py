from typing import List, Any

def exclude_keys(dictionary: dict, exclude_keys: List[Any]):
    for key in exclude_keys:
        dictionary.pop(key, None)
