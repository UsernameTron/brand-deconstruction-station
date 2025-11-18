#!/usr/bin/env python3
"""Test Vertex AI Imagen setup"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("Google Cloud Configuration Test")
print("=" * 60)

# Check environment variables
project = os.getenv('GOOGLE_CLOUD_PROJECT', 'Not set')
location = os.getenv('GOOGLE_CLOUD_LOCATION', 'Not set')
credentials = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'Not set')
google_api_key = os.getenv('GOOGLE_API_KEY', 'Not set')

print(f"\n1. Environment Variables:")
print(f"   GOOGLE_CLOUD_PROJECT: {project}")
print(f"   GOOGLE_CLOUD_LOCATION: {location}")
print(f"   GOOGLE_APPLICATION_CREDENTIALS: {credentials}")
print(f"   GOOGLE_API_KEY: {google_api_key[:20]}..." if google_api_key != 'Not set' else "   GOOGLE_API_KEY: Not set")

# Check if Vertex AI libraries are installed
print(f"\n2. Library Status:")
try:
    from google.cloud import aiplatform
    from vertexai.preview.vision_models import ImageGenerationModel
    import vertexai
    print("   ✅ Vertex AI libraries installed")
except ImportError as e:
    print(f"   ❌ Vertex AI libraries NOT installed: {e}")
    print("   Run: pip install google-cloud-aiplatform")

# Test Vertex AI initialization
print(f"\n3. Vertex AI Initialization Test:")
try:
    import vertexai
    vertexai.init(project="avatar-449218", location="us-central1")
    print("   ✅ Vertex AI initialized successfully")
    
    # Try to load the model
    from vertexai.preview.vision_models import ImageGenerationModel
    model = ImageGenerationModel.from_pretrained("imagegeneration@006")
    print("   ✅ Imagen model loaded successfully")
    
except Exception as e:
    print(f"   ❌ Vertex AI initialization failed: {e}")
    print("\n   To fix this:")
    print("   1. Install gcloud CLI")
    print("   2. Run: gcloud auth application-default login")
    print("   3. Select your Google account with access to project avatar-449218")
    
# Test the media generator
print(f"\n4. Media Generator Test:")
try:
    from media_generator import GoogleMediaGenerator
    generator = GoogleMediaGenerator()
    print(f"   Mock mode: {generator.mock_mode}")
    
    if not generator.mock_mode:
        print("   ✅ Real image generation available!")
    else:
        print("   ⚠️  Still in mock mode")
        
except Exception as e:
    print(f"   ❌ Media generator error: {e}")

print("\n" + "=" * 60)
