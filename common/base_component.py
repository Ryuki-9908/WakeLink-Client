from common.config import Config
from common.logger import Logger
from common.setting import Setting


class BaseComponent:
    def __init__(self, class_name: str):
        self.config = Config()
        self.logger = Logger(class_name).get_logger()
        self.setting = Setting(self.config.SETTING_INI)
