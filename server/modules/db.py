import sqlite3
from modules.console import console_base

class sql_queries:
    __slots__ = 'conn', 'cur'
    def __init__(self, path="./modules/files/data.db"):
        self.conn = sqlite3.connect(path)
        self.cur = self.conn.cursor()

    def save(self, statement):
        self.cur.execute(statement)
        try: self.conn.commit()
        except: self.conn.rollback()

    def fetch(self, statement):
        self.cur.execute(statement)
        return self.cur.fetchone()

    def authorize(self, login, password):
        login_data = f"""
        SELECT pwd FROM users
        WHERE login = '{login}'
        """
        if password in self.fetch(login_data):
            get_data = f"""
            SELECT id, nick, avatar, friends, blocked, status
            FROM users
            WHERE login = '{login}'
            """
            return self.fetch(get_data)
        return None