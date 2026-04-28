import requests
files = {"file": ("sample_sar_transactions.csv", open("../Frontend/sample_sar_transactions.csv", "rb"))}
r2 = requests.post("http://127.0.0.1:8000/api/v1/analyze/csv", files=files)
print("Status:", r2.status_code)
print("Response:", r2.text)
