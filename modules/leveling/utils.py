import random
from typing import Tuple

from ORM import Level
from managers import settings, SettingsManager
from managers.settings.guild_settings import SettingKey
from controllers.utility import Config

config = Config()

async def process_leveling_for_message(message) -> Tuple[bool, str | None]:
    leveling_enabled = await settings.get(scope_type=SettingsManager.SCOPES_GUILD, scope_id=message.guild.id, setting_key=SettingKey.LEVEL_UP_ENABLED)
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

    if user.level >= 2 and not any(role.id == config.get("level_verification") for role in message.author.roles):
        guild = message.guild
        role = guild.get_role(config.get("level_verification"))
        await message.author.add_roles(role)

    return True, user.level