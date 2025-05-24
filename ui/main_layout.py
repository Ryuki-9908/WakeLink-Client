import asyncio
import copy
import subprocess
import threading
import tkinter as tk
import tracemalloc
from tkinter import Listbox, messagebox, ttk
import time
from utils import colors
from common.logger import Logger
from controller.main_controller import MainController
from models.host_model import HostModel, HostInfo
from ui.frame.host_list_frame import HostListFrame
from ping3 import ping
from common.base_component import BaseComponent


class MainLayout(tk.Tk):
    def __init__(self):
        super().__init__()
        """ 初期化処理 """
        class_name = self.__class__.__name__
        # 各画面への通知用キューを画面IDに紐づけて生成
        self.queues = {}
        # ロガー生成
        self.logger = Logger(tag=class_name).get_logger()
        # タイマー初期化
        self.buftime = time.time()
        # 切断されたデバイス
        self.disconnect_devices = set()
        # 状態確認スレッド制御用のフラグ
        self.isCheck = False
        # ロガーやconfigなど共通部を初期化
        self.component = BaseComponent(class_name=self.__class__.__name__)
        # Pythonのコマンドを取得する。環境によって異なるためsetting.iniで管理。
        self.python_cmd = self.component.setting.get(section="Settings", key="python_cmd")

        """ 保存されたホスト一覧をすべて取得 """
        self.host_model = HostModel()
        self.show_host_list = self.create_show_host_list(self.host_model.get_all_host())

        """ GUI生成 """
        self.title("WakeLink Client")
        self.geometry("800x500")
        self.resizable(width=False, height=False)

        """ ウィジットの初期化 """
        # ホスト一覧
        self.host_list_frame: HostListFrame
        self.remote_hosts_menu: tk.Menu = tk.Menu()
        self.host_name: tk.Entry = tk.Entry()
        self.ip_addr: tk.Entry = tk.Entry()
        self.user_name: tk.Entry = tk.Entry()
        self.password: tk.Entry = tk.Entry()
        self.mac_addr: tk.Entry = tk.Entry()

        """ コントローラーの初期化 """
        self.controller = MainController()

        """ メイン画面生成 """
        self.create_main()

        """ 選択中アイテムのID """
        self.selected_id = 0

        """ 監視サービス起動 """
        self.thread_lock = threading.Lock()  # スレッドロックを使用
        self.time_event(interval=0, attempts=1)

    def create_show_host_list(self, host_info_list: list[HostInfo]) -> list:
        # 表示用リストを生成
        show_host_list = []
        for host_info in host_info_list:
            # 後続処理でpingによる起動確認を行うためここでは一旦すべてオフラインとする。
            item_dict = {"id": host_info.id, "name": host_info.name, "ip_addr": host_info.ip_addr,
                         "user": host_info.user, "password": host_info.password, "mac_addr": host_info.mac_addr,
                         "status": "offline"}
            show_host_list.append(item_dict)
        return show_host_list

    # 各画面へのデバイス切断通知
    def notice_queues(self):
        pass

    # 毎秒、ホストの状態を自動更新
    def time_event(self, interval = 10, attempts = 3, after_time = 2000):
        tmp = time.time()
        if (tmp - self.buftime) >= interval and not self.isCheck:
            # 前回の確認から10秒以上経っており、確認処理中でない場合
            if self.thread_lock.acquire(blocking=False):  # スレッドロックをチェック
                try:
                    th = threading.Thread(target=self.host_status_check, args=(attempts,), daemon=True)
                    th.start()
                finally:
                    self.thread_lock.release()  # スレッドロックを解除
        self.after(after_time, self.time_event)

    """ 表示リストの更新を行う """
    def update_show_host_list(self):
        # 前回DBから取得したデータと現在DBに保存されているデータを比較してリストを更新
        new_show_host_list = self.create_show_host_list(self.host_model.get_all_host())

        # 差分が無ければ更新しない
        if new_show_host_list != self.show_host_list:
            self.show_host_list = new_show_host_list

        if not self.isCheck:
            # 状態確認を行う
            self.host_list_frame.update_devices(self.show_host_list)

    """ ホストの状態確認処理 """
    def host_status_check(self, attempts: int = 3):
        self.isCheck = True

        # リスト更新判断のために複製
        copy_show_host_list = copy.deepcopy(self.show_host_list)
        try:
            # リストに含まれるホストの状態を確認
            for idx, host in enumerate(self.show_host_list):
                is_online = False
                # 指定回数pingを送って状態を確認
                for _ in range(attempts):
                    try:
                        # port:22で死活監視
                        response = subprocess.run(
                            [self.python_cmd, self.component.config.SEND_PING_FILE, "--ip", host['ip_addr'], "--port", "22"],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                        )
                        if response.returncode == 0:
                            is_online = True
                    except Exception as e:
                        self.logger.error(e)

                if is_online:
                    self.show_host_list[idx]['status'] = "online"
                else:
                    self.show_host_list[idx]['status'] = "offline"

            # 複製しておいたリストと差分がある場合はリストを更新
            if copy_show_host_list != self.show_host_list:
                self.host_list_frame.update_devices(self.show_host_list)
        except Exception as e:
            self.logger.error(e)
        finally:
            # フラグを戻して終了
            self.isCheck = False
            self.buftime = time.time()

    """ サブ画面が閉じられた時のコールバック """
    def close_callback(self, screen_id, device, ):
        key = self.create_queues_key(screen_id, device)
        # キューを削除
        self.queues.pop(key)

    def wake_on_lan_callback(self, event):
        mac_addr = self.mac_addr.get()
        ret = messagebox.askokcancel("確認", "【" + mac_addr + "】" + "を起動します。よろしいですか？", parent=self)
        if ret:
            if self.controller.wake_on_lan(self.mac_addr.get()):
                messagebox.showinfo("Success", "【" + mac_addr + "】" + "に起動要求を送信しました。", parent=self)
            else:
                # デバイスが接続されていない場合
                messagebox.showerror("Error", "【" + mac_addr + "】" + "への起動要求に失敗しました。", parent=self)

    def save_callback(self, event):
        ret = messagebox.askokcancel("確認", "現在入力中のホスト情報を保存しますか？", parent=self)
        if ret:
            host = self.host_name.get()
            ip_addr = self.ip_addr.get()
            user = self.user_name.get()
            pwd = self.password.get()
            mac_addr = self.mac_addr.get()
            if self.controller.host_info_save(host, ip_addr, user, pwd, mac_addr):
                messagebox.showinfo("Success", "保存しました。", parent=self)
                self.update_show_host_list()
            else:
                # デバイスが接続されていない場合
                messagebox.showerror("Error", "保存に失敗しました。", parent=self)

    def connect_callback(self, event):
        ip_addr = self.ip_addr.get()
        user = self.user_name.get()
        pwd = self.password.get()
        self.controller.ssh_connect(ip_addr, user, pwd)

    def host_selected_callback(self, host_info):
        # 選択中アイテムIDを保持
        self.selected_id = host_info['id']

        # フィールドクリア処理
        self.host_name.delete(0, tk.END)
        self.ip_addr.delete(0, tk.END)
        self.user_name.delete(0, tk.END)
        self.password.delete(0, tk.END)
        self.mac_addr.delete(0, tk.END)

        # クリアしたフィールドに値をセット
        self.host_name.insert(0, host_info['name'])
        self.ip_addr.insert(0, host_info['ip_addr'])
        self.user_name.insert(0, host_info['user'])
        self.password.insert(0, host_info['password'])
        self.mac_addr.insert(0, host_info['mac_addr'])

    """ メイン画面表示 """
    def create_main(self):
        # 背景色
        background_color = colors.BACKGROUND_COLOR

        # 背景色を設定
        self.configure(bg=background_color)

        # メイン画面を左右に分割（左：ホスト一覧、右：詳細フォーム）
        self.columnconfigure(0, weight=1, minsize=200)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        """ ホスト一覧 """
        self.host_list_frame = HostListFrame(self, self.show_host_list, select_callback=self.host_selected_callback)
        self.host_list_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 20), pady=10)

        """ 詳細フォーム """
        host_info_frame = tk.Frame(self, bg=background_color, bd=0, relief="sunken")
        host_info_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=20)
        host_info_frame.columnconfigure(0, weight=1)
        host_info_frame.rowconfigure(10, weight=1)

        # ホスト名 / IPアドレス
        host_name_label = tk.Label(host_info_frame, text="ホスト名", bg=background_color)
        host_name_label.grid(row=0, column=0, sticky="w", pady=5)

        # ホスト名またはIPアドレスを指定
        self.host_name = tk.Entry(host_info_frame)
        self.host_name.grid(row=1, column=0, sticky="ew", padx=(0, 20), pady=5)

        ip_addr_label = tk.Label(host_info_frame, text="IPアドレス", bg=background_color)
        ip_addr_label.grid(row=2, column=0, sticky="w", pady=5)

        # ホスト名またはIPアドレスを指定
        self.ip_addr = tk.Entry(host_info_frame)
        self.ip_addr.grid(row=3, column=0, sticky="ew", padx=(0, 20), pady=5)

        # ユーザー/パスワード
        user_pass_label_frame = tk.Frame(host_info_frame, bg=background_color, bd=0, relief="sunken")
        user_pass_label_frame.grid(row=4, column=0, sticky="nsew", pady=(10, 5))
        user_pass_label_frame.columnconfigure(0, weight=1)
        user_pass_label_frame.columnconfigure(1, weight=1)

        user_pass_frame = tk.Frame(host_info_frame, bg=background_color, bd=0, relief="sunken")
        user_pass_frame.grid(row=5, column=0, sticky="nsew", padx=(0, 20))
        user_pass_frame.columnconfigure(0, weight=1)
        user_pass_frame.columnconfigure(1, weight=1)

        # ユーザー名
        user_label = tk.Label(user_pass_label_frame, text="ユーザー", bg=background_color)
        user_label.grid(row=0, column=0, sticky="w")

        # ユーザー名を指定
        self.user_name = tk.Entry(user_pass_frame)
        self.user_name.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        # パスワード
        password_label = tk.Label(user_pass_label_frame, text="パスワード", bg=background_color)
        password_label.grid(row=0, column=1, sticky="w")

        # パスワードを指定
        self.password = tk.Entry(user_pass_frame)
        self.password.grid(row=0, column=1, sticky="ew", padx=(5, 5))

        # MACアドレス
        mac_addr_label = tk.Label(host_info_frame, text="MACアドレス", bg=background_color)
        mac_addr_label.grid(row=6, column=0, sticky="w", pady=(10, 0))

        # MACアドレスを指定
        self.mac_addr = tk.Entry(host_info_frame)
        self.mac_addr.grid(row=7, column=0, sticky="ew", padx=(0, 20), pady=5)

        save_btn = tk.Button(host_info_frame, text="保存")
        save_btn.bind("<Button-1>", self.save_callback)
        save_btn.grid(row=8, column=0, sticky="ew", padx=(0, 20), pady=(20, 0))

        wake_on_lan_btn = tk.Button(host_info_frame, text="起動")
        wake_on_lan_btn.bind("<Button-1>", self.wake_on_lan_callback)
        wake_on_lan_btn.grid(row=9, column=0, sticky="ew", padx=(0, 20), pady=(20, 0))

        connect_btn = tk.Button(host_info_frame, text="接続")
        connect_btn.bind("<Button-1>", self.connect_callback)
        connect_btn.grid(row=10, column=0, sticky="ew", padx=(0, 20), pady=20)
