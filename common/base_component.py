from common.config import Config
from common.logger import Logger


class BaseComponent:
    def __init__(self, class_name: str):
        self.config = Config()
        self.logger = Logger(class_name).get_logger()
