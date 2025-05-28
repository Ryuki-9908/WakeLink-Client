""" setting.ini 操作用 """
import configparser
import os


class Setting:
    def __init__(self, setting_ini):
        self.setting_ini = setting_ini
        self.setting = configparser.ConfigParser()
        self.load()

        # 存在確認するディレクトリパス
        check_dir_path = []

        for path in check_dir_path:
            # ディレクトリが存在しない場合は作成
            dir_path = os.path.dirname(path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path)

    def load(self):
        if os.path.exists(self.setting_ini):
            self.setting.read(self.setting_ini)
        else:
            raise FileNotFoundError(f"Setting file {self.setting_ini} not found.")

    def save(self):
        with open(self.setting_ini, "w") as f:
            self.setting.write(f)

    def get(self, section, key):
        return self.setting.get(section, key)

    def set(self, section, key, value):
        if not self.setting.has_section(section):
            self.setting.add_section(section)
        self.setting.set(section, key, value)
        self.save()
