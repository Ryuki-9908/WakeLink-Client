import re
from ui.widgets.components.custom_entry import CustomEntry


class MainWidgets:
    def __init__(self, master):
        self.master = master

    def port_entry(self, root=None, max_length=5):
        def limit_input(max_value):
            def validate_input(new_value):
                if new_value == "":
                    return True
                if re.fullmatch(r"[0-9]*", new_value) is not None:
                    return len(new_value) <= max_value
                return False
            return validate_input

        # 引数rootがNoneであれば初期化時にセットしたmasterの上に表示する。
        parent = root or self.master
        valid_cmd = (parent.register(limit_input(max_value=max_length)), "%P")

        entry = CustomEntry(parent, font=("MSゴシック", "10", "bold"))
        entry.set_placeholder(placeholder="port:22", placeholder_color="gray")
        entry.set_validation(validate="key", valid_cmd=valid_cmd)
        return entry
