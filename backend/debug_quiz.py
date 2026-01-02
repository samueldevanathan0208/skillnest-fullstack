import requests
import json

url = "http://127.0.0.1:8000/create_quiz"
data = {
    "user_id": 15,
    "quiz_id": "html",
    "score": 100,
    "attempt_date": "2025-01-01"
}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")
except Exception as e:
    print(f"Error: {e}")
