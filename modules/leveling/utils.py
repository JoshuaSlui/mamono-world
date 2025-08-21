import random
import discord
import re
from typing import Tuple, Any

import settings
from ORM import Level
from managers import settings_manager, SettingsManager
from managers.settings.guild_settings import SettingKey
from controllers.utility import Config

config = Config()


async def process_leveling_for_message(message) -> Tuple[bool, str | None]:
    leveling_enabled = await settings_manager.get(scope_type=SettingsManager.SCOPES_GUILD, scope_id=message.guild.id, setting_key=SettingKey.LEVEL_UP_ENABLED)
    if not leveling_enabled:
        return False, None

    user_id = message.author.id
    user, _ = await Level.objects.get_or_create(user=user_id, guild=message.guild.id)

    if not await user.can_gain_xp(cooldown_seconds=60):
        return False, None # User is on cooldown for gaining XP

    gained_xp = random.randint(10, 20)
    leveled_up = await user.add_xp(gained_xp)

    if not leveled_up:
        return False, None

    return True, user.level

# Build regex dynamically from the whitelist
USER_PARAM_PATTERN = re.compile(r"{user\.(" + "|".join(map(re.escape, settings.ALLOWED_USER_PARAMS)) + r")}")
GUILD_PARAM_PATTERN = re.compile(r"{guild\.(" + "|".join(map(re.escape, settings.ALLOWED_GUILD_PARAMS)) + r")}")


def message_params_processor(message: str, user: discord.User = None, guild: discord.Guild = None) -> str:
    """
    Replaces whitelisted placeholders for a user object in the message string.

    Supported placeholders:
    {user.mention}
    {user.name}
    {user.display_name}
    {user.id}
    {guild.name}
    {guild.id}
    """
    def replace_match(match: re.Match) -> str:
        attr = match.group(1)
        value = getattr(user, attr, None)
        if value is None and guild is not None:
            value = getattr(guild, attr, None)
        return str(value) if value is not None else match.group(0)

    user_parsed = USER_PARAM_PATTERN.sub(replace_match, message)
    guild_parsed = GUILD_PARAM_PATTERN.sub(replace_match, user_parsed)

    return guild_parsed
