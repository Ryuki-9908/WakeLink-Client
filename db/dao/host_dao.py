from db.sqlite_manager import SQLiteManager
from common.context import Context
from db.models.host_model import HostModel, HostInfo


class HostDao:
    def __init__(self):
        self.manager = SQLiteManager()
        self.table_name = HostModel.__tablename__
        context = Context(class_name=self.__class__.__name__)
        self.logger = context.logger

    def insert(self, query: str, params: tuple):
        result = False
        try:
            self.manager.execute_query(query, params)
            result = True
        except Exception as e:
            self.logger.error(e)
        return result

    def read(self, query: str, params: tuple):
        host_info = ()
        try:
            host_info = self.manager.execute_query(query, params)
        except Exception as e:
            self.logger.error(e)
        return host_info

    def update(self, query: str, params: tuple):
        result = False
        try:
            self.manager.execute_update(query, params)
            result = True
        except Exception as e:
            self.logger.error(e)
        return result

    def delete(self, query: str, params: tuple):
        result = False
        try:
            self.manager.execute_update(query, params)
            result = True
        except Exception as e:
            self.logger.error(e)
        return result
