import os
import tkinter as tk
from tkinter import PhotoImage
from common.component import Component
from utils import process_type

status_colors = {
    "online": "green",
    "offline": "gray"
}


class HostListFrame(tk.Frame):
    def __init__(self, parent, host_map, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.host_map = host_map
        self.host_frames = []
        self.selected_frame = None
        self.selected_host = None
        self.callbacks = {}

        # アイコン画像の入ったフォルダパスを取得
        component = Component(class_name=self.__class__.__name__)
        img_path = component.config.IMG_PATH

        # アイコン画像の読み込み
        self.icon_online = PhotoImage(file=os.path.join(img_path, "pc_online.png"))
        self.icon_offline = PhotoImage(file=os.path.join(img_path, "pc_offline.png"))

        # ヘッダー領域
        header_frame = tk.Frame(self)
        header_frame.pack(fill="x", padx=5, pady=(5, 0))

        header_label = tk.Label(header_frame, text="ホスト一覧", font=("メイリオ", 12, "bold"))
        header_label.pack(side="left")

        add_new_button = tk.Button(header_frame, text="＋ 新規追加", command=self.on_addition, font=("メイリオ", 10))
        add_new_button.pack(side="right")
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="削除", command=self.on_right_click_delete)


        self.canvas = tk.Canvas(self, borderwidth=0, background="#ffffff")
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, background="#ffffff")

        self.scrollable_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        self.render_devices(self.host_map)

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.scrollable_window, width=event.width)

    def render_devices(self, new_show_host_map):
        # 既存のホスト行を削除
        for f in self.host_frames:
            f.destroy()
        self.host_frames.clear()

        # 選択状態をクリア
        self.selected_frame = None

        # 新しいリストを表示
        for key in new_show_host_map:
            host = new_show_host_map[key]
            frame = self.create_host_item(self.scrollable_frame, host)
            self.host_frames.append(frame)

    def create_host_item(self, parent, host):
        frame = tk.Frame(parent, bg="white")
        frame.pack(fill="x", padx=5, pady=0)

        def on_click(event):
            self.selected_host = host
            if self.selected_frame:
                self.deselect_frame(self.selected_frame)
            self.select_frame(frame)
            self.run_callback(process_type.SELECT, host)

        def on_right_click(event):
            self.selected_host = host
            if self.selected_frame:
                self.deselect_frame(self.selected_frame)
            self.select_frame(frame)
            self.context_menu.tk_popup(event.x_root, event.y_root)

        frame.bind("<Button-1>", on_click)

        icon = self.icon_online if host.get("status") == "online" else self.icon_offline
        icon_label = tk.Label(frame, image=icon, bg="white")
        icon_label.image = icon
        icon_label.pack(side="left", padx=5, pady=5)
        icon_label.bind("<Button-1>", on_click)

        text_frame = tk.Frame(frame, bg="white")
        text_frame.pack(side="left", padx=10)

        name = host.get("name", "").strip()
        ip = host.get("ip_addr", "")

        frame.bind("<Button-3>", on_right_click)
        icon_label.bind("<Button-3>", on_right_click)
        text_frame.bind("<Button-3>", on_right_click)
        if name:
            name_label = tk.Label(text_frame, text=name, bg="white", font=("Arial", 12, "bold"))
            name_label.pack(anchor="w")
            name_label.bind("<Button-1>", on_click)
            name_label.bind("<Button-3>", on_right_click)

            ip_label = tk.Label(text_frame, text=ip, bg="white", font=("Arial", 10))
            ip_label.pack(anchor="w")
            ip_label.bind("<Button-1>", on_click)
            ip_label.bind("<Button-3>", on_right_click)
        else:
            ip_label = tk.Label(text_frame, text=ip, bg="white", font=("Arial", 12))
            ip_label.pack(anchor="w")
            ip_label.bind("<Button-1>", on_click)
            ip_label.bind("<Button-3>", on_right_click)

        status_canvas = tk.Canvas(frame, width=20, height=20, bg="white", highlightthickness=0)
        status_canvas.pack(side="left", padx=10)
        color = status_colors.get(host.get("status", "offline"), "gray")
        status_canvas.create_oval(5, 5, 15, 15, fill=color, outline=color)
        status_canvas.bind("<Button-1>", on_click)
        status_canvas.bind("<Button-3>", on_right_click)

        line = tk.Frame(parent, bg="#ddd", height=1)
        line.pack(fill="x", padx=5)

        return frame

    def select_frame(self, frame):
        frame.configure(bg="#e0f0ff")
        for widget in frame.winfo_children():
            widget.configure(bg="#e0f0ff")
            if isinstance(widget, tk.Frame):
                for w in widget.winfo_children():
                    w.configure(bg="#e0f0ff")
        self.selected_frame = frame

    def deselect_frame(self, frame):
        frame.configure(bg="white")
        for widget in frame.winfo_children():
            widget.configure(bg="white")
            if isinstance(widget, tk.Frame):
                for w in widget.winfo_children():
                    w.configure(bg="white")
        self.selected_frame = None

    def update_hosts(self, new_show_host_map):
        """外部から呼び出してホスト一覧を更新"""
        self.host_map = new_show_host_map
        self.render_devices(new_show_host_map)

    def run_callback(self, process, *args, **kwargs):
        if process in self.callbacks:
            self.callbacks[process](*args, **kwargs)

    def set_callback(self, process: process_type, callback):
        self.callbacks[process] = callback

    def on_delete(self):
        self.run_callback(process_type.DELETE, self.selected_host)

    def on_right_click_delete(self):
        self.run_callback(process_type.DELETE, self.selected_host)

    def on_addition(self):
        self.run_callback(process_type.HOST_ADD)
