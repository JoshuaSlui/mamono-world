from controllers.database import execute
from controllers.db_pool import db_pool
from controllers.utility import Config

from discord import Intents, Status, Activity, ActivityType, Bot, NoEntryPointError

from tasks import start_birthday_tasks

intents = Intents(messages=True, guilds=True, members=True, message_content=True)

bot = Bot(
    intents=intents,
    status=Status.online,
    activity=Activity(type=ActivityType.streaming, name="Starting..."),
    debug_guilds=[1189254335129976862],
)


@bot.listen()
async def on_connect() -> None:
    print("Connecting to discord...")
    await db_pool.init_pool()
    await execute(
        """
    CREATE TABLE IF NOT EXISTS users (
        id BIGINT PRIMARY KEY,
        is_superuser BOOLEAN DEFAULT FALSE,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS birthdays (
        id BIGINT PRIMARY KEY,
        date DATE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE
    );
    """
    )
    config.load_extensions(bot, exclude=["modals.py", "utility.py"])

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


config = Config()
bot.run(config.get("bot_token"))
