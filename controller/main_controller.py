import threading
import paramiko
from wakeonlan import send_magic_packet
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from common.base_component import BaseComponent
from models.host_model import HostModel


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

    def interactive_shell(self, ip_addr, user, password):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=ip_addr, username=user, password=password)

        chan = client.invoke_shell()
        history = InMemoryHistory()
        session = PromptSession(history=history)

        def recv_loop():
            while True:
                if chan.recv_ready():
                    data = chan.recv(1024)
                    print(data.decode(errors="ignore"), end="", flush=True)

        thread = threading.Thread(target=recv_loop, daemon=True)
        thread.start()

        try:
            while True:
                cmd = session.prompt("> ")  # 入力補完・履歴対応
                chan.send(cmd + "\n")
        except (KeyboardInterrupt, EOFError):
            print("\n終了します")
        finally:
            chan.close()
            client.close()

    def ssh_connect(self, ip_addr, user, pwd):
        self.interactive_shell(ip_addr, user, pwd)
