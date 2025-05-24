import os
import tkinter as tk
from tkinter import PhotoImage
from common.base_component import BaseComponent

status_colors = {
    "online": "green",
    "offline": "gray"
}


class HostListFrame(tk.Frame):
    def __init__(self, parent, hosts, select_callback=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.hosts = hosts
        self.host_frames = []
        self.selected_frame = None
        self.select_callback = select_callback

        # アイコン画像の入ったフォルダパスを取得
        component = BaseComponent(class_name=self.__class__.__name__)
        img_path = component.config.IMG_PATH

        # アイコン画像の読み込み
        self.icon_online = PhotoImage(file=os.path.join(img_path, "pc_online.png"))
        self.icon_offline = PhotoImage(file=os.path.join(img_path, "pc_offline.png"))

        self.canvas = tk.Canvas(self, borderwidth=0, background="#ffffff")
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, background="#ffffff")

        self.scrollable_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        self.render_devices(self.hosts)

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.scrollable_window, width=event.width)

    def create_device_item(self, parent, host):
        frame = tk.Frame(parent, bg="white")
        frame.pack(fill="x", padx=5, pady=0)

        def on_click(event):
            if self.selected_frame:
                self.deselect_frame(self.selected_frame)
            self.select_frame(frame)
            if self.select_callback:
                self.select_callback(host)

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

        if name:
            name_label = tk.Label(text_frame, text=name, bg="white", font=("Arial", 12, "bold"))
            name_label.pack(anchor="w")
            name_label.bind("<Button-1>", on_click)

            ip_label = tk.Label(text_frame, text=ip, bg="white", font=("Arial", 10))
            ip_label.pack(anchor="w")
            ip_label.bind("<Button-1>", on_click)
        else:
            ip_label = tk.Label(text_frame, text=ip, bg="white", font=("Arial", 12))
            ip_label.pack(anchor="w")
            ip_label.bind("<Button-1>", on_click)

        status_canvas = tk.Canvas(frame, width=20, height=20, bg="white", highlightthickness=0)
        status_canvas.pack(side="left", padx=10)
        color = status_colors.get(host.get("status", "offline"), "gray")
        status_canvas.create_oval(5, 5, 15, 15, fill=color, outline=color)
        status_canvas.bind("<Button-1>", on_click)

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

    def render_devices(self, hosts):
        # 既存のホスト行を削除
        for f in self.host_frames:
            f.destroy()
        self.host_frames.clear()

        for device in hosts:
            frame = self.create_device_item(self.scrollable_frame, device)
            self.host_frames.append(frame)

    def update_devices(self, new_show_hosts):
        """外部から呼び出してホスト一覧を更新"""
        self.hosts = new_show_hosts
        self.render_devices(new_show_hosts)
