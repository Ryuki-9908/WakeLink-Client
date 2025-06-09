import sqlite3
from sqlite3 import OperationalError
from common.context import Context
from db.migrate import Migrator


class SQLiteManager:
    def __init__(self):
        context = Context(class_name=self.__class__.__name__)
        self.logger = context.logger

        # 設定ファイル読み込み
        self.db_path = context.config.DB_PATH
        self.migrations_dir = context.config.DB_MIGRATIONS_PATH
        self.conn = None

    def connect(self):
        """データベース接続"""
        if not self.conn:
            self.conn = sqlite3.connect(self.db_path)

    def close(self):
        """データベース接続終了"""
        if self.conn:
            self.conn.close()

    def execute_query(self, query, params=None):
        """クエリ実行"""
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute(query, params or ())
        self.conn.commit()
        return cursor.fetchall()

    def execute_update(self, query, params=None):
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute(query, params or ())
        self.conn.commit()

    def migration(self):
        migrator = Migrator(self.db_path, self.migrations_dir)
        migrator.run()
