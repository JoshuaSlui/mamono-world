from controllers.database import execute

async def upgrade():
    # Step 1: Rename current `id` to `user`
    await execute("""
        DROP TABLE IF EXISTS activity;
        ALTER TABLE votes DROP FOREIGN KEY IF EXISTS votes_ibfk_1;
        ALTER TABLE votes DROP FOREIGN KEY IF EXISTS votes_ibfk_2;
        ALTER TABLE responses DROP FOREIGN KEY IF EXISTS responses_ibfk_1;
        DROP TABLE IF EXISTS votes;
        DROP TABLE IF EXISTS responses;
        DROP TABLE IF EXISTS polls;
    
        ALTER TABLE levels
        CHANGE COLUMN id user BIGINT NOT NULL;
        
        ALTER TABLE birthdays DROP FOREIGN KEY IF EXISTS birthdays_ibfk_1;
        
        ALTER TABLE birthdays
        CHANGE COLUMN id user BIGINT NOT NULL;
    """)


    # Step 3: Drop old UNIQUE on `user` (update name if different)
    await execute("""
        ALTER TABLE levels
        DROP INDEX `PRIMARY`;

        ALTER TABLE birthdays
        DROP INDEX `PRIMARY`;
    """)

    # Step 2: Add new `id` as auto-incrementing PK
    await execute("""
        ALTER TABLE levels
        ADD COLUMN id BIGINT AUTO_INCREMENT PRIMARY KEY FIRST;
            
        ALTER TABLE birthdays
        ADD COLUMN id BIGINT AUTO_INCREMENT PRIMARY KEY FIRST;
    """)

    # Step 4: Add new UNIQUE on (user, guild)
    await execute("""
        ALTER TABLE levels
        ADD UNIQUE KEY unique_user_per_guild (user, guild);
        
        ALTER TABLE birthdays
        ADD UNIQUE KEY unique_user_per_guild (user, guild);
    """)

async def downgrade():
    # Step 1: Drop new UNIQUE constraint
    await execute("""
        ALTER TABLE levels
        DROP INDEX unique_user_per_guild;
        
        ALTER TABLE birthdays
        DROP INDEX unique_user_per_guild;
    """)

    # Step 2: Drop the new auto-incrementing `id`
    await execute("""
        ALTER TABLE levels
        DROP COLUMN id;
        
        ALTER TABLE birthdays
        DROP COLUMN id;
    """)

    # Step 3: Rename `user` back to `id`
    await execute("""
        ALTER TABLE levels
        CHANGE COLUMN user id BIGINT NOT NULL;
        
        ALTER TABLE birthdays
        CHANGE COLUMN user id BIGINT NOT NULL;
    """)

    # Step 4: Restore original unique constraint
    await execute("""
        ALTER TABLE levels
        ADD UNIQUE KEY user (id);
        
        ALTER TABLE birthdays
        ADD UNIQUE KEY user (id);
    """)
