import os
import logging

LOG_FILE = ".\\Logs\\app.log"


class Log:
    def __init__(self, tag):
        self.logger = logging.getLogger(tag)
        if not self.logger.handlers:
            self.logger.setLevel(logging.DEBUG)
            # コンソールハンドラー
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            console_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            console_handler.setFormatter(console_formatter)

            # ログファイルのディレクトリが存在しない場合は作成
            log_dir = os.path.dirname(LOG_FILE)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)

            # ファイルハンドラー
            file_handler = logging.FileHandler(LOG_FILE)
            file_handler.setLevel(logging.INFO)
            file_formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s - %(filename)s - %(funcName)s"
            )
            file_handler.setFormatter(file_formatter)

            # ハンドラーをロガーに追加
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)

    # def info(self, class_name):
    #     return
    #
    # def debug(self, class_name):
    #     return
    #
    # def error(self, class_name):
    #     return

    def get_logger(self):
        return self.logger
