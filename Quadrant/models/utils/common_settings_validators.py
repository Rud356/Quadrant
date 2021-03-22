from typing import Callable, AnyStr, Any
from dataclasses import dataclass


@dataclass
class CommonSettingsValidator:
    key: AnyStr
    validator: Callable

    def validate(self, value: Any) -> bool:
        if self.validator(value):
            return True

        else:
            raise ValueError("Invalid setting value")


COMMON_SETTINGS = (
    CommonSettingsValidator("enable_sites_preview", lambda v: isinstance(v, bool)),
)
