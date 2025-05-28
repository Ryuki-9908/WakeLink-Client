from dataclasses import dataclass


@dataclass(frozen=True)
class DialogKey:
    key: str
    dialog_id: str


""" ダイアログ管理 """
class DialogManager:
    def __init__(self):
        self._dialogs = {}

    def show_dialog(self, parent, key: DialogKey, create_dialog_fn):
        if key in self._dialogs and self._dialogs[key].winfo_exists():
            self._dialogs[key].lift()
            return

        dialog = create_dialog_fn(parent)
        dialog.protocol("WM_DELETE_WINDOW", lambda: self._on_close(key))
        self._dialogs[key] = dialog

    def _on_close(self, key: DialogKey):
        if key in self._dialogs:
            self._dialogs[key].destroy()
            del self._dialogs[key]


# 各画面で共通のインスタンスを使用する
dialog_manager = DialogManager()
