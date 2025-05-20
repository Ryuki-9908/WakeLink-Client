import threading
import tkinter as tk
from tkinter import Listbox, messagebox, ttk
import time
from utils import colors
from common.log import Log
from controller import main_controller


class MainLayout(tk.Tk):
    def __init__(self):
        super().__init__()
        """ 初期化処理 """
        class_name = self.__class__.__name__
        # 各画面への通知用キューを画面IDに紐づけて生成
        self.queues = {}
        # ロガー生成
        self.log = Log(tag=class_name).get_logger()
        # タイマー初期化
        self.buftime = time.time()
        # 切断されたデバイス
        self.disconnect_devices = set()

        """ GUI生成 """
        self.title("WakeLink Client")
        self.geometry("800x500")
        self.resizable(width=False, height=False)

        """ ウィジットの初期化 """
        # ホスト一覧
        self.remote_hosts_view: tk.Listbox = Listbox()
        self.remote_hosts_menu: tk.Menu = tk.Menu()

        """ メイン画面生成 """
        self.create_main()

        """ 監視サービス起動 """
        self.reload()
        self.time_event()

    # 各画面へのデバイス切断通知
    def notice_queues(self):
        pass

    # 毎秒、ホストの状態を自動更新
    def time_event(self):
        tmp = time.time()
        if (tmp - self.buftime) >= 0.5:
            # 非同期で監視で自動更新
            th = threading.Thread(target=self.reload)
            th.start()
            self.buftime = tmp
        self.after(1, self.time_event)

    # ホストの状態を更新
    def reload(self, event=None):
        pass

    """ サブ画面が閉じられた時のコールバック """
    def close_callback(self, screen_id, device, ):
        key = self.create_queues_key(screen_id, device)
        # キューを削除
        self.queues.pop(key)

    def host_connect(self, host):
        return

    """ メイン画面表示 """
    def create_main(self):
        # 背景色
        background_color = colors.BACKGROUND_COLOR

        # 背景色を設定
        self.configure(bg=background_color)

        # メイン画面を左右に分割（左：ホスト一覧、右：詳細フォーム）
        self.columnconfigure(0, weight=1, minsize=200)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        """ ホスト一覧 """
        host_list_frame = tk.Frame(self, bg=background_color, bd=0, relief="sunken")
        host_list_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        host_list_label = tk.Label(host_list_frame, text="ホスト一覧", bg=background_color)
        host_list_label.place(x=20, y=20)

        host_list = []
        host_list_items = tk.StringVar(host_list_frame, value=host_list)
        self.remote_hosts_view = Listbox(host_list_frame, listvariable=host_list_items, height=25, width=50)
        self.remote_hosts_view.place(x=15, y=50)

        """ 詳細フォーム """
        host_info_frame = tk.Frame(self, bg=background_color, bd=0, relief="sunken")
        host_info_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=20)
        host_info_frame.columnconfigure(0, weight=1)
        host_info_frame.rowconfigure(10, weight=1)

        # ホスト名 / IPアドレス
        operation_label = tk.Label(host_info_frame, text="ホスト名 / IPアドレス", bg=background_color)
        operation_label.grid(row=0, column=0, sticky="w", pady=5)

        # ホスト名またはIPアドレスを指定
        host_name = tk.Entry(host_info_frame)
        host_name.grid(row=1, column=0, sticky="ew", padx=(0, 20), pady=5)

        # ユーザー/パスワード
        user_pass_label_frame = tk.Frame(host_info_frame, bg=background_color, bd=0, relief="sunken")
        user_pass_label_frame.grid(row=2, column=0, sticky="nsew", pady=(10, 5))
        user_pass_label_frame.columnconfigure(0, weight=1)
        user_pass_label_frame.columnconfigure(1, weight=1)

        user_pass_frame = tk.Frame(host_info_frame, bg=background_color, bd=0, relief="sunken")
        user_pass_frame.grid(row=3, column=0, sticky="nsew", padx=(0, 20))
        user_pass_frame.columnconfigure(0, weight=1)
        user_pass_frame.columnconfigure(1, weight=1)

        # ユーザー名
        operation_label = tk.Label(user_pass_label_frame, text="ユーザー", bg=background_color)
        operation_label.grid(row=0, column=0, sticky="w")

        # ユーザー名を指定
        host_name = tk.Entry(user_pass_frame)
        host_name.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        # パスワード
        operation_label = tk.Label(user_pass_label_frame, text="パスワード", bg=background_color)
        operation_label.grid(row=0, column=1, sticky="w")

        # パスワードを指定
        host_name = tk.Entry(user_pass_frame)
        host_name.grid(row=0, column=1, sticky="ew", padx=(5, 5))

        install_bt = tk.Button(host_info_frame, text="接続")
        install_bt.bind("<Button-1>", self.host_connect)
        install_bt.grid(row=9, column=0, sticky="ew", padx=(0, 20), pady=20)
