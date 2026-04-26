import requests
import json

r1 = requests.post("http://127.0.0.1:8000/api/v1/auth/login", json={"username": "admin", "password": "admin"})
token = r1.json()["access_token"]

files = {"file": ("sample_sar_transactions.csv", open("../Frontend/sample_sar_transactions.csv", "rb"))}
headers = {"Authorization": f"Bearer {token}"}
r2 = requests.post("http://127.0.0.1:8000/api/v1/analyze/csv", files=files, headers=headers)
print("Status:", r2.status_code)
print("Response:", r2.text)
