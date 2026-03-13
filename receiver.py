import requests

RASPBERRY_PI_IP = "192.168.1.100"
PORT = 5000

url = f"http://{RASPBERRY_PI_IP}:{PORT}/set_boolean"

data = {
    "value": True
}

try:
    response = requests.post(url, json=data, timeout=5)
    print("Status code:", response.status_code)
    print("Response:", response.json())
except requests.exceptions.RequestException as e:
    print("Error:", e)
