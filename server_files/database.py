import sqlite3

#? adaptor class for both virtual and real db
class database:
    def __init__(self, path, virtual=True):
        self.con = sqlite3.connect(path)
        self.c = self.con.cursor()

    @staticmethod
    def check_integrity(con, c):
        pass