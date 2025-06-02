# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

from ui import MainWindow
from db.sqlite_manager import SQLiteManager
from crypto.key_manager import KeyManager


if __name__ == "__main__":
    # 暗号鍵生成
    KeyManager().gen_fernet_key()
    # DBの確認および生成
    SQLiteManager()
    # メイン画面
    app = MainWindow()
    app.mainloop()
