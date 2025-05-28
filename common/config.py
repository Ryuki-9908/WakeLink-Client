import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    DB_PATH: str = "./db/host.sqlite3"
    HOST_TABLE: str = "my_host"
    IMG_PATH = os.path.join(os.getcwd(), "resources", "images")
    SEND_PING_FILE = os.path.join(os.getcwd(), "utils", "send_ping.py")
    SETTING_INI = os.path.join(os.getcwd(), "common", "setting.ini")
    SSH_TERMINAL_FILE = os.path.join(os.getcwd(), "utils", "ssh_terminal.py")
