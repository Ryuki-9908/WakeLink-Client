from ui import MainWindow
from db.sqlite_repository import SQLiteRepository


if __name__ == "__main__":
    SQLiteRepository()
    app = MainWindow()
    app.mainloop()
