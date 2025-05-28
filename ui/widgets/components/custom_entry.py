import tkinter as tk


class CustomEntry(tk.Entry):
    def __init__(self, master, font=None, font_color="black", max_length=None, *args, **kwargs):
        super().__init__(master, font=font)

        # 設定値
        self.placeholder = ""
        self.placeholder_color = ""
        self.default_fg = self['fg']
        self.max_length = max_length

        # 初期化
        self.validate = None
        self.valid_cmd = None
        self._has_placeholder = False
        self.font_color = font_color

        # バインド
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
        self.bind("<KeyRelease>", self._on_key_release)

    def insert(self, index, string):
        self.configure(validate='none')
        self.config(fg=self.font_color)
        super().insert(index, string)
        if self.validate:
            self.configure(validate=self.validate, validatecommand=self.valid_cmd)

    def set_validation(self, validate, valid_cmd):
        self.validate = validate
        self.valid_cmd = valid_cmd
        self.configure(validate=self.validate, validatecommand=self.valid_cmd)

    def set_placeholder(self, placeholder, placeholder_color):
        self.placeholder = placeholder
        self.placeholder_color = placeholder_color

        # insert処理のためにvalidateを一時オフ
        self.configure(validate='none')
        self.insert(0, placeholder)
        self.config(fg=self.placeholder_color)
        self._has_placeholder = True
        # insert処理後にvalidateを有効
        if self.validate:
            self.configure(validate=self.validate, validatecommand=self.valid_cmd)

    def _clear_placeholder(self):
        if self._has_placeholder:
            self.delete(0, tk.END)
            self.config(fg=self.default_fg)
            self._has_placeholder = False

    def _on_focus_in(self, event):
        self._clear_placeholder()

    def _on_focus_out(self, event):
        if not self.get():
            self.set_placeholder(self.placeholder, self.placeholder_color)

    def _on_key_release(self, event):
        if self.max_length and not self._has_placeholder:
            current = self.get()
            if len(current) > self.max_length:
                self.delete(self.max_length, tk.END)
