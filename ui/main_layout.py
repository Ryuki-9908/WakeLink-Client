import copy
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox
import time
from utils import colors, process_type
from common.logger import Logger
from controller.main_controller import MainController
from models.host_model import HostModel, HostInfo
from ui.frame.host_list_frame import HostListFrame
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
        self.show_host_map = self.create_show_host_list(self.host_model.get_all_host())

        """ GUI生成 """
        self.title("WakeLink Client")
        self.geometry("600x400")
        self.resizable(width=False, height=False)

        """ ウィジットの初期化 """
        # ホスト一覧
        self.host_list_frame: HostListFrame = None
        self.remote_hosts_menu: tk.Menu = tk.Menu()
        self.host_name: tk.Entry = tk.Entry()
        self.ip_addr: tk.Entry = tk.Entry()
        self.user_name: tk.Entry = tk.Entry()
        self.password: tk.Entry = tk.Entry()
        self.mac_addr: tk.Entry = tk.Entry()

        """ コントローラーの初期化 """
        self.controller = MainController()

        """ 画面生成前に状態確認を行う """
        self.host_status_check(attempts=1)

        """ メイン画面生成 """
        self.create_main()

        """ 選択中アイテムのID """
        self.selected_id = 0

        """ 監視サービス起動 """
        self.thread_lock = threading.Lock()  # スレッドロックを使用
        self.time_event()

    def create_show_host_list(self, host_info_list: list[HostInfo]) -> dict:
        # 表示用リストを生成
        show_host_map = {}
        for host_info in host_info_list:
            # 後続処理でpingによる起動確認を行うためここでは一旦すべてオフラインとする。
            show_host_map[host_info.id] = {"id": host_info.id, "name": host_info.name, "ip_addr": host_info.ip_addr,
                                           "user": host_info.user, "password": host_info.password, "mac_addr": host_info.mac_addr,
                                           "status": "offline"}
        return show_host_map

    # 各画面へのデバイス切断通知
    def notice_queues(self):
        pass

    # 毎秒、ホストの状態を自動更新
    def time_event(self, interval=10, attempts=3, after_time=2000):
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
        new_show_host_map = self.create_show_host_list(self.host_model.get_all_host())

        # 差分が無ければ更新しない
        if new_show_host_map != self.show_host_map:
            for key in self.show_host_map:
                try:
                    new_show_host_map[key]["status"] = self.show_host_map[key]["status"]
                except KeyError as e:
                    # 削除時の更新処理はここを通る
                    pass
                except Exception as e:
                    self.logger.error(e)
            self.show_host_map = new_show_host_map

        if not self.isCheck and not self.host_list_frame is None:
            # 状態確認を行う
            self.host_list_frame.update_devices(self.show_host_map)

    """ ホストの状態確認処理 """
    def host_status_check(self, attempts: int = 3):
        self.isCheck = True

        # リスト更新判断のために複製
        copy_show_host_map = copy.deepcopy(self.show_host_map)
        try:
            # リストに含まれるホストの状態を確認
            for key in self.show_host_map:
                host = self.show_host_map[key]
                is_online = False
                # 指定回数pingを送って状態を確認
                for _ in range(attempts):
                    # IPの入力が無い場合は即抜ける
                    if len(host['ip_addr']) == 0: break
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
                    self.show_host_map[key]['status'] = "online"
                else:
                    self.show_host_map[key]['status'] = "offline"

            # 複製しておいたリストと差分がある場合はリストを更新
            if copy_show_host_map != self.show_host_map and not self.host_list_frame is None:
                self.host_list_frame.update_devices(self.show_host_map)
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
        name = self.host_name.get()
        if len(name) > 0:
            ret = messagebox.askokcancel("確認", "現在入力中のホスト情報を保存しますか？", parent=self)
            if ret:
                ip_addr = self.ip_addr.get()
                user = self.user_name.get()
                pwd = self.password.get()
                mac_addr = self.mac_addr.get()
                if self.controller.host_info_save(name, ip_addr, user, pwd, mac_addr):
                    messagebox.showinfo("Success", "保存しました。", parent=self)
                    self.update_show_host_list()
                else:
                    messagebox.showerror("Error", "保存に失敗しました。", parent=self)
        else:
            # ホスト名が未入力の場合はエラーとする。
            messagebox.showerror("Error", "ホスト名を入力してください。", parent=self)

    def delete_callback(self, host_info):
        name = host_info['name']
        ip_addr = host_info['ip_addr']
        mac_addr = host_info['mac_addr']
        message = ""
        if len(host_info['mac_addr']) > 0:
            # Macアドレスが保存されている場合は優先でメッセージに表示（一意のため）
            message = f"{name}({mac_addr})を削除しますか？"
        elif len(host_info['ip_addr']) > 0:
            # Macアドレスが保存されていない場合はIPアドレスをメッセージに表示
            message = f"{name}({ip_addr})を削除しますか？"
        else:
            message = f"{name}を削除しますか？"

        ret = messagebox.askokcancel("確認", message, parent=self)
        if ret:
            if self.controller.host_info_delete(host_info["id"]):
                messagebox.showinfo("Success", "削除しました。", parent=self)
                self.update_show_host_list()
            else:
                # デバイスが接続されていない場合
                messagebox.showerror("Error", "削除に失敗しました。", parent=self)

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
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2, minsize=300)
        self.rowconfigure(0, weight=1)

        """ ホスト一覧 """
        self.host_list_frame = HostListFrame(self, self.show_host_map)
        self.host_list_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 20), pady=10)

        self.host_list_frame.set_callback(process_type.SELECT, callback=self.host_selected_callback)
        self.host_list_frame.set_callback(process_type.DELETE, callback=self.delete_callback)

        """ 詳細フォームの親となるサブフレーム """
        sub_frame = tk.Frame(self, bg=background_color, bd=0, relief="sunken")
        sub_frame.grid(row=0, column=1, sticky="nsew")
        sub_frame.columnconfigure(0, weight=1)
        # 詳細フォーム
        sub_frame.rowconfigure(0, weight=9)
        # ボタン表示領域
        sub_frame.rowconfigure(1, weight=1)

        """ 詳細フォーム """
        host_info_frame = tk.Frame(sub_frame, bg=background_color, bd=0, relief="sunken")
        host_info_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=(20, 0))
        host_info_frame.columnconfigure(0, weight=0)
        host_info_frame.columnconfigure(1, weight=1)
        host_info_frame.rowconfigure(0, weight=1)
        host_info_frame.rowconfigure(1, weight=9)

        # ホスト情報
        host_info_label = tk.Label(host_info_frame, text="ホスト情報", bg=background_color, font=("メイリオ", "15", "bold"))
        host_info_label.grid(row=0, column=0, sticky="ew", pady=(5, 10))

        # ラベル領域
        label_frame = tk.Frame(host_info_frame, bg=background_color, bd=0, relief="sunken")
        label_frame.grid(row=1, column=0, sticky="nsew", pady=5)
        label_frame.rowconfigure(5, weight=1)

        # データ領域
        data_frame = tk.Frame(host_info_frame, bg=background_color, bd=0, relief="sunken")
        data_frame.grid(row=1, column=1, sticky="nsew", padx=(0, 20), pady=5)
        data_frame.columnconfigure(1, weight=1)
        data_frame.rowconfigure(5, weight=1)

        # Grid配置インクリメント関数定義
        self.row_increment = -1
        def grid_row_increment(increment=True, reset=False):
            if reset:
                self.row_increment = 0
            else:
                if increment:
                    self.row_increment = self.row_increment + 1
            return self.row_increment

        """ ラベル領域 """
        # ホスト名
        host_name_label = tk.Label(label_frame, text="ホスト名", bg=background_color, width=10, anchor="w")
        host_name_label.grid(row=grid_row_increment(), column=0, sticky="w", pady=5, ipady=4)

        # IPアドレス
        ip_addr_label = tk.Label(label_frame, text="IPアドレス", bg=background_color, width=10, anchor="w")
        ip_addr_label.grid(row=grid_row_increment(), column=0, sticky="w", pady=5, ipady=4)

        # ユーザー名
        user_label = tk.Label(label_frame, text="ユーザー名", bg=background_color, width=10, anchor="w")
        user_label.grid(row=grid_row_increment(), column=0, sticky="w", pady=5, ipady=4)

        # パスワード
        password_label = tk.Label(label_frame, text="パスワード", bg=background_color, width=10, anchor="w")
        password_label.grid(row=grid_row_increment(), column=0, sticky="w", pady=5, ipady=4)

        # MACアドレス
        mac_addr_label = tk.Label(label_frame, text="MACアドレス", bg=background_color, width=10, anchor="w")
        mac_addr_label.grid(row=grid_row_increment(), column=0, sticky="w", pady=5, ipady=4)

        """ データ領域 """
        data_frame_pady = (10, 0)
        # ホスト名またはIPアドレスを指定
        self.host_name = tk.Entry(data_frame, font=("MSゴシック", "10", "bold"))
        self.host_name.grid(row=grid_row_increment(reset=True), column=1, sticky="ew", pady=data_frame_pady, ipady=4)

        # IPアドレスを指定
        self.ip_addr = tk.Entry(data_frame, font=("MSゴシック", "10", "bold"))
        self.ip_addr.grid(row=grid_row_increment(), column=1, sticky="ew", pady=data_frame_pady, ipady=4)

        # ユーザー名を指定
        self.user_name = tk.Entry(data_frame, font=("MSゴシック", "10", "bold"))
        self.user_name.grid(row=grid_row_increment(), column=1, sticky="ew", pady=data_frame_pady, ipady=4)

        # パスワードを指定
        self.password = tk.Entry(data_frame, font=("MSゴシック", "10", "bold"), show="*")
        self.password.grid(row=grid_row_increment(), column=1, sticky="ew", pady=data_frame_pady, ipady=4)

        # MACアドレスを指定
        self.mac_addr = tk.Entry(data_frame, font=("MSゴシック", "10", "bold"))
        self.mac_addr.grid(row=grid_row_increment(), column=1, sticky="ew", pady=data_frame_pady, ipady=4)

        # ボタン表示領域
        button_frame = tk.Frame(sub_frame, bg=background_color, bd=0, relief="sunken")
        button_frame.grid(row=2, column=0, sticky="nsew", padx=(20, 20), pady=(0, 50))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)

        save_btn = tk.Button(button_frame, text="保存")
        save_btn.bind("<Button-1>", self.save_callback)
        save_btn.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        wake_on_lan_btn = tk.Button(button_frame, text="起動")
        wake_on_lan_btn.bind("<Button-1>", self.wake_on_lan_callback)
        wake_on_lan_btn.grid(row=0, column=1, sticky="nsew", padx=(0, 20))

        connect_btn = tk.Button(button_frame, text="接続")
        connect_btn.bind("<Button-1>", self.connect_callback)
        connect_btn.grid(row=0, column=2, sticky="nsew", padx=(0, 0))
