import argparse
import subprocess
import platform


def ping(host):
    system = platform.system()
    if system == "Windows":
        cmd = ["ping", "-n", "1", host]
    else:
        cmd = ["ping", "-c", "1", host]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ip")
    args = parser.parse_args()

    if ping(args.ip):
        print(f"{args.ip} is reachable")
        exit(0)  # 成功は0
    else:
        print(f"{args.ip} is unreachable")
        exit(1)  # 失敗は1


if __name__ == "__main__":
    main()
