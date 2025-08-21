from typing import Optional
from ORM.models import AsyncORMBase  # your existing base classes


class Setting(AsyncORMBase):
    table_name = "settings"
    pk_field = "id"
