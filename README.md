# 🖥️ WakeLink Client（開発中）

**WakeLink Client** は、Wake-on-LAN (WOL) と SSH を組み合わせて、家庭内・ローカルネットワーク上の複数サーバーを手軽に起動・接続できる軽量クライアントアプリです。

中古の低スペックPCでも軽快に動作するよう、Linux環境や学習コストの低減を意識して開発されています。Tkinterベースで構築されており、Pythonが動く環境なら幅広く対応可能です。

---

## 👤 開発背景

WakeLink Client は、自宅に複数台のPCやサーバーを設置する中で、省エネと効率を両立するためのクライアントツールとして開発されました。

- WOLによる電源制御とSSHによる即時接続  
- 中古・低スペックPCにLinuxを入れても快適に動作  
- Tkinter＋Python による 導入・改修の学習コストが低い構成  

これらを実現することで、誰でも手軽に自宅内ネットワークの自動化や管理ができる環境を目指しています。

---

## 🎯 主な機能

- 登録されたサーバーに対する WOL送信とSSH自動接続  
- サーバー起動状態の可視化（オンライン時は緑の〇、オフラインはグレー）  
- サーバー情報の追加・編集・削除（SQLiteベース）  
- 設定ファイル（setting.ini）による実行環境カスタマイズ（例：python / python3）  
- マルチプラットフォーム対応（Windows / Linux）  

---

## 🛣 今後の予定

- SFTP転送機能の追加  
- テーマ・配色選択（カスタマイズ性の向上）  
- マイグレーション対応（アップデートでの設定維持）  
- テスト／ドキュメントの整備  

---

## 🧱 使用技術

- Python / Tkinter  
- wakeonlan, paramiko  
- SQLite3（ローカルデータベース）
- cryptography（暗号化ライブラリ、Fernet利用）
- INI設定ファイル（configparser）  

---

## 🚀 起動方法

1. リポジトリのクローン

```bash
git clone https://github.com/Ryuki-9908/WakeLink-Client.git 
cd WakeLink-Client
```

※ 本リポジトリは読み取り専用でクローン可能ですが、変更をGitHubに反映（push）するには開発権限が必要です。

2. 仮想環境の作成と有効化

**Windows:**

```bash
python -m venv venv
.venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

3. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

4. アプリケーションの起動

```bash
python main.py
```

---

## 📂 ディレクトリ構成

```
WakeLink-Client/
├── main.py              # アプリの起動スクリプト
├── requirements.txt     # 依存ライブラリ一覧
├── setting.ini          # アプリケーション設定ファイル
├── common/              # 共通処理（設定管理・ロギングなど）
│   ├── context.py
│   ├── config.py
│   └── logger.py
├── controller/          # UI操作系の制御ロジック
│   └── dialogs/         # 各種Tkinterダイアログコントローラ
├── crypto/              # 暗号化/復号化の処理（鍵管理含む）
│   ├── fernet_cipher.py
│   ├── key_manager.py
│   └── __init__.py
├── db/                  # DBアクセス関連（DAO・マネージャ）
│   ├── dao/
│   ├── handler/
│   ├── models/
│   └── sqlite_manager.py
├── service/             # バックグラウンド処理や監視系のサービス層
├── ui/                  # UI構築（Tkinterウィジェット等）
│   └── widgets/
├── utils/               # 補助関数・定数など汎用ユーティリティ
├── resources/           # 画像・アイコンなどの静的リソース
└── .WakeLink-Client/    # ユーザー環境設定（鍵ファイル保存先など、実行後生成）
```

---

## 💬 お問い合わせ

バグ報告・機能提案などは Issues にてお知らせください。
