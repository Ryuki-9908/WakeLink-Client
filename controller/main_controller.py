import subprocess
from wakeonlan import send_magic_packet
from common.base_component import BaseComponent
from models.host_model import HostModel
import platform


class MainController(BaseComponent):
    def __init__(self):
        super().__init__(class_name=self.__class__.__name__)
        self.host_model = HostModel()

    def host_info_save(self, host, ip_addr, user, pwd, mac_addr):
        return self.host_model.insert(host, ip_addr, user, pwd, mac_addr)

    def host_info_delete(self, id):
        return self.host_model.delete(id)

    def wake_on_lan(self, mac_addr):
        result = False
        try:
            send_magic_packet(mac_addr)
            result = True
        except Exception as e:
            print("WOL送信に失敗しました")
            print(e)

        return result

    def ssh_connect(self, ip_addr, user, password, port="22"):
        python = self.setting.get(section="Settings", key="python_cmd")
        file_path = self.config.SSH_TERMINAL_FILE
        options = ["--ip", ip_addr, "--port", port, "--user", user, "--pwd", password]
        # 環境によってコマンドを分ける
        if platform.system() == "Windows":
            # windowsの場合
            subprocess.Popen(["cmd", "/c", python, file_path] + options,
                             creationflags=subprocess.CREATE_NEW_CONSOLE)
        elif platform.system() == "Linux":
            # Linuxの場合
            # xtermを使うため（sudo apt install xtermでインストール必須）
            python_cmd = f"{python} {file_path} --ip {ip_addr} --port {port} --user {user} --pwd {password}"
            subprocess.Popen(['xterm', '-e', 'bash', '-c', python_cmd])
