import sqlite3
import os
from pathlib import Path
from common.context import Context

class Migrator:
    def __init__(self, db_path: str, migrations_dir: str):
        context = Context(class_name=self.__class__.__name__)
        self.logger = context.logger
        self.db_path = db_path
        self.migrations_dir = Path(migrations_dir)

    def get_connection(self):
        if not os.path.exists(self.db_path):
            self.logger.debug("DBファイルが存在しません。新規作成します。")
        return sqlite3.connect(self.db_path)

    def get_current_version(self, cursor):
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'"
        )
        if cursor.fetchone() is None:
            return 0
        cursor.execute("SELECT MAX(version) FROM schema_version")
        row = cursor.fetchone()
        return row[0] if row and row[0] else 0

    def set_current_version(self, cursor, version: int):
        cursor.execute("INSERT INTO schema_version (version) VALUES (?)", (version,))

    def ensure_schema_table(self, cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER NOT NULL,
                applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

    def run(self):
        self.logger.debug(f"DBパス: {self.db_path}")
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            self.ensure_schema_table(cursor)
            current_version = self.get_current_version(cursor)
            self.logger.debug(f"現在のバージョン: {current_version}")

            for sql_file in sorted(self.migrations_dir.glob("*.sql")):
                try:
                    version = int(sql_file.stem.split("_")[0])
                except ValueError:
                    self.logger.warning(f"{sql_file.name} は無効なバージョン番号です。スキップします。")
                    continue

                if version <= current_version:
                    continue

                with open(sql_file, "r", encoding="utf-8") as f:
                    sql = f.read()

                try:
                    cursor.executescript(sql)
                    self.set_current_version(cursor, version)
                    conn.commit()
                    self.logger.debug(f"バージョン {version} へ更新完了")
                except Exception as e:
                    self.logger.error(f"{sql_file.name} の適用に失敗: {e}")
                    conn.rollback()
                    break
        finally:
            conn.close()
