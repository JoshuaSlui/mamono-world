import asyncio
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import discord
from discord.ext import tasks

from ORM.models.User import User
from ORM.models.Birthday import Birthday
from controllers.utility import Config


async def check_user_birthday(user):
    birthday = await Birthday.get(user.id)
    if not birthday:
        return

    today = datetime.now(ZoneInfo("America/New_York")).date()
    if birthday.date.day == today.day and birthday.date.month == today.month:
        return True


async def wait_until_midnight_est():
    now = datetime.now(ZoneInfo("America/New_York"))
    tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    delta = (tomorrow - now).total_seconds()
    print(f"⏱ Waiting {int(delta)} seconds until midnight EST/EDT...")
    await asyncio.sleep(delta)

@tasks.loop(hours=24)
async def birthday_check_loop(bot: discord.Bot, channel: discord.TextChannel, guild: discord.Guild):
    print("🎂 Running birthday check loop...")
    users = await User.all()
    for user in users:
        try:
            is_birthday = await check_user_birthday(user, bot)
            if is_birthday:
                user = guild.get_member(user.id)
                embed = discord.Embed()
                embed.title = "🎉 Happy Birthday!"
                embed.description = f"Happy birthday to {user.display_name}!"
                embed.set_thumbnail(url=user.avatar.url)
                await channel.send(f"{user.mention}", embed=embed)

        except Exception as e:
            print(f"⚠️ Error checking user {user.id}: {e}")


async def start_birthday_tasks(bot: discord.Bot):
    await wait_until_midnight_est()
    config = Config()
    guild = bot.get_guild(config.get("guild_id"))
    channel = guild.get_channel(config.get("birthday_channel"))
    birthday_check_loop.start(bot, channel, guild)
