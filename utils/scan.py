import argparse
import socket
import subprocess
import platform


def ping(host):
    system = platform.system()
    if system == "Windows":
        cmd = ["ping", "-n", "1", host]
    else:
        cmd = ["ping", "-c", "1", host]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=2)
    return result.returncode == 0

def check_host(host, port, timeout=1):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, socket.error):
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip")
    parser.add_argument("--port", type=int)
    args = parser.parse_args()

    if check_host(args.ip, args.port):
        print(f"{args.ip} is reachable")
        exit(0)  # 成功は0
    else:
        print(f"{args.ip} is unreachable")
        exit(1)  # 失敗は1


if __name__ == "__main__":
    main()
