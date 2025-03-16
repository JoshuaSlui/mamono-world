from controllers.database import execute
from controllers.db_pool import db_pool
from controllers.utility import config

from discord import Intents, Status, Activity, ActivityType, Bot

intents = Intents(messages=True, guilds=True, members=True, message_content=True)

bot = Bot(intents=intents, status=Status.online, activity=Activity(type=ActivityType.streaming, name="Starting..."), debug_guilds=[1189254335129976862])

@bot.listen()
async def on_connect() -> None:
    print('Connecting to discord...')
    await db_pool.init_pool()
    await execute("""
    CREATE TABLE IF NOT EXISTS polls (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description VARCHAR(500),
    channel BIGINT NOT NULL,
    message BIGINT NOT NULL,
    closing_date BIGINT,
    author BIGINT NOT NULL,
    voting_cap INT,
    votes_per_user INT,
    status varchar(255) NOT NULL DEFAULT 'open')
    """)
    await execute("""
    CREATE TABLE IF NOT EXISTS responses (
        id INT AUTO_INCREMENT PRIMARY KEY,
        author BIGINT NOT NULL,
        description VARCHAR(128) NOT NULL,
        status VARCHAR(255) NOT NULL DEFAULT 'pending',
        poll INT NOT NULL,
        FOREIGN KEY (poll) REFERENCES polls (id) ON DELETE CASCADE
    )
    """)

    await execute("""
    CREATE TABLE IF NOT EXISTS votes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        author BIGINT NOT NULL,
        poll INT NOT NULL,
        response INT NOT NULL,
        FOREIGN KEY (poll) REFERENCES polls (id) ON DELETE CASCADE,
        FOREIGN KEY (response) REFERENCES responses (id) ON DELETE CASCADE
    )
    """)
    await execute("""
    CREATE TABLE IF NOT exists activity (
        id INT AUTO_INCREMENT PRIMARY KEY,
        author_name VARCHAR(255) NOT NULL,
        author_id BIGINT NOT NULL,
        date TEXT NOT NULL
    )
    """)
    bot.load_extensions("modules", recursive=True)

@bot.listen()
async def on_reconnect() -> None:
    print('Reconnecting to discord...')

@bot.listen()
async def on_ready() -> None:
    print(f'Authenticating as {bot.user}')
    print(f'------------------{len(str(bot.user)) * '-'}')
    await bot.change_presence(activity=Activity(type=ActivityType.streaming, name="Watching Mamono"))
    print(f'Authenticated with modules:\n{"\n".join(bot.extensions).replace('.', '/')}')

@bot.listen()
async def on_disconnect() -> None:
    print('Disconnecting from discord...')
    await db_pool.close_pool()
    await bot.close()

@bot.event
async def on_message(message):
    if message.author.id == bot.user.id:
        return

    await execute("INSERT INTO activity (author_name, author_id, date) VALUES (%s, %s, %s)", [message.author.name, message.author.id, message.created_at])


bot.run(config('bot_token'))