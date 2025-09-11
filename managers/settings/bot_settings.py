from enum import Enum

from managers.settings.definitions import SettingDefinition


class SettingKey(Enum):
    EXCEPTION_LOG = SettingDefinition(
        default=None,
        value_type=dict,
        description="Channel and guild ID where exception logs will be sent"
    ) # Example: {"guild": 112233445566778899, "channel": 112233445566778899}