from datetime import datetime

class InitialMigration:
    version = '001'
    
    def up(self):
        return [
            """
            CREATE TABLE users (
                id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
            """,
            """
            CREATE TABLE lists (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                user_id TEXT,
                created_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """
        ]
