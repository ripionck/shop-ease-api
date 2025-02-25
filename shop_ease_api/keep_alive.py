import time
import requests
from datetime import datetime


URL = "https://shop-ease-3oxf.onrender.com"
INTERVAL = 30


def ping_server():
    while True:
        try:
            response = requests.get(URL, timeout=10)
            if response.status_code == 200:
                print(
                    f"[{datetime.now()}] Ping successful - Status Code: {response.status_code}")
            else:
                print(
                    f"[{datetime.now()}] Ping failed - Status Code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"[{datetime.now()}] Ping failed: {str(e)}")
        time.sleep(INTERVAL)


if __name__ == "__main__":
    print("Starting server pinger...")
    ping_server()
