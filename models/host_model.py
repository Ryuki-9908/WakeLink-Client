from db.sqlite_repository import SQLiteRepository
from common.base_component import BaseComponent
from dataclasses import dataclass


class HostModel(BaseComponent):
    def __init__(self):
        super().__init__(class_name=self.__class__.__name__)
        self.table_name = self.config.HOST_TABLE
        self.repository = SQLiteRepository()

    def insert(self, host, ip_addr, user, password, mac_addr):
        result = False
        try:
            """ホストをINSERT"""
            query = "INSERT INTO {} (host, ip_addr, user, password, mac_addr ) VALUES (?, ?, ?, ?, ?)".format(self.table_name)
            self.repository.execute_query(query, (host, ip_addr, user, password, mac_addr))
            result = True
        except Exception as e:
            self.logger.debug(e)
        return result

    def get_all_host(self):
        """登録している全ホストを取得"""
        query = "SELECT * FROM {}".format(self.table_name)
        hosts = self.repository.execute_query(query)
        host_info_list = []
        for host in hosts:
            host_info = HostInfo(
                id=host[0],
                name=host[1],
                ip_addr=host[2],
                user=host[3],
                password=host[4],
                mac_addr=host[5],
            )
            host_info_list.append(host_info)
        return host_info_list


@dataclass
class HostInfo:
    id: int
    name: str
    ip_addr: str
    user: str
    password: str
    mac_addr: str
