from datetime import datetime

class AddIndexesMigration:
    version = '002'
    
    def up(self):
        return [
            """
            CREATE INDEX idx_users_email 
            ON users(email)
            """,
            """
            CREATE INDEX idx_lists_user_id 
            ON lists(user_id)
            """,
            """
            CREATE INDEX idx_items_list_id 
            ON items(list_id)
            """
        ]
