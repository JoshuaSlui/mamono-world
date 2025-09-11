from controllers.database import execute
from main import config


async def upgrade():
    await execute("""
        CREATE TABLE IF NOT EXISTS users (
            id BIGINT PRIMARY KEY,
            is_superuser BOOLEAN DEFAULT FALSE,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );
    """)

    await execute("""
        CREATE TABLE IF NOT EXISTS birthdays (
            id BIGINT PRIMARY KEY,
            date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );
    """)

    await execute("""
        CREATE TABLE IF NOT EXISTS levels (
            id BIGINT PRIMARY KEY,
            level INT DEFAULT 0,
            xp INT DEFAULT 0,
            last_message TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );
    """)

    await execute("""
        CREATE TABLE IF NOT EXISTS guilds (
            id BIGINT PRIMARY KEY,
            owner_id BIGINT NOT NULL,
            name VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        );
            
        INSERT INTO guilds (id, owner_id, name) VALUES (%s, %s, 'Initial server') ON DUPLICATE KEY UPDATE id = id;
    """, [
        config.get('guild_id')[0],  # Replace with your actual guild ID
        1  # You can change this with the eval command later
    ])


async def downgrade():
    await execute("DROP TABLE IF EXISTS guilds;")
    await execute("DROP TABLE IF EXISTS levels;")
    await execute("DROP TABLE IF EXISTS birthdays;")
    await execute("DROP TABLE IF EXISTS users;")
