from . import AsyncORMBase


class User(AsyncORMBase):
    table_name = "users"
    pk_field = "id"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
