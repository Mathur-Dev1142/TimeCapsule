import httpx
import os
from dotenv import load_dotenv

load_dotenv()

token = os.environ["WIKIMEDIA_ACCESS_TOKEN"]

headers = {
    "Authorization": f"Bearer {token}",
    "User-Agent": "TimeCapsule/1.0 (deepmat465@gmail.com)"
    }

url = "https://api.wikimedia.org/feed/v1/wikipedia/en/onthisday/all/07/23"

response = httpx.get(url, headers=headers)

print("Status code:", response.status_code)
print(response.json())