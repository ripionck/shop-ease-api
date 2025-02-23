import time
import requests
from django.conf import settings

URL = "https://shop-ease-3oxf.onrender.com"
INTERVAL = 30


def ping_server():
    while True:
        try:
            response = requests.get(URL)
            print(f"Ping successful - Status Code: {response.status_code}")
        except Exception as e:
            print(f"Ping failed: {str(e)}")
        time.sleep(INTERVAL)


if __name__ == "__main__":
    ping_server()
