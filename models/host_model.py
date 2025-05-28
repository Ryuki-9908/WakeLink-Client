from db.sqlite_repository import SQLiteRepository
from common.component import Component
from dataclasses import dataclass


@dataclass
class HostInfo:
    id: int
    name: str
    ip_addr: str
    port: str
    user: str
    password: str
    mac_addr: str


class HostModel(Component):
    def __init__(self):
        super().__init__(class_name=self.__class__.__name__)
        self.table_name = self.config.HOST_TABLE
        self.repository = SQLiteRepository()

    def insert(self, host, ip_addr, port, user, password, mac_addr):
        result = False
        try:
            """ホストを追加"""
            query = "INSERT INTO {} (host, ip_addr, port, user, password, mac_addr ) VALUES (?, ?, ?, ?, ?, ?)".format(self.table_name)
            self.repository.execute_query(query, (host, ip_addr, port, user, password, mac_addr))
            result = True
        except Exception as e:
            self.logger.debug(e)
        return result

    def update(self, host_info: HostInfo):
        result = False

        try:
            host_id = host_info.id
            name = host_info.name
            ip_addr = host_info.ip_addr
            port = host_info.port
            user = host_info.user
            pwd = host_info.password
            mac_addr = host_info.mac_addr

            query = f"""
                UPDATE {self.table_name}
                SET host = ?, ip_addr = ?, port = ?, user = ?, password = ?, mac_addr = ?
                WHERE id = ?
            """
            params = (name, ip_addr, port, user, pwd, mac_addr, host_id)
            self.repository.execute_update(query, params)
            result = True
        except Exception as e:
            self.logger.debug(e)
        return result

    def delete(self, id):
        result = False
        try:
            """ホストを削除"""
            query = "DELETE FROM {} WHERE id = ?".format(self.table_name)
            self.repository.execute_update(query, (id,))
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
                port=host[3],
                user=host[4],
                password=host[5],
                mac_addr=host[6],
            )
            host_info_list.append(host_info)
        return host_info_list
