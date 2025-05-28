import argparse
import threading
import paramiko
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory


def interactive_shell(ip_addr, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=ip_addr, username=user, password=password)

    chan = client.invoke_shell()
    history = InMemoryHistory()
    session = PromptSession(history=history)

    def recv_loop():
        while True:
            if chan.recv_ready():
                data = chan.recv(1024)
                print(data.decode(errors="ignore"), end="", flush=True)

    thread = threading.Thread(target=recv_loop, daemon=True)
    thread.start()

    try:
        while True:
            cmd = session.prompt("> ")  # 入力補完・履歴対応
            chan.send(cmd + "\n")
    except (KeyboardInterrupt, EOFError):
        print("\n終了します")
    finally:
        chan.close()
        client.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip")
    parser.add_argument("--port", type=int)
    parser.add_argument("--user")
    parser.add_argument("--pwd")
    args = parser.parse_args()

    if interactive_shell(args.ip, args.user, args.pwd):
        print(f"{args.ip} is reachable")
        exit(0)  # 成功は0
    else:
        print(f"{args.ip} is unreachable")
        exit(1)  # 失敗は1


if __name__ == "__main__":
    print("ssh_terminal run.")
    main()
