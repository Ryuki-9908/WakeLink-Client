from common.context import Context
from db.dao.host_dao import HostDao
from db.sqlite_manager import SQLiteManager
from db.models.host_model import HostInfo


class HostHandler:
    def __init__(self):
        self.dao = HostDao()
        self.table_name = self.dao.table_name
        self.logger = Context(class_name=self.__class__.__name__).logger

    def save_host(self, host_info: HostInfo):
        """ホストを追加"""
        query = f"""
            INSERT INTO {self.table_name} (host, ip_addr, port, user, password, mac_addr ) 
            VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (
            host_info.name,
            host_info.ip_addr,
            host_info.port,
            host_info.user,
            host_info.password,
            host_info.mac_addr
        )
        result = False
        if self.dao.insert(query, params):
            result = True
            self.logger.debug("save host success.")
            self.logger.debug(host_info)
        else:
            self.logger.debug("save host failed.")

        return result

    def get_host(self, host_id):
        query = f"""
            SELECT * FROM {self.table_name}
        """
        conditions = []
        params = []

        if host_id:
            conditions.append("id = ?")
            params.append(host_id)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        hosts = self.dao.read(query, tuple(params))
        host_info = HostInfo(
            id=hosts[0],
            name=hosts[1],
            ip_addr=hosts[2],
            port=hosts[3],
            user=hosts[4],
            password=hosts[5],
            mac_addr=hosts[6],
        )
        return host_info

    def get_all_host(self):
        query = f"""
            SELECT * FROM {self.table_name}
        """
        params = ()

        """登録している全ホストを取得"""
        hosts = self.dao.read(query, params)
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

    def update_host(self, host_info: HostInfo):
        query = f"""
            UPDATE {self.table_name}
            SET host = ?, ip_addr = ?, port = ?, user = ?, password = ?, mac_addr = ?
            WHERE id = ?
        """
        params = (
            host_info.name,
            host_info.ip_addr,
            host_info.port,
            host_info.user,
            host_info.password,
            host_info.mac_addr,
            host_info.id
        )
        result = False
        if self.dao.update(query, params):
            result = True
            self.logger.debug("update host success.")
            self.logger.debug(f"after host: {host_info}")
        else:
            self.logger.debug("update host failed.")

        return result

    def delete_host(self, host_id: int):
        """ホストを削除"""
        query = f"DELETE FROM {self.table_name} WHERE id = ?"
        params = (host_id,)
        result = self.dao.delete(query, params)
        if result:
            self.logger.debug("delete host success.")
        else:
            self.logger.debug("delete host failed.")

        return result
