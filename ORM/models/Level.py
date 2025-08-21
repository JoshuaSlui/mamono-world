from datetime import datetime
from ORM.models import AsyncORMBase


class Level(AsyncORMBase):
    table_name = "levels"
    pk_field = "id"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.xp = kwargs.get("xp", 0)
        self.level = kwargs.get("level", 0)
        self.last_message = kwargs.get("last_message")

    @staticmethod
    def xp_required(level: int) -> int:
        return int(100 * level ** 1.5)

    @staticmethod
    def total_xp_for_level(level: int) -> int:
        # Total XP required to reach a specific level
        return sum(Level.xp_required(lvl) for lvl in range(1, level + 1))

    @staticmethod
    def level_from_xp(xp: int) -> int:
        level = 1
        total_xp = 0
        while total_xp + Level.xp_required(level) <= xp:
            total_xp += Level.xp_required(level)
            level += 1
        return level

    async def add_xp(self, amount: int) -> bool:
        self.xp += amount
        new_level = self.level_from_xp(self.xp)
        leveled_up = new_level > self.level
        if leveled_up:
            self.level = new_level
        await self.save()
        return leveled_up

    async def can_gain_xp(self, cooldown_seconds=60) -> bool:
        now = datetime.now()
        if self.last_message and (now - self.last_message).total_seconds() < cooldown_seconds:
            return False
        self.last_message = now
        return True
