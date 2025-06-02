import logging
import datetime
from logging.handlers import RotatingFileHandler
from common.config import Config


class Logger:
    def __init__(self, tag):
        self.logger = logging.getLogger(tag)
        if not self.logger.handlers:
            self.logger.setLevel(logging.DEBUG)
            self.logger.propagate = False

            # フォーマッター定義
            console_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            file_formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s - %(filename)s - %(funcName)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )

            # コンソールハンドラー
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            console_handler.setFormatter(console_formatter)

            # ログファイル生成
            log_file = self.create_log_file()

            # ファイルハンドラー
            file_handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=5)
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(file_formatter)

            # ハンドラーをロガーに追加
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)

    def create_log_file(self):
        # ログファイルのディレクトリが存在しない場合は作成
        Config.LOG_DIR.mkdir(exist_ok=True)
        today = datetime.date.today().isoformat()
        log_file = Config.LOG_DIR.joinpath(f"{today}.log").resolve()
        return log_file

    def get_logger(self):
        return self.logger
