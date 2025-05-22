from ui import MainLayout
from db.sqlite_repository import SQLiteRepository


if __name__ == "__main__":
    SQLiteRepository()
    app = MainLayout()
    app.mainloop()
