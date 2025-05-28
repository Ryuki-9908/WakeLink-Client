import subprocess
from tkinter import messagebox

from wakeonlan import send_magic_packet
from common.component import Component
from models.host_model import HostModel, HostInfo
import platform
from ui.dialogs.dialog_manager import dialog_manager, DialogKey
from ui.dialogs.add_new_host_dialog import AddNewHostDialog


class MainController(Component):
    def __init__(self, master):
        super().__init__(class_name=self.__class__.__name__)
        self.master = master
        self.host_model = HostModel()

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

    def ssh_connect(self, ip_addr, port, user, password):
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

    def save_host(self, parent, host_info: HostInfo):
        name = host_info.name
        if len(name) > 0:
            ret = messagebox.askokcancel("確認", "現在入力中のホスト情報を保存しますか？", parent=parent)
            if ret:
                ip_addr = host_info.ip_addr
                port = host_info.port
                user = host_info.user
                pwd = host_info.password
                mac_addr = host_info.mac_addr
                if self.host_model.insert(name, ip_addr, port, user, pwd, mac_addr):
                    messagebox.showinfo("Success", "保存しました。", parent=parent)
                    self.master.update_show_host_list()
                else:
                    messagebox.showerror("Error", "保存に失敗しました。", parent=parent)
        else:
            # ホスト名が未入力の場合はエラーとする。
            messagebox.showerror("Error", "ホスト名を入力してください。", parent=parent)

    def update_host(self, parent, host_info: HostInfo):
        name = host_info.name
        if len(name) > 0:
            ret = messagebox.askokcancel("確認", "ホスト情報を上書きしますか？", parent=parent)
            if ret:
                if self.host_model.update(host_info):
                    messagebox.showinfo("Success", "保存しました。", parent=parent)
                    self.master.update_show_host_list()
                else:
                    messagebox.showerror("Error", "保存に失敗しました。", parent=parent)
        else:
            # ホスト名が未入力の場合はエラーとする。
            messagebox.showerror("Error", "ホスト名を入力してください。", parent=parent)

    def create_add_new_host_dialog(self, parent):
        return AddNewHostDialog(parent, save_callback=self.save_host)
