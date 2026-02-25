import threading
import socket
import time

import uvicorn
import webview

from backend import app

def get_free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port

def run_server(port: int):
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    server.run()

def wait_port(port: int, timeout: float = 5.0):
    end = time.time() + timeout
    while time.time() < end:
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", port)) == 0:
                return
        time.sleep(0.05)
    raise RuntimeError("本地服务启动超时")

if __name__ == "__main__":
    port = get_free_port()

    t = threading.Thread(target=run_server, args=(port,), daemon=True)
    t.start()
    wait_port(port)

    url = f"http://127.0.0.1:{port}/"
    webview.create_window("My FastAPI Desktop App", url, width=1000, height=700)
    webview.start()