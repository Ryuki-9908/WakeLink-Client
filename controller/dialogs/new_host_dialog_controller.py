from tkinter import messagebox
from common.context import Context
from db.models.host_model import HostInfo
from db.handler.host_handler import HostHandler
from utils import process_type


class NewHostDialogController:
    def __init__(self, master):
        self.master = master
        self.host_handler = HostHandler()
        self.callbacks = {}
        context = Context(class_name=self.__class__.__name__)
        self.logger = context.logger

    """ ホスト保存処理 """
    def save_host(self, host_info: HostInfo):
        name = host_info.name
        if len(name) > 0:
            ret = messagebox.askokcancel("確認", "現在入力中のホスト情報を保存しますか？", parent=self.master)
            if ret:
                if self.host_handler.save_host(host_info):
                    messagebox.showinfo("Success", "保存しました。", parent=self.master)
                    self.on_update_show_hosts()
                else:
                    messagebox.showerror("Error", "保存に失敗しました。", parent=self.master)
        else:
            # ホスト名が未入力の場合はエラーとする。
            messagebox.showerror("Error", "ホスト名を入力してください。", parent=self.master)

    def run_callback(self, process, *args, **kwargs):
        if process in self.callbacks:
            self.callbacks[process](*args, **kwargs)

    def set_callback(self, process: process_type, callback):
        self.callbacks[process] = callback

    def on_update_show_hosts(self):
        self.run_callback(process_type.SHOW_HOST_UPDATE)
