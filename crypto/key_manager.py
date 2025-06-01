import os
from cryptography.fernet import Fernet
from common.context import Context


class KeyManager:
    def __init__(self):
        context = Context(class_name=self.__class__.__name__)
        self.logger = context.logger
        self.key_path = context.config.ENCRYPT_KEY_PATH
        self.key_file = self.key_path.joinpath(context.config.ENCRYPT_KEY_FILE)

    def gen_fernet_key(self):
        if not self.key_file.exists():
            self.key_path.mkdir(parents=True, exist_ok=True)
            key = Fernet.generate_key()
            # ファイルに書き込み
            with open(self.key_file, "wb") as f:
                f.write(key)

            # パーミッション制限付与
            os.chmod(self.key_file, 0o600)

    def load_seed(self):
        if not self.key_file.exists():
            raise FileNotFoundError("Seed file not found.")

        with open(self.key_file, "rb") as f:
            return f.read()
