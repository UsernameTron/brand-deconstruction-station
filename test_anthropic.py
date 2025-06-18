import os
from dotenv import load_dotenv
load_dotenv()
try:
    import anthropic
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=10,
        messages=[{"role": "user", "content": "Hello, Claude!"}]
    )
    print("✅ Anthropic API key works. Response:", response.content)
except Exception as e:
    print("❌ Anthropic API key failed:", e)
