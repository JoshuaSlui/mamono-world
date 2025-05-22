from controllers.database import execute


class AsyncORMBase:
    table_name = ""
    pk_field = "id"

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    async def all(cls):
        query = f"SELECT * FROM {cls.table_name}"
        rows = await execute(query)
        return [cls(**row) for row in rows]

    @classmethod
    async def get(cls, pk):
        query = f"SELECT * FROM {cls.table_name} WHERE {cls.pk_field} = %s"
        rows = await execute(query, [pk])
        if not rows:
            return None
        return cls(**rows[0])

    @classmethod
    async def get_or_create(cls, pk):
        instance = await cls.get(pk)
        if instance:
            return instance
        await execute(
            f"INSERT INTO {cls.table_name} ({cls.pk_field}) VALUES (%s) ON DUPLICATE KEY UPDATE {cls.pk_field}={cls.pk_field}",
            [pk],
        )
        return await cls.get(pk)

    async def save(self):
        columns = [k for k in self.__dict__.keys() if not k.startswith("_")]
        values = [getattr(self, col) for col in columns]

        placeholders = ", ".join(["%s"] * len(columns))
        column_list = ", ".join(columns)

        update_clause = ", ".join(
            f"{col} = VALUES({col})" for col in columns if col != self.pk_field
        )

        query = f"""
            INSERT INTO {self.table_name} ({column_list})
            VALUES ({placeholders})
            ON DUPLICATE KEY UPDATE {update_clause}
        """
        await execute(query, values)

    async def delete(self):
        await execute(
            f"DELETE FROM {self.table_name} WHERE {self.pk_field} = %s",
            [getattr(self, self.pk_field)],
        )
        return True
