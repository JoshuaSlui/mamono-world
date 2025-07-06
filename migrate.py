import asyncio
import sys
import os
import re

from controllers.db_pool import db_pool
from controllers.migrations_runner import apply_migrations, revert_migration
from controllers.logger import setup_logger

logger = setup_logger()

MIGRATIONS_DIR = os.path.join(os.path.dirname(__file__), "migrations")

TEMPLATE = '''from controllers.database import execute

async def upgrade():
    # TODO: Write upgrade logic here
    pass

async def downgrade():
    # TODO: Write downgrade logic here
    pass
'''


def get_next_migration_number():
    files = [f for f in os.listdir(MIGRATIONS_DIR) if f.endswith(".py")]
    numbers = []

    for f in files:
        match = re.match(r"(\d+)_", f)
        if match:
            numbers.append(int(match.group(1)))

    return max(numbers, default=0) + 1


def slugify(name: str):
    return re.sub(r"[^\w]+", "_", name.strip().lower())


def create_migration(description: str):
    os.makedirs(MIGRATIONS_DIR, exist_ok=True)

    number = get_next_migration_number()
    slug = slugify(description)
    filename = f"{number:03d}_{slug}.py"
    filepath = os.path.join(MIGRATIONS_DIR, filename)

    with open(filepath, "w") as f:
        f.write(TEMPLATE)

    logger.info(f"📄 Created new migration: migrations/{filename}")


async def main():
    if len(sys.argv) < 2:
        logger.info("Usage:\n  python migrate.py upgrade\n  python migrate.py downgrade <name>\n  python migrate.py create <description>")
        return

    command = sys.argv[1]

    if command in ("upgrade", "downgrade"):
        await db_pool.init_pool()
        try:
            if command == "upgrade":
                await apply_migrations()
            elif command == "downgrade":
                if len(sys.argv) < 3:
                    logger.warning("Specify the migration name to downgrade (e.g. 002_add_column)")
                    return
                await revert_migration(sys.argv[2])
        finally:
            await db_pool.close_pool()

    elif command == "create":
        if len(sys.argv) < 3:
            logger.warning("Specify a description for the migration.")
            return
        description = " ".join(sys.argv[2:])
        create_migration(description)

    else:
        logger.error(f"Unknown command: {command}")


if __name__ == "__main__":
    asyncio.run(main())
