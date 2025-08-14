import discord

from ORM import Level, Guild
from controllers.db_pool import db_pool
from controllers.utility import Config
import random

from discord import Intents, Status, Activity, ActivityType, Bot

from managers import settings, SettingsManager
from managers.settings.guild_settings import SettingKey
from modules.leveling.utils import process_leveling_for_message
from tasks import start_birthday_tasks

intents = Intents(messages=True, guilds=True, members=True, message_content=True)
config = Config()

bot = Bot(
    intents=intents,
    status=Status.online,
    activity=Activity(type=ActivityType.streaming, name="Starting..."),
    debug_guilds=config.get("guild_id") if config.get("debug") else None,  # Replace with your debug guild ID
    allowed_mentions=discord.AllowedMentions(
        everyone=False,  # Disable @everyone mentions
        users=True,  # Enable @user mentions
        roles=True,  # Disable @role mentions
    )
)


@bot.listen()
async def on_connect() -> None:
    print("Connecting to discord...")
    await db_pool.init_pool()
    config.load_extensions(bot)

@bot.listen()
async def on_reconnect() -> None:
    print("Reconnecting to discord...")


@bot.listen()
async def on_ready() -> None:
    print(f"Authenticating as {bot.user}")
    print(f"------------------{len(str(bot.user)) * '-'}")
    await bot.change_presence(
        activity=Activity(type=ActivityType.streaming, name="Watching Mamono")
    )
    print(f'Authenticated with modules:\n{"\n".join(bot.extensions).replace('.', '/')}')
    await start_birthday_tasks(bot)


@bot.listen()
async def on_disconnect() -> None:
    print("Disconnecting from discord...")
    await db_pool.close_pool()
    await bot.close()

@bot.listen()
async def on_message(message):
    if message.author.bot:
        return

    leveled_up, level = await process_leveling_for_message(message)

    if not leveled_up:
        return

    leveling_message = await settings.get(scope_type=SettingsManager.SCOPES_GUILD, scope_id=message.guild.id, setting_key=SettingKey.LEVEL_UP_MESSAGE)
    await message.channel.send(leveling_message.format(user=message.author, level=level))

@bot.listen()
async def on_member_join(member):
    embed = discord.Embed()
    embed.set_author(
        name="- Mamono Management",
        icon_url="https://cdn.discordapp.com/attachments/1369382913241649313/1371960397598294036/shadesilly.png?ex=68343270&is=6832e0f0&hm=1c376876f6f530116c5d1628de1a417c9b304ae2fcf159f172cc232333af18bd&"
    )
    embed.title = f"Welcome {member.display_name}!"
    embed.description = """
        Welcome to Mamono World! Please verify in <id:customize>!
        Afterwards, please introduce yourself and feel free to enjoy our community!!!!
    """
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.colour = discord.Colour.purple()
    channel = bot.get_channel(config.get("joins_channel"))
    await channel.send(embed=embed)

@bot.listen()
async def on_guild_join(guild: discord.Guild):
    await Guild.create_or_update(guild)
    print(f"Joined guild: {guild.name} (ID: {guild.id})")

if __name__ == "__main__":
    bot.run(config.get("bot_token"))
