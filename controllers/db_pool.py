import asyncio
import aiomysql
from controllers.utility import Config


class DBPool:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DBPool, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):  # Ensure pool is initialized only once
            self.pool = None
            self.initialized = False

    async def init_pool(self):
        if not self.initialized:
            config = Config()
            self.pool = await aiomysql.create_pool(
                host=config.get("db_host", "localhost"),
                port=config.get("db_port", 3306),
                user=config.get("db_username"),
                password=config.get("db_password"),
                db=config.get("database"),
                loop=asyncio.get_event_loop(),
                autocommit=True,
                maxsize=10,  # Adjust the pool size as needed
            )
            self.initialized = True

    async def close_pool(self):
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            self.pool = None
            self.initialized = False

    def get_pool(self):
        return self.pool


# Instantiate and export a single instance
db_pool = DBPool()
