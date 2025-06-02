import tkinter as tk

from db.models.host_model import HostInfo
from ui.dialogs.base_dialog import BaseDialog
from ui.widgets import HostInfoFormWidgets
from utils import colors, process_type
from controller.dialogs.new_host_dialog_controller import NewHostDialogController


class NewHostDialog(BaseDialog):
    def __init__(self, dialog, update_show_hosts_callback):
        super().__init__(dialog, class_name=self.__class__.__name__)
        self.dialog = dialog
        self.widgets = HostInfoFormWidgets(master=self)

        # 処理を制御するコントローラ―を初期化
        self.controller = NewHostDialogController(self)
        # 表示ホスト更新用コールバックをセット
        self.controller.set_callback(process=process_type.SHOW_HOST_UPDATE, callback=update_show_hosts_callback)

        # 入力情報
        self.host_name: tk.Entry = tk.Entry()
        self.ip_addr: tk.Entry = tk.Entry()
        self.port: tk.Entry = tk.Entry()
        self.user_name: tk.Entry = tk.Entry()
        self.password: tk.Entry = tk.Entry()
        self.mac_addr: tk.Entry = tk.Entry()

        # 画面生成
        self.create_view()

    """ 新規追加するホスト情報を保存 """
    def save_new_host(self, event):
        # 入力データをまとめる
        # DBから取得したものではないので、エラー回避のためにID=0を指定
        host_info = HostInfo(
            id=0,
            name=self.host_name.get(),
            ip_addr=self.ip_addr.get(),
            port=self.port.get(),
            user=self.user_name.get(),
            password=self.password.get(),
            mac_addr=self.mac_addr.get(),
        )
        # ホストを保存
        self.controller.save_host(host_info=host_info)
        # 保存後はダイアログを終了
        self.destroy()

    def create_view(self):
        # 背景色
        background_color = colors.BACKGROUND_COLOR

        # GUI生成
        self.title("【新規追加】")
        self.geometry("380x350")
        self.resizable(width=False, height=False)
        self.configure(bg=background_color)

        """ 詳細フォームの親となるフレーム """
        frame = tk.Frame(self, bg=background_color, bd=0, relief="sunken", width=350, height=350)
        frame.grid(row=0, column=0, sticky="nsew", padx=(10, 10), pady=0)
        frame.grid_propagate(False)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        frame.rowconfigure(1, weight=9)

        # 見出し領域
        host_info_label = tk.Label(frame, text="新規ホスト情報", bg=background_color,
                                   font=("メイリオ", "15", "bold"))
        host_info_label.grid(row=0, column=0, sticky="ew", pady=(5, 10))

        """ 詳細フォーム """
        host_info_frame = tk.Frame(frame, bg=background_color, bd=0, relief="sunken")
        host_info_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        host_info_frame.columnconfigure(0, weight=1)
        host_info_frame.columnconfigure(1, weight=1)
        host_info_frame.rowconfigure(0, weight=1)

        """ ホスト情報入力フォーム """
        info_frame = tk.Frame(host_info_frame, bg=background_color, bd=0, relief="sunken")
        info_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=5)
        info_frame.columnconfigure(0, weight=1)
        info_frame.rowconfigure(0, weight=1)
        info_frame.rowconfigure(1, weight=1)
        info_frame.rowconfigure(2, weight=1)
        info_frame.rowconfigure(3, weight=1)
        info_frame.rowconfigure(4, weight=1)

        frame_padx = (10, 0)
        """ ホスト名 """
        name_frame = tk.Frame(info_frame, bg=background_color, bd=0, relief="sunken")
        name_frame.grid(row=0, column=0, sticky="nsew", padx=frame_padx)
        name_frame.columnconfigure(0, weight=0)
        name_frame.columnconfigure(1, weight=1)
        name_frame.rowconfigure(0, weight=1)

        host_name_label = tk.Label(name_frame, text="ホスト名", bg=background_color, width=10, anchor="w")
        host_name_label.grid(row=0, column=0, sticky="w")
        self.host_name = tk.Entry(name_frame, font=("MSゴシック", "10", "bold"))
        self.host_name.grid(row=0, column=1, sticky="ew", ipady=4)

        """ IP / Port """
        ip_port_frame = tk.Frame(info_frame, bg=background_color, bd=0, relief="sunken")
        ip_port_frame.grid(row=1, column=0, sticky="nsew")
        ip_port_frame.columnconfigure(0, weight=1)
        ip_port_frame.columnconfigure(1, weight=2)
        ip_port_frame.rowconfigure(0, weight=1)

        # IPアドレス
        ip_addr_frame = tk.Frame(ip_port_frame, bg=background_color, bd=0, relief="sunken")
        ip_addr_frame.grid(row=0, column=0, sticky="nsew", padx=frame_padx)
        ip_addr_frame.columnconfigure(0, weight=0)
        ip_addr_frame.columnconfigure(1, weight=1)
        ip_addr_frame.rowconfigure(0, weight=1)

        ip_addr_label = tk.Label(ip_addr_frame, text="IPアドレス", bg=background_color, width=10, anchor="w")
        ip_addr_label.grid(row=0, column=0, sticky="w")
        self.ip_addr = tk.Entry(ip_addr_frame, font=("MSゴシック", "10", "bold"))
        self.ip_addr.grid(row=0, column=1, sticky="ew", ipady=4, ipadx=10)

        # ポート番号
        port_frame = tk.Frame(ip_port_frame, bg=background_color, bd=0, relief="sunken")
        port_frame.grid(row=0, column=1, sticky="nsew")
        port_frame.columnconfigure(0, weight=0)
        port_frame.columnconfigure(1, weight=1)
        port_frame.rowconfigure(0, weight=1)

        port_label = tk.Label(port_frame, text="ポート番号", bg=background_color, width=8, anchor="w")
        port_label.grid(row=0, column=0, sticky="w", padx=frame_padx)
        self.port = self.widgets.port_entry(port_frame, max_length=5, placeholder="22")
        self.port.grid(row=0, column=1, sticky="ew", padx=(5, 0), ipady=4)

        """ ユーザー名 """
        user_frame = tk.Frame(info_frame, bg=background_color, bd=0, relief="sunken")
        user_frame.grid(row=2, column=0, sticky="nsew", padx=frame_padx)
        user_frame.columnconfigure(0, weight=0)
        user_frame.columnconfigure(1, weight=1)
        user_frame.rowconfigure(0, weight=1)

        user_label = tk.Label(user_frame, text="ユーザー名", bg=background_color, width=10, anchor="w")
        user_label.grid(row=0, column=0, sticky="w")
        self.user_name = tk.Entry(user_frame, font=("MSゴシック", "10", "bold"))
        self.user_name.grid(row=0, column=1, sticky="ew", ipady=4)

        """ パスワード """
        password_frame = tk.Frame(info_frame, bg=background_color, bd=0, relief="sunken")
        password_frame.grid(row=3, column=0, sticky="nsew", padx=frame_padx)
        password_frame.columnconfigure(0, weight=0)
        password_frame.columnconfigure(1, weight=1)
        password_frame.rowconfigure(0, weight=1)

        password_label = tk.Label(password_frame, text="パスワード", bg=background_color, width=10, anchor="w")
        password_label.grid(row=0, column=0, sticky="w")
        self.password = tk.Entry(password_frame, font=("MSゴシック", "10", "bold"), show="*")
        self.password.grid(row=0, column=1, sticky="ew", ipady=4)

        """ MACアドレス """
        mac_addr_frame = tk.Frame(info_frame, bg=background_color, bd=0, relief="sunken")
        mac_addr_frame.grid(row=4, column=0, sticky="nsew", padx=frame_padx)
        mac_addr_frame.columnconfigure(0, weight=0)
        mac_addr_frame.columnconfigure(1, weight=1)
        mac_addr_frame.rowconfigure(0, weight=1)

        mac_addr_label = tk.Label(mac_addr_frame, text="MACアドレス", bg=background_color, width=10, anchor="w")
        mac_addr_label.grid(row=0, column=0, sticky="w")
        self.mac_addr = tk.Entry(mac_addr_frame, font=("MSゴシック", "10", "bold"))
        self.mac_addr.grid(row=0, column=1, sticky="ew", ipady=4)

        """ ボタン表示 """
        button_frame = tk.Frame(frame, bg=background_color, bd=0, relief="sunken")
        button_frame.grid(row=2, column=0, sticky="nsew", padx=frame_padx, pady=(20, 10))
        button_frame.columnconfigure(0, weight=1)

        save_btn = tk.Button(button_frame, text="保存")
        save_btn.bind("<Button-1>", self.save_new_host)
        save_btn.grid(row=0, column=0, sticky="nsew")
