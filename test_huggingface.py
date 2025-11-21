import os
import requests
from dotenv import load_dotenv
load_dotenv()

token = os.getenv("HUGGINGFACE_API_TOKEN")
headers = {"Authorization": f"Bearer {token}"}
try:
    r = requests.get("https://huggingface.co/api/whoami-v2", headers=headers, timeout=10)
    r.raise_for_status()
    print("✅ Hugging Face API token works. User:", r.json().get("name"))
except Exception as e:
    print("❌ Hugging Face API token failed:", e)
