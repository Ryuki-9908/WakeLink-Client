import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    LOG_DIR = Path(os.getcwd()).joinpath("logs")
    DB_PATH: str = "./db/host.sqlite3"
    DB_MIGRATIONS_PATH = Path(os.getcwd()).joinpath("db", "migrations")
    HOST_TABLE: str = "my_host"
    IMG_PATH = Path(os.getcwd()).joinpath("resources", "images")
    SEND_PING_FILE = Path(os.getcwd()).joinpath("utils", "scan.py")
    SETTING_INI = Path(os.getcwd()).joinpath("common", "setting.ini")
    SSH_TERMINAL_FILE = Path(os.getcwd()).joinpath("utils", "ssh_terminal.py")
    ENCRYPT_KEY_PATH = Path.home().joinpath(".WakeLink-Client", "keyfile")
    ENCRYPT_KEY_FILE = "master_encrypt.key"
