from typing import TypeVar, Generic, Type, List, Optional, Any, Tuple
from controllers.database import execute

T = TypeVar("T", bound="AsyncORMBase")


class QuerySet(Generic[T]):
    def __init__(self, model_cls: Type[T]):
        self.model_cls = model_cls
        self._filters: List[str] = []
        self._params: List[Any] = []

    def filter(self: "QuerySet[T]", **kwargs: Any) -> "QuerySet[T]":
        for key, value in kwargs.items():
            self._filters.append(f"{key} = %s")
            self._params.append(value)
        return self

    def __await__(self):
        # This makes it so you can `await User.objects.filter(...)`
        return self.all().__await__()

    async def all(self) -> List[T]:
        query = f"SELECT * FROM {self.model_cls.table_name}"
        if self._filters:
            query += " WHERE " + " AND ".join(self._filters)
        rows = await execute(query, self._params)
        return [self.model_cls(**row) for row in rows]

    async def get(self, **kwargs: Any) -> Optional[T]:
        # noinspection PyAsyncCall
        self.filter(**kwargs)  # PyCharm believes filter is async because of __await__, but it isn't
        results = await self.all()
        if not results:
            return None
        if len(results) > 1:
            raise Exception("Multiple objects returned from get()")
        return results[0]

    async def get_or_create(self, **kwargs: Any) -> Tuple[T, bool]:
        instance = await self.get(**kwargs)
        if instance:
            return instance, False

        columns = list(kwargs.keys())
        values = list(kwargs.values())

        col_str = ", ".join(columns)
        placeholders = ", ".join(["%s"] * len(values))

        query = f"""
            INSERT INTO {self.model_cls.table_name} ({col_str})
            VALUES ({placeholders})
            ON DUPLICATE KEY UPDATE {self.model_cls.pk_field} = {self.model_cls.pk_field}
        """

        await execute(query, values)
        instance = await self.get(**kwargs)
        return instance, True


class Manager(Generic[T]):
    def __get__(self, instance, owner) -> "QuerySet[T]":
        return QuerySet(owner)


class AsyncORMBase:
    table_name: str = ""
    pk_field: str = "id"

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    objects = Manager()

    async def save(self) -> None:
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

    async def delete(self) -> bool:
        await execute(
            f"DELETE FROM {self.table_name} WHERE {self.pk_field} = %s",
            [getattr(self, self.pk_field)],
        )
        return True
