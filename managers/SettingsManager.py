from enum import Enum
from typing import Any, Type

from managers.settings.guild_settings import SettingKey


class Scopes(Enum):
    BOT = "bot"
    GUILD = "guild"
    USER = "user"


class SettingsManager:
    def __init__(self, model_cls, schema_enum):
        self.model_cls = model_cls
        self.schema = schema_enum  # e.g., SettingKey
        self._cache = {}  # {scope_type: {scope_id: {setting_key: value}}}

    SCOPES_BOT = Scopes.BOT
    SCOPES_GUILD = Scopes.GUILD
    SCOPES_USER = Scopes.USER

    async def get(self, scope_type: Scopes, scope_id: int, setting_key: SettingKey) -> Any:
        # --- check cache ---
        scope_cache = self._cache.setdefault(scope_type, {})
        id_cache = scope_cache.setdefault(scope_id, {})
        if setting_key.name in id_cache:
            return id_cache[setting_key.name]

        # --- fetch from DB ---
        key_name = setting_key.name.lower()
        setting = await self.model_cls.objects.get(
            scope_type=scope_type.value,
            scope_id=scope_id,
            setting_key=key_name
        )
        if setting is None:
            value = setting_key.value.default
        else:
            value = self._deserialize(setting.value, setting_key.value.value_type)

        # --- store in cache ---
        id_cache[setting_key.name] = value
        return value

    async def set(self, scope_type: Scopes, scope_id: int, setting_key: SettingKey, value: Any = None) -> None:
        if value is None:
            value = setting_key.value.default

        if not isinstance(value, setting_key.value.value_type):
            raise TypeError(f"Expected value of type {setting_key.value.value_type} for {setting_key.name}")

        key_name = setting_key.name.lower()
        value_str = self._serialize(value)

        setting = await self.model_cls.objects.get(
            scope_type=scope_type.value,
            scope_id=scope_id,
            setting_key=key_name
        )
        if setting is None:
            setting = self.model_cls(
                scope_type=scope_type.value,
                scope_id=scope_id,
                setting_key=key_name,
                value=value_str
            )
        else:
            setting.value = value_str

        await setting.save()

        # --- update cache ---
        scope_cache = self._cache.setdefault(scope_type, {})
        id_cache = scope_cache.setdefault(scope_id, {})
        id_cache[setting_key.name] = value

    def invalidate_cache(self, scope_type: Scopes, scope_id: int):
        if scope_type in self._cache:
            self._cache[scope_type].pop(scope_id, None)

    @staticmethod
    def _serialize(value: Any) -> str:
        import json
        if isinstance(value, (dict, list)):
            return json.dumps(value)
        return str(value)

    @staticmethod
    def _deserialize(raw_value: str, value_type: Type) -> Any:
        import json
        if value_type == bool:
            return raw_value.lower() in ("1", "true", "yes", "on")
        if value_type == int:
            return int(raw_value)
        if value_type == float:
            return float(raw_value)
        if value_type in (dict, list):
            return json.loads(raw_value)
        return raw_value
