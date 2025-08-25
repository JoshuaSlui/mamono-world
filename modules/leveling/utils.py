import random
import discord
import re
from typing import Tuple

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

async def process_member_join(member: discord.Member) -> tuple[bool, None] | tuple[
    bool, dict[str, discord.TextChannel | discord.Embed]]:
    guild = member.guild
    join_logs_enabled = await settings_manager.get(scope_type=SettingsManager.SCOPES_GUILD, scope_id=guild.id, setting_key=SettingKey.LOGS_JOIN_ENABLED)
    if not join_logs_enabled:
        return False, None

    join_logs_channel = await settings_manager.get(scope_type=SettingsManager.SCOPES_GUILD, scope_id=guild.id,setting_key=SettingKey.LOGS_JOIN_CHANNEL_ID)
    join_logs_channel = guild.get_channel(join_logs_channel) if join_logs_channel else None
    if not join_logs_channel:
        return False, None

    join_logs_message = await settings_manager.get(scope_type=SettingsManager.SCOPES_GUILD, scope_id=guild.id, setting_key=SettingKey.LOGS_JOIN_MESSAGE)

    embed = discord.Embed()
    embed.set_author(name=f"{member.display_name} joined the server", icon_url=guild.icon.url)
    embed.thumbnail = member.avatar.url
    embed.description = await message_params_processor(join_logs_message, user=member, guild=guild)
    embed.colour = member.colour

    return True, {"channel": join_logs_channel, "embed": embed}


async def message_params_processor(
    message: str,
    user: discord.User | discord.Member = None,
    guild: discord.Guild = None,
) -> str:
    """
    Replaces whitelisted placeholders for any supported object in the message string.
    Placeholders look like {user.name}, {guild.id}, etc.
    """

    obj_map = {
        "user": user,
        "guild": guild,
    }

    def replace(match: re.Match) -> str:
        obj_type = match.group(1)
        attr = match.group(2)
        obj = obj_map.get(obj_type)
        if not obj:
            return match.group(0)  # leave placeholder intact
        return str(getattr(obj, attr, match.group(0)))

    return settings.PARSER_PATTERN.sub(replace, message)
