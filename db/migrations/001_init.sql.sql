-- スキーマバージョン管理テーブル
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER NOT NULL,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO schema_version (version) VALUES (1);

-- ホスト情報テーブル
CREATE TABLE IF NOT EXISTS my_host (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    host TEXT,
    ip_addr TEXT,
    port TEXT,
    user TEXT,
    password TEXT,
    mac_addr TEXT
);
