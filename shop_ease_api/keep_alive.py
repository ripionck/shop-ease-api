import time
import requests
from datetime import datetime

URL = "https://shop-ease-3oxf.onrender.com"
INTERVAL = 25 * 60


def ping_server():
    while True:
        try:
            response = requests.get(URL, timeout=10)
            print(f"[{datetime.now()}] Status: {response.status_code}")
        except Exception as e:
            print(f"[{datetime.now()}] Error: {e}")
        time.sleep(INTERVAL)


if __name__ == "__main__":
    ping_server()
