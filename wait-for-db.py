#!/usr/bin/env python3
import sys
import socket
import time
import os

def wait_for(host, port, timeout=3):
    while True:
        try:
            with socket.create_connection((host, int(port)), timeout=timeout):
                return
        except Exception:
            print(f"Waiting for {host}:{port} ...")
            time.sleep(1)

def main():
    if len(sys.argv) < 3:
        print("Usage: wait-for-db.py host port -- command ...")
        sys.exit(1)

    host = sys.argv[1]
    port = sys.argv[2]

    # find '--' separator to get the command to exec
    cmd = []
    if '--' in sys.argv:
        idx = sys.argv.index('--')
        cmd = sys.argv[idx+1:]
    else:
        cmd = ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

    wait_for(host, port)
    print(f"{host}:{port} is available — launching: {' '.join(cmd)}")
    os.execvp(cmd[0], cmd)

if __name__ == "__main__":
    main()
