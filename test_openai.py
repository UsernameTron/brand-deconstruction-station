import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
try:
    response = openai.models.list()
    print("✅ OpenAI API key works. Models:", [m.id for m in response.data])
except Exception as e:
    print("❌ OpenAI API key failed:", e)
