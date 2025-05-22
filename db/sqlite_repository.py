import sqlite3
from sqlite3 import OperationalError
from common.base_component import BaseComponent


class SQLiteRepository(BaseComponent):
    def __init__(self):
        super().__init__(class_name=self.__class__.__name__)
        # 設定ファイル読み込み
        db_path = self.config.DB_PATH
        self.db_path = db_path
        self.conn = None
        self.create()

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

    def create(self):
        self.connect()
        with sqlite3.connect(self.db_path) as self.conn:
            try:
                cur = self.conn.cursor()
                # table生成
                cur.execute('CREATE TABLE my_host(id INTEGER PRIMARY KEY AUTOINCREMENT, host STRING, ip_addr STRING, user STRING, password STRING, mac_addr STRING)')
                # DBコミット
                self.conn.commit()
            except OperationalError as e:
                pass
            except Exception as e:
                print(e)
