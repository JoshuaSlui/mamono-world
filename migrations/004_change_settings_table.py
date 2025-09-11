from controllers.database import execute

async def upgrade():
    await execute("DROP TABLE IF EXISTS settings;")

    await execute("""
        CREATE TABLE settings (
            id INT PRIMARY KEY AUTO_INCREMENT,
            scope_type ENUM('bot', 'guild', 'user') NOT NULL,
            scope_id BIGINT NOT NULL DEFAULT 0,
            setting_key VARCHAR(255) NOT NULL,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY unique_scope_key (scope_type, scope_id, setting_key)
        );
    """)

async def downgrade():
    # TODO: Write downgrade logic here
    await execute("DROP TABLE IF EXISTS settings;")

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

