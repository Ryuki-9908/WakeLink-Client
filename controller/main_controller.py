import platform
import shlex
import subprocess
from tkinter import messagebox
from wakeonlan import send_magic_packet
from common.context import Context
from db.models.host_model import HostInfo
from db.handler.host_handler import HostHandler
from ui.dialogs import dialog_ids
from ui.dialogs.dialog_manager import dialog_manager, DialogKey
from ui.dialogs.new_host_dialog import NewHostDialog


class MainController:
    def __init__(self, master):
        self.master = master
        self.host_handler = HostHandler()
        context = Context(class_name=self.__class__.__name__)
        self.logger = context.logger
        self.setting = context.setting
        self.config = context.config

    """ 既存のホスト情報を更新 """
    def update_host(self, host_info: HostInfo):
        name = host_info.name
        if len(name) > 0:
            ret = messagebox.askokcancel("確認", "ホスト情報を上書きしますか？", parent=self.master)
            if ret:
                if self.host_handler.update_host(host_info):
                    messagebox.showinfo("Success", "保存しました。", parent=self.master)
                    self.update_show_hosts()
                else:
                    messagebox.showerror("Error", "保存に失敗しました。", parent=self.master)
        else:
            # ホスト名が未入力の場合はエラーとする。
            messagebox.showerror("Error", "ホスト名を入力してください。", parent=self.master)

    """ 登録済みホスト削除処理 """
    def delete_host(self, host_id):
        self.master.clear_field()
        return self.host_handler.delete_host(host_id)

    """ 表示用ホストリスト生成処理 """
    def create_show_host_list(self, host_info_list: list[HostInfo]) -> dict:
        # 表示用リスト
        show_host_map = {}
        for host_info in host_info_list:
            # 別処理で死活監視を行うためここでは一旦すべてオフラインとする。
            show_host_map[host_info.id] = {"id": host_info.id, "name": host_info.name, "ip_addr": host_info.ip_addr,
                                           "port": host_info.port, "user": host_info.user, "password": host_info.password,
                                           "mac_addr": host_info.mac_addr, "status": "offline"}
        return show_host_map

    """ 表示リストの更新を行う """
    def update_show_hosts(self):
        # 前回DBから取得したデータと現在DBに保存されているデータを比較してリストを更新
        new_show_host_map = self.create_show_host_list(self.host_handler.get_all_host())

        # 差分が無ければ更新しない
        if new_show_host_map != self.master.show_host_map:
            for key in self.master.show_host_map:
                try:
                    new_show_host_map[key]["status"] = self.master.show_host_map[key]["status"]
                except KeyError as e:
                    # 削除時の更新処理はここを通る
                    pass
                except Exception as e:
                    self.logger.error(e)
            self.master.show_host_map = new_show_host_map

        if not self.master.host_list_frame is None:
            # 状態確認を行う
            self.master.host_list_frame.update_show_hosts(self.master.show_host_map)

    """ WOL送信処理 """
    def wake_on_lan(self, mac_addr):
        # wol送信処理
        def send():
            result = False
            try:
                send_magic_packet(mac_addr)
                result = True
            except Exception as e:
                self.logger.error("send WOL failed.")
                self.logger.error(e)
            return result

        if len(mac_addr) > 0:
            ret = messagebox.askokcancel("確認", f"【{mac_addr}】を起動します。よろしいですか？", parent=self.master)
            if ret:
                if send():
                    messagebox.showinfo("Success", f"【{mac_addr}】に起動要求を送信しました。", parent=self.master)
                else:
                    messagebox.showerror("Error", f"【{mac_addr}】への起動要求に失敗しました。", parent=self.master)
        else:
            messagebox.showerror("Error", "MACアドレスが入力されていません。", parent=self.master)

    """ SSH接続処理 """
    def ssh_connect(self, host_info: HostInfo):
        # ホスト情報を取得
        name = host_info.name
        ip_addr = host_info.ip_addr
        port = host_info.port
        user = host_info.user
        password = host_info.password

        def connect():
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
                python_cmd = ' '.join([
                    shlex.quote(python),
                    shlex.quote(str(file_path)),
                    "--ip", shlex.quote(ip_addr),
                    "--port", shlex.quote(port),
                    "--user", shlex.quote(user),
                    "--pwd", shlex.quote(password)
                ])
                subprocess.Popen(['xterm', '-e', 'bash', '-c', python_cmd])

        if len(ip_addr) > 0:
            ret = messagebox.askokcancel("SSH接続確認", f"【{name}({ip_addr})】に接続します。よろしいですか？", parent=self.master)
            if ret: connect()
        else:
            messagebox.showerror("Error", "IPアドレスが入力されていません。", parent=self.master)

    """ ホスト一覧からの削除処理のコールバック """
    def delete_callback(self, host_info):
        name = host_info['name']
        ip_addr = host_info['ip_addr']
        mac_addr = host_info['mac_addr']
        message = f"{name}を削除しますか？"
        if len(host_info['mac_addr']) > 0:
            # Macアドレスが保存されている場合は優先でメッセージに表示（一意のため）
            message = f"{name}({mac_addr})を削除しますか？"
        elif len(host_info['ip_addr']) > 0:
            # Macアドレスが保存されていない場合はIPアドレスをメッセージに表示
            message = f"{name}({ip_addr})を削除しますか？"

        ret = messagebox.askokcancel("確認", message, parent=self.master)
        if ret:
            if self.delete_host(host_info["id"]):
                messagebox.showinfo("Success", "削除しました。", parent=self.master)
                self.update_show_hosts()
            else:
                messagebox.showerror("Error", "削除に失敗しました。", parent=self.master)

    def show_add_new_host_dialog(self):
        def show_dialog(parent):
            # 新規ホスト追加ダイアログを表示
            # 新規追加後にホスト一覧を更新するためにコールバックを渡す
            return NewHostDialog(parent, update_show_hosts_callback=self.update_show_hosts)

        # 複数画面を許可しないのでkeyは空文字で指定
        key = DialogKey(key="", dialog_id=dialog_ids.ADD_NEW_HOST_DIALOG)
        dialog_manager.show_dialog(self.master, key, create_dialog_fn=show_dialog)
