from datetime import datetime
from zoneinfo import ZoneInfo

from ORM.models.Birthday import Birthday


async def check_user_birthday(user):
    birthday = await Birthday.get(user.id)
    if not birthday:
        return

    today = datetime.now(ZoneInfo("America/New_York")).date()
    if birthday.date.day == today.day and birthday.date.month == today.month:
        return True