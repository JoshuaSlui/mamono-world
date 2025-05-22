from ORM.models.Birthday import Birthday
from ORM.models.baseORM import AsyncORMBase


class User(AsyncORMBase):
    table_name = "users"
    pk_field = "id"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)