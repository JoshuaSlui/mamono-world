from enum import Enum
from dataclasses import dataclass
from typing import Any, Type

@dataclass
class SettingDefinition:
    default: Any
    value_type: Type
    description: str

class SettingKey(Enum):
    LEVEL_UP_MESSAGE = SettingDefinition(
        default="Congratulations {user.mention}, you leveled up to level {level}!",
        value_type=str,
        description="Message sent when a user levels up."
    )
    LEVEL_UP_ENABLED = SettingDefinition(
        default=True,
        value_type=bool,
        description="Enable or disable the leveling module"
    )
