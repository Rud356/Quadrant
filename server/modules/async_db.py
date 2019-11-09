import sqlite3
import asyncio
from modules.console import console_base
class sql_queries:
    __slots__ = 'loop', 'conn', 'cur'
    def __init__(self, loop: asyncio.AbstractEventLoop, path="/modules/files/data.db"):
        self.loop = loop
        self.conn = sqlite3.connect(path)
        self.cur = self.conn.cursor()

    async def save(self, query) -> bool:
        try:
            self.loop.run_in_executor(self.cur.execute(query))
            self.conn.commit()
            return True
        except Exception as e:
            console_base.Error(e)
            return False

    async def fetch1_query(self, query):
        return self.loop.run_in_executor(None, lambda: self.cur.execute(query).fetchone())

    async def fetchall_query(self, query):
        return self.loop.run_in_executor(None, lambda: self.cur.execute(query).fetchall())

    async def authorize(self, login, password):
        pass