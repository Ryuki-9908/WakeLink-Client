import copy
import subprocess
import threading
from common.context import Context
import time


class HostMonitor:
    def __init__(self, master, update_ui_callback):
        self.master = master
        self.update_ui_callback = update_ui_callback
        self._stop_event = threading.Event()

        context = Context(class_name=self.__class__.__name__)
        self.logger = context.logger
        self.python_cmd = context.setting.get(section="Settings", key="python_cmd")
        self.scan_python = context.config.SEND_PING_FILE

        # タイマー初期化
        self.buf_time = time.time()
        # 状態確認スレッド制御用のフラグ
        self.isCheck = False

        """ 監視サービス起動 """
        self.thread_lock = threading.Lock()  # スレッドロックを使用

    def start(self, interval=10, attempts=3):
        self._stop_event.clear()
        self._loop(interval, attempts)

    def stop(self):
        self._stop_event.set()

    def _loop(self, interval=10, attempts=3):
        if self._stop_event.is_set():
            return
        tmp = time.time()
        if (tmp - self.buf_time) >= interval and not self.isCheck:
            # 前回の確認から10秒以上経っており、確認処理中でない場合
            if self.thread_lock.acquire(blocking=False):  # スレッドロックをチェック
                try:
                    threading.Thread(target=self.check_host_status, args=(attempts,), daemon=True).start()
                finally:
                    self.thread_lock.release()  # スレッドロックを解除

        threading.Timer(interval, self._loop, args=(interval, attempts)).start()

    """ ホストの状態確認処理 """
    def check_host_status(self, attempts: int = 3):
        # 差分マージ用の辞書作成（新しい状態のみ）
        updated_map = {}
        self.isCheck = True

        # リスト更新判断のために複製
        copy_show_host_map = copy.deepcopy(self.master.show_host_map)
        try:
            # リストに含まれるホストの状態を確認
            for key, host in self.master.show_host_map.items():
                is_online = False
                for _ in range(attempts):
                    # IPの入力が無い場合は即抜ける
                    if len(host['ip_addr']) == 0: break
                    try:
                        # 入力されているポート番号を指定する。無ければデフォルト"22"
                        ssh_port = str(host['port']) if host.get('port') else "22"

                        # 死活監視
                        response = subprocess.run(
                            [self.python_cmd, self.scan_python, "--ip", host['ip_addr'], "--port", ssh_port],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                        )
                        if response.returncode == 0:
                            is_online = True
                    except Exception as e:
                        self.logger.error(e)

                # is_online判定後、差分チェック
                new_status = "online" if is_online else "offline"
                old_status = copy_show_host_map[key]['status']

                if new_status != old_status:
                    updated_map[key] = {**host, 'status': new_status}

            # 複製しておいたリストと差分がある場合はリストを更新
            if updated_map and self.update_ui_callback:
                self.update_ui_callback(updated_map)

        except Exception as e:
            self.logger.error(e)
        finally:
            # フラグを戻して終了
            self.isCheck = False
            self.buf_time = time.time()
