import sqlite3

class SQLiteConnection:

    def __init__(self) -> None:
        self.connection = None
        self.cursor = None

    def connect(self, connection_string: str) -> None:
        self.connection = sqlite3.connect(database=connection_string)
        self.cursor = self.connection.cursor()

    def query(self, query_string: str, *kwargs) -> None:
        self.cursor.execute(query_string, kwargs)

    def disconnect(self) -> None:
        if self.cursor is not None:
            # self.cursor.close()
            self.cursor = None
        if self.connection is not None:
            self.connection.close()
            self.connection = None
