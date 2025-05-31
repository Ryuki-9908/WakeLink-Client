import tkinter as tk
from utils import colors, process_type
from controller.main_controller import MainController
from db.models.host_model import HostModel, HostInfo
from ui.frame.host_list_frame import HostListFrame
from common.context import Context
from ui.widgets.host_info_form_widgets import HostInfoFormWidgets
from service.host_monitor import HostMonitor


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        """ 初期化処理 """
        # ロガーやconfigなど共通部を初期化
        self.context = Context(class_name=self.__class__.__name__)

        """ コントローラーの初期化 """
        self.controller = MainController(master=self)

        """ 保存されたホスト一覧をすべて取得 """
        self.host_model = HostModel()
        self.show_host_map = self.controller.create_show_host_list(self.host_model.get_all_host())

        """ 死活監視サービスの初期化 """
        monitor_service = HostMonitor(self, self.update_show_hosts)

        """ GUI生成 """
        self.title("WakeLink Client")
        self.geometry("600x400")
        self.resizable(width=False, height=False)

        """ ウィジットの初期化 """
        self.widgets = HostInfoFormWidgets(master=self)
        # ホスト一覧
        self.host_list_frame: HostListFrame = None
        self.remote_hosts_menu: tk.Menu = tk.Menu()
        self.host_name: tk.Entry = tk.Entry()
        self.ip_addr: tk.Entry = tk.Entry()
        self.port: tk.Entry = tk.Entry()
        self.user_name: tk.Entry = tk.Entry()
        self.password: tk.Entry = tk.Entry()
        self.mac_addr: tk.Entry = tk.Entry()

        """ メイン画面生成 """
        self.create_view()

        """ 選択中アイテムのID """
        self.selected_id = 0

        """ 初回の確認と監視サービスの開始 """
        monitor_service.check_host_status(attempts=1)
        monitor_service.start()

    def update_show_hosts(self, updated_map):
        for key, new_data in updated_map.items():
            self.show_host_map[key].update(new_data)
        self.host_list_frame.update_hosts(self.show_host_map)

    def on_wake_on_lan_clicked(self, event):
        mac_addr = self.mac_addr.get()
        self.controller.wake_on_lan(mac_addr)

    def on_click_save(self, event):
        # 選択中のホスト情報をまとめる
        host_info = HostInfo(
            id=self.master.selected_id,
            name=self.master.host_name.get(),
            ip_addr=self.master.ip_addr.get(),
            port=self.master.port.get(),
            user=self.master.user_name.get(),
            password=self.master.password.get(),
            mac_addr=self.master.mac_addr.get(),
        )
        # データベース更新
        self.controller.update_host(host_info)

    def on_connect_clicked(self, event):
        # 選択中のホスト情報をまとめる
        host_info = HostInfo(
            id=self.selected_id,
            name=self.host_name.get(),
            ip_addr=self.ip_addr.get(),
            port=self.port.get(),
            user=self.user_name.get(),
            password=self.password.get(),
            mac_addr=self.mac_addr.get(),
        )

        # SSH接続
        self.controller.ssh_connect(host_info)

    def on_addition_host_clicked(self):
        # 新規ホスト追加画面を表示
        self.controller.show_add_new_host_dialog()

    def host_selected_callback(self, host_info):
        # 選択中アイテムIDを保持
        self.selected_id = host_info['id']

        # フィールドクリア処理
        self.host_name.delete(0, tk.END)
        self.ip_addr.delete(0, tk.END)
        self.port.delete(0, tk.END)
        self.user_name.delete(0, tk.END)
        self.password.delete(0, tk.END)
        self.mac_addr.delete(0, tk.END)

        # クリアしたフィールドに値をセット
        self.host_name.insert(0, host_info['name'])
        self.ip_addr.insert(0, host_info['ip_addr'])
        self.port.insert(0, host_info['port'])
        self.user_name.insert(0, host_info['user'])
        self.password.insert(0, host_info['password'])
        self.mac_addr.insert(0, host_info['mac_addr'])

    def clear_field(self, event=None):
        # フィールドクリア処理
        self.host_name.delete(0, tk.END)
        self.ip_addr.delete(0, tk.END)
        self.port.delete(0, tk.END)
        self.user_name.delete(0, tk.END)
        self.password.delete(0, tk.END)
        self.mac_addr.delete(0, tk.END)

    """ メイン画面表示 """
    def create_view(self):
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
        self.host_list_frame.set_callback(process_type.DELETE, callback=self.controller.delete_callback)
        self.host_list_frame.set_callback(process_type.HOST_ADD, callback=self.on_addition_host_clicked)

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

        # 見出し領域
        host_info_label = tk.Label(host_info_frame, text="ホスト情報", bg=background_color, font=("メイリオ", "15", "bold"))
        host_info_label.grid(row=0, column=0, sticky="ew", pady=(5, 10))

        # 入力クリアボタン
        clear_btn = tk.Button(host_info_frame, text="入力クリア")
        clear_btn.bind("<Button-1>", self.clear_field)
        clear_btn.grid(row=0, column=1, sticky="se", padx=(0, 20))

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

        # IP / Port入力領域
        ip_port_frame = tk.Frame(data_frame, bg=background_color, bd=0, relief="sunken")
        ip_port_frame.grid(row=grid_row_increment(), column=1, sticky="nsew", pady=data_frame_pady)
        ip_port_frame.columnconfigure(0, weight=1)
        ip_port_frame.columnconfigure(1, weight=3)
        ip_port_frame.rowconfigure(0, weight=1)

        # IPアドレスを指定
        self.ip_addr = tk.Entry(ip_port_frame, font=("MSゴシック", "10", "bold"))
        self.ip_addr.grid(row=0, column=0, sticky="ew", ipady=4)

        # ポートを指定
        self.port = self.widgets.port_entry(ip_port_frame, max_length=5, placeholder="port")
        self.port.grid(row=0, column=1, sticky="ew", padx=data_frame_pady, ipady=4)

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

        save_btn = tk.Button(button_frame, text="上書き保存")
        save_btn.bind("<Button-1>", self.on_click_save)
        save_btn.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        wake_on_lan_btn = tk.Button(button_frame, text="起動")
        wake_on_lan_btn.bind("<Button-1>", self.on_wake_on_lan_clicked)
        wake_on_lan_btn.grid(row=0, column=1, sticky="nsew", padx=(0, 20))

        connect_btn = tk.Button(button_frame, text="接続")
        connect_btn.bind("<Button-1>", self.on_connect_clicked)
        connect_btn.grid(row=0, column=2, sticky="nsew", padx=(0, 0))
