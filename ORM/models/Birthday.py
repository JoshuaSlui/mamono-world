from . import AsyncORMBase
from controllers.database import execute


class Birthday(AsyncORMBase):
    table_name = "birthdays"
    pk_field = "id"  # foreign key to user id

    @classmethod
    async def create_or_update(cls, user_id, date):
        await execute(
            """
            INSERT INTO birthdays (id, date) VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE date = VALUES(date), updated_at = CURRENT_TIMESTAMP
        """,
            [user_id, date],
        )
        return await cls.get(user_id)
