from cryptography.fernet import Fernet
from crypto.key_manager import KeyManager


class FernetCipher:
    def __init__(self):
        self.__key = KeyManager().load_seed()

    def encrypt_data(self, data: str) -> str:
        fernet = Fernet(self.__key)
        encrypted = fernet.encrypt(data.encode())
        return encrypted.decode()

    def decrypt_data(self, enc_data: str) -> str:
        fernet = Fernet(self.__key)
        decrypted = fernet.decrypt(enc_data.encode())
        return decrypted.decode()
