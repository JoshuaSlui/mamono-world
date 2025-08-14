from enum import Enum
from typing import Any, Type

from managers.settings.guild_settings import SettingKey

class Scopes(Enum):
    GLOBAL = "global"
    GUILD = "guild"
    USER = "user"

class SettingsManager:
    def __init__(self, model_cls, schema_enum):
        self.model_cls = model_cls
        self.schema = schema_enum  # e.g., SettingKey

    SCOPES_GLOBAL = Scopes.GLOBAL
    SCOPES_GUILD = Scopes.GUILD
    SCOPES_USER = Scopes.USER

    async def get(self, scope_type: str, scope_id: int, setting_key: SettingKey) -> Any:
        key_name = setting_key.name.lower()
        setting = await self.model_cls.objects.get(
            scope_type=scope_type,
            scope_id=scope_id,
            setting_key=key_name
        )
        if setting is None:
            default_value = setting_key.value.default
            await self.set(scope_type, scope_id, setting_key, default_value)
            return default_value

        # Deserialize and type-check
        raw_value = setting.value
        value = self._deserialize(raw_value, setting_key.value.value_type)
        return value

    async def set(self, scope_type: str, scope_id: int, setting_key: SettingKey, value: Any) -> None:
        if not isinstance(value, setting_key.value.value_type):
            raise TypeError(f"Expected value of type {setting_key.value.value_type} for {setting_key.name}")
        if not isinstance(scope_type, Scopes):
            raise ValueError(f"Invalid scope type: {scope_type}. Must be one of {list(Scopes)}")

        key_name = setting_key.name.lower()
        value_str = self._serialize(value)

        print(self.model_cls.objects, self.model_cls)

        setting = await self.model_cls.objects.get(
            scope_type=scope_type,
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

    def _serialize(self, value: Any) -> str:
        import json
        if isinstance(value, (dict, list)):
            return json.dumps(value)
        return str(value)

    def _deserialize(self, raw_value: str, value_type: Type) -> Any:
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
