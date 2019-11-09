import sqlite3
import asyncio

class sql_queries:
    def __init__(self, loop, path="/modules/files/data.db"):
        self.loop = loop
        self.conn = sqlite3.connect(path)
