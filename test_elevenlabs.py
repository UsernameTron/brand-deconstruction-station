import os
import requests
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("ELEVENLABS_API_KEY")
headers = {"xi-api-key": api_key}
try:
    r = requests.get("https://api.elevenlabs.io/v1/voices", headers=headers, timeout=10)
    r.raise_for_status()
    print("✅ ElevenLabs API key works. Voices:", [v["name"] for v in r.json()["voices"]])
except Exception as e:
    print("❌ ElevenLabs API key failed:", e)
