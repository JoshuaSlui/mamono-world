from dataclasses import dataclass
from typing import Any, Type


@dataclass
class SettingDefinition:
    default: Any
    value_type: Type
    description: str