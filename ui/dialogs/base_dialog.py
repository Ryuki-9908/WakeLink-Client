import tkinter as tk
from common.context import Context


class BaseDialog(tk.Toplevel):
    def __init__(self, parent, class_name):
        super().__init__(parent)
        self.context = Context(class_name)
        self.logger = self.context.logger
