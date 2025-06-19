import requests

url = "https://dbe1-168-196-203-94.ngrok-free.app/webhook"  # reemplaza con tu URL real de ngrok
data = {
    "action": "buy",
    "sl": 3.2,
    "tp": 3.5,
    "trail": 0.3
}

response = requests.post(url, json=data)
print("Status:", response.status_code)
print("Respuesta:", response.text)