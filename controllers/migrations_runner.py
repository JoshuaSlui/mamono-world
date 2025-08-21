import os
import importlib.util
from controllers.database import execute
from controllers import setup_logger

logger = setup_logger()


async def apply_migrations():
    await execute("""
        CREATE TABLE IF NOT EXISTS migrations (
            name VARCHAR(255) PRIMARY KEY
        );
    """)
    applied_rows = await execute("SELECT name FROM migrations")
    applied = {row["name"] for row in applied_rows}

    migrations_dir = os.path.join(os.path.dirname(__file__), "..", "migrations")
    migration_files = sorted(f for f in os.listdir(migrations_dir) if f.endswith(".py"))

    for filename in migration_files:
        name = filename[:-3]
        if name in applied:
            continue

        filepath = os.path.join(migrations_dir, filename)
        spec = importlib.util.spec_from_file_location(name, filepath)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        logger.info(f"🔧 Applying migration: {name}")
        await mod.upgrade()
        await execute("INSERT INTO migrations (name) VALUES (%s)", (name,))


async def revert_migration(name: str):
    filepath = os.path.join(os.path.dirname(__file__), "..", "migrations", f"{name}.py")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Migration '{name}' not found.")

    spec = importlib.util.spec_from_file_location(name, filepath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    logger.warning(f"⏪ Reverting migration: {name}")
    await mod.downgrade()
    await execute("DELETE FROM migrations WHERE name = %s", (name,))