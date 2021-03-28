from typing import Callable, AnyStr, Any
from dataclasses import dataclass


@dataclass
class CommonSettingsValidator:
    key: AnyStr
    default: Any
    validator: Callable

    def validate(self, value: Any) -> bool:
        if self.validator(value):
            return True

        else:
            raise ValueError("Invalid setting value")


COMMON_SETTINGS = (
    CommonSettingsValidator("enable_sites_preview", False, lambda v: isinstance(v, bool)),
)
DEFAULT_COMMON_SETTINGS_DICT = {i.key: i.default for i in COMMON_SETTINGS}

