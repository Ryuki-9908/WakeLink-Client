import tkinter as tk
from common.component import Component


class BaseDialog(tk.Toplevel):
    def __init__(self, parent, class_name):
        super().__init__(parent)
        self.component = Component(class_name)
