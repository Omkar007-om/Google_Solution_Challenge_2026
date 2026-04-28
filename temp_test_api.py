import urllib.request
import urllib.error
import json

data = json.dumps({"input_data": {"user_id": "USR-001", "transactions": []}}).encode("utf-8")
req = urllib.request.Request("http://localhost:8000/api/v1/analyze", data=data, headers={"Content-Type": "application/json"})

try:
    with urllib.request.urlopen(req) as response:
        print("Status Code:", response.getcode())
        print("Response:", response.read().decode("utf-8"))
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code)
    print("Response:", e.read().decode("utf-8"))
except Exception as e:
    print("Error:", e)
