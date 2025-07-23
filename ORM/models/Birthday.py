from . import AsyncORMBase


class Birthday(AsyncORMBase):
    table_name = "birthdays"
    pk_field = "id"  # foreign key to user id
