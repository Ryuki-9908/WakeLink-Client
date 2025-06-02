from common.config import Config
from common.logger import Logger
from common.setting import Setting


class Context:
    def __init__(self, class_name: str):
        self.class_name = class_name
        self.config = Config()
        self.__logger_instance = None    # ロガーは遅延初期化
        self.setting = Setting(self.config.SETTING_INI)

    @property
    def logger(self):
        if self.__logger_instance is None:
            self.__logger_instance = Logger(self.class_name).get_logger()
        return self.__logger_instance
