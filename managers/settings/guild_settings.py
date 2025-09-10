from enum import Enum

from managers.settings.definitions import SettingDefinition


class SettingKey(Enum):
    LEVEL_UP_MESSAGE = SettingDefinition(
        default="Congratulations {user.mention}, you leveled up to level {user.level}!",
        value_type=str,
        description="Message sent when a user levels up."
    )
    LEVEL_UP_ENABLED = SettingDefinition(
        default=True,
        value_type=bool,
        description="Enable or disable the leveling module"
    )
    LOGS_JOIN_ENABLED = SettingDefinition(
        default=False,
        value_type=bool,
        description="Enable or disable join logs"
    )
    LOGS_JOIN_CHANNEL_ID = SettingDefinition(
        default=None,
        value_type=int,
        description="Channel ID where join logs will be sent"
    )
    LOGS_JOIN_MESSAGE = SettingDefinition(
        default="Welcome {user.mention} to {guild.name}! Enjoy your stay!",
        value_type=str,
        description="Message sent when a user joins the server."
    )
