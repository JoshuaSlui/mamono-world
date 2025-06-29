import discord

from . import AsyncORMBase
from controllers.database import execute

class Guild(AsyncORMBase):
    table_name = "guilds"
    pk_field = "id"

    @classmethod
    async def create_or_update(cls, guild: discord.Guild):
        await execute(
            """
            INSERT INTO guilds (id, owner_id, name) VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE name = VALUES(name), owner_id = VALUES(owner_id)
        """,
            [guild.id, guild.owner_id, guild.name],
        )
        return await cls.get(guild.id)