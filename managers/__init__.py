from managers.SettingsManager import SettingsManager
from managers.settings.guild_settings import SettingKey
from ORM import Setting

settings = SettingsManager(Setting, SettingKey)

__all__ = [settings, SettingsManager, SettingKey]