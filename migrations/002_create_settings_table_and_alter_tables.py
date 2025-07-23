from controllers.database import execute
from controllers.utility import Config
config = Config()

async def upgrade():
    await execute("""
        CREATE TABLE settings (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            entity_id BIGINT NOT NULL,
            setting VARCHAR(255) NOT NULL,
            value TEXT NOT NULL,
            entity_type ENUM('bot', 'guild', 'user') NOT NULL,
            UNIQUE KEY unique_setting_per_entity (setting, entity_id)
        );
    """)
    await execute("""
        ALTER TABLE birthdays
        ADD COLUMN guild BIGINT DEFAULT NULL,
        ADD CONSTRAINT fk_birthdays_guild
        FOREIGN KEY (guild) REFERENCES guilds(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE;
        
        ALTER TABLE levels
        ADD COLUMN guild BIGINT DEFAULT NULL,
        ADD CONSTRAINT fk_levels_guild
        FOREIGN KEY (guild) REFERENCES guilds(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE;
            
        UPDATE birthdays SET birthdays.guild = %s WHERE guild IS NULL;
        UPDATE levels SET levels.guild = %s WHERE guild IS NULL;
    """, [config.get("guild_id")[0], config.get("guild_id")[0]])

async def downgrade():
    await execute("""
        DROP TABLE IF EXISTS settings;
        ALTER TABLE birthdays DROP FOREIGN KEY fk_birthdays_guild;
        ALTER TABLE levels DROP FOREIGN KEY fk_levels_guild;
        ALTER TABLE birthdays DROP COLUMN IF EXISTS guild;
        ALTER TABLE levels DROP COLUMN IF EXISTS guild;
    """)
