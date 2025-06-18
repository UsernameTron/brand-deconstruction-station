import os
from dotenv import load_dotenv
load_dotenv()

try:
    from google.generativeai.client import configure
    from google.generativeai.models import list_models
    from google.generativeai.generative_models import GenerativeModel
    api_key = os.getenv("GOOGLE_API_KEY")
    configure(api_key=api_key)
    print("Available Gemini models:")
    preferred = [
        'models/gemini-1.5-flash',
        'models/gemini-1.5-pro',
        'models/gemini-2.5-flash',
        'models/gemini-2.5-pro',
    ]
    model_name = None
    for m in list_models():
        print(f"- {m.name} (methods: {getattr(m, 'generation_methods', getattr(m, 'supported_generation_methods', []))})")
        methods = getattr(m, 'generation_methods', getattr(m, 'supported_generation_methods', []))
        # Skip deprecated models
        if 'deprecated' in getattr(m, 'description', '').lower():
            continue
        if m.name in preferred and 'generateContent' in methods:
            model_name = m.name
            break
        if not model_name and 'generateContent' in methods and 'vision' not in m.name:
            model_name = m.name
    if not model_name:
        raise Exception("No non-deprecated model supports generateContent")
    print(f"Using model: {model_name}")
    model = GenerativeModel(model_name)
    response = model.generate_content(["Hello Gemini!"])
    print("✅ Google Gemini API key works. Response:", getattr(response, 'text', response))
except Exception as e:
    print("❌ Google Gemini API key failed:", e)
