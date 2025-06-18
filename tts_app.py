#!/usr/bin/env python3
"""
🎤 Neural Voice Synthesis Terminal
AI-Powered Text-to-Speech Engine with Dual API Support
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
from dotenv import load_dotenv
import json
import time
import tempfile
import io
from datetime import datetime
import threading
import base64
import requests

# Load environment variables
load_dotenv()  # This will load from .env file
load_dotenv('tts.env')  # This will also load from tts.env if it exists

app = Flask(__name__)

class VoiceSynthesisEngine:
    """Multi-AI voice synthesis engine with support for multiple providers"""
    
    def __init__(self):
        # Try to get API keys from environment variables first, then from .env files
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.huggingface_token = os.getenv('HUGGINGFACE_API_TOKEN')
        self.elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
        
        # Filter out placeholder values
        api_keys = {
            'openai': self.openai_api_key,
            'anthropic': self.anthropic_api_key,
            'google': self.google_api_key,
            'huggingface': self.huggingface_token,
            'elevenlabs': self.elevenlabs_api_key
        }
        
        for service, key in api_keys.items():
            if key and key.startswith('your-'):
                setattr(self, f'{service}_api_key' if service != 'huggingface' else 'huggingface_token', None)
        
        print("🔍 API Key Status:")
        print(f"  OpenAI: {'✅' if self.openai_api_key else '❌'}")
        print(f"  Anthropic: {'✅' if self.anthropic_api_key else '❌'}")
        print(f"  Google: {'✅' if self.google_api_key else '❌'}")
        print(f"  Hugging Face: {'✅' if self.huggingface_token else '❌'}")
        print(f"  ElevenLabs: {'✅' if self.elevenlabs_api_key else '❌'}")
        
        # Initialize OpenAI client
        self.openai_client = None
        if self.openai_api_key:
            try:
                import openai
                self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
                print("✅ OpenAI TTS client initialized")
            except ImportError:
                print("⚠️  OpenAI package not available")
            except Exception as e:
                print(f"⚠️  OpenAI client initialization failed: {e}")
        else:
            print("⚠️  OpenAI API key not found in environment")
        
        # Initialize Google TTS client
        self.google_available = False
        if self.google_api_key:
            try:
                # Google TTS would require google-cloud-texttospeech
                print("✅ Google API key available (requires google-cloud-texttospeech)")
                self.google_available = True
            except Exception as e:
                print(f"⚠️  Google TTS initialization failed: {e}")
        else:
            print("⚠️  Google API key not found in environment")
        
        # Initialize Hugging Face client
        self.huggingface_available = False
        if self.huggingface_token:
            try:
                # Hugging Face TTS would use transformers library
                print("✅ Hugging Face token available")
                self.huggingface_available = True
            except Exception as e:
                print(f"⚠️  Hugging Face initialization failed: {e}")
        else:
            print("⚠️  Hugging Face token not found in environment")
        
        # Initialize ElevenLabs client
        self.elevenlabs_available = False
        if self.elevenlabs_api_key:
            try:
                import requests
                # Test ElevenLabs connection
                headers = {"xi-api-key": self.elevenlabs_api_key}
                response = requests.get("https://api.elevenlabs.io/v1/voices", headers=headers, timeout=10)
                if response.status_code == 200:
                    self.elevenlabs_available = True
                    print("✅ ElevenLabs API client initialized")
                else:
                    print(f"⚠️  ElevenLabs API test failed: {response.status_code}")
            except Exception as e:
                print(f"⚠️  ElevenLabs client initialization failed: {e}")
        else:
            print("⚠️  ElevenLabs API key not found in environment")
    
    def generate_openai_speech(self, text, voice="alloy", model="tts-1", speed=1.0):
        """Generate speech using OpenAI TTS API"""
        if not self.openai_client:
            raise Exception("OpenAI client not available")
        
        try:
            response = self.openai_client.audio.speech.create(
                model=model,
                voice=voice,
                input=text,
                speed=speed
            )
            
            # Create temporary file for audio
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            response.stream_to_file(temp_file.name)
            
            return {
                'status': 'success',
                'file_path': temp_file.name,
                'service': 'openai',
                'voice': voice,
                'model': model,
                'speed': speed,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"OpenAI TTS generation failed: {str(e)}")
    
    def generate_elevenlabs_speech(self, text, voice_id="rachel", stability=0.5, clarity=0.5):
        """Generate speech using ElevenLabs API"""
        if not self.elevenlabs_available:
            raise Exception("ElevenLabs client not available")
        
        try:
            import requests
            
            # Voice ID mapping
            voice_mapping = {
                "rachel": "21m00Tcm4TlvDq8ikWAM",
                "drew": "29vD33N1CtxCmqQRPOHJ",
                "clyde": "2EiwWnXFnvU5JabPnv8n",
                "paul": "5Q0t7uMcjvnagumLfvZi",
                "domi": "AZnzlk1XvdvUeBnXmlld",
                "custom1": "rOcOyFPuYX8nT1BUDAok"  # Added custom voice
            }
            
            actual_voice_id = voice_mapping.get(voice_id, voice_id)
            
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{actual_voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": stability,
                    "similarity_boost": clarity
                }
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Create temporary file for audio
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_file.write(response.content)
            temp_file.close()
            
            return {
                'status': 'success',
                'file_path': temp_file.name,
                'service': 'elevenlabs',
                'voice': voice_id,
                'stability': stability,
                'clarity': clarity,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"ElevenLabs TTS generation failed: {str(e)}")
    
    def get_available_services(self):
        """Get status of available TTS services"""
        return {
            'openai': {
                'available': self.openai_client is not None,
                'voices': ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'],
                'models': ['tts-1', 'tts-1-hd'],
                'description': 'OpenAI TTS with neural voices'
            },
            'elevenlabs': {
                'available': self.elevenlabs_available,
                'voices': ['rachel', 'drew', 'clyde', 'paul', 'domi', 'custom1'],  # Added custom1
                'description': 'ElevenLabs premium voice synthesis'
            },
            'google': {
                'available': self.google_available,
                'voices': ['en-US-Wavenet-A', 'en-US-Wavenet-B', 'en-US-Wavenet-C'],
                'description': 'Google Cloud Text-to-Speech (requires setup)'
            },
            'huggingface': {
                'available': self.huggingface_available,
                'voices': ['facebook/fastspeech2-en-200_speaker-cv4'],
                'description': 'Hugging Face TTS models (requires setup)'
            },
            'anthropic': {
                'available': self.anthropic_api_key is not None,
                'description': 'Anthropic Claude (text generation only)'
            }
        }

# Initialize synthesis engine
synthesis_engine = VoiceSynthesisEngine()

@app.route('/')
def index():
    """Main TTS interface"""
    return render_template('tts_interface.html')

@app.route('/favicon.ico')
def favicon():
    """Serve cyberpunk-themed favicon"""
    favicon_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
        <rect fill="#000011" width="32" height="32"/>
        <circle cx="16" cy="16" r="12" fill="none" stroke="#ff0080" stroke-width="2"/>
        <text x="16" y="20" text-anchor="middle" fill="#ff0080" font-family="monospace" font-size="14" font-weight="bold">🎤</text>
        <rect x="4" y="4" width="24" height="2" fill="#ff0080" opacity="0.7"/>
        <rect x="4" y="26" width="24" height="2" fill="#ff0080" opacity="0.7"/>
    </svg>'''
    
    from flask import Response
    response = Response(favicon_svg, mimetype='image/svg+xml')
    response.headers['Cache-Control'] = 'public, max-age=86400'
    return response

@app.route('/api/services')
def get_services():
    """Get available TTS services and their capabilities"""
    return jsonify(synthesis_engine.get_available_services())

@app.route('/api/synthesize/openai', methods=['POST'])
def synthesize_openai():
    """Generate speech using OpenAI TTS"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        voice = data.get('voice', 'alloy')
        model = data.get('model', 'tts-1')
        speed = float(data.get('speed', 1.0))
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        if len(text) > 4096:
            return jsonify({'error': 'Text too long (max 4096 characters)'}), 400
        
        result = synthesis_engine.generate_openai_speech(text, voice, model, speed)
        
        # Convert file to base64 for client
        with open(result['file_path'], 'rb') as f:
            audio_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Clean up temp file
        os.unlink(result['file_path'])
        
        result['audio_data'] = audio_data
        del result['file_path']
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/synthesize/elevenlabs', methods=['POST'])
def synthesize_elevenlabs():
    """Generate speech using ElevenLabs API"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        voice = data.get('voice', 'rachel')
        stability = float(data.get('stability', 0.5))
        clarity = float(data.get('clarity', 0.5))
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        if len(text) > 5000:
            return jsonify({'error': 'Text too long (max 5000 characters)'}), 400
        
        result = synthesis_engine.generate_elevenlabs_speech(text, voice, stability, clarity)
        
        # Convert file to base64 for client
        with open(result['file_path'], 'rb') as f:
            audio_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Clean up temp file
        os.unlink(result['file_path'])
        
        result['audio_data'] = audio_data
        del result['file_path']
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    services = synthesis_engine.get_available_services()
    return jsonify({
        'status': 'operational',
        'timestamp': datetime.now().isoformat(),
        'services': services,
        'openai_available': services['openai']['available'],
        'elevenlabs_available': services['elevenlabs']['available']
    })

if __name__ == '__main__':
    print("🎤 Neural Voice Synthesis Terminal Starting...")
    print("📡 Server: http://localhost:5003")
    print("🎵 TTS Engines: Initializing...")
    
    services = synthesis_engine.get_available_services()
    if services['openai']['available']:
        print("✅ OpenAI TTS: Connected")
    else:
        print("⚠️  OpenAI TTS: Not Available")
    
    if services['elevenlabs']['available']:
        print("✅ ElevenLabs: Connected")
    else:
        print("⚠️  ElevenLabs: Not Available")
    
    print("\n" + "="*50)
    print("🚀 Ready for voice synthesis!")
    print("="*50 + "\n")
    
    app.run(host='0.0.0.0', port=5003, debug=True, threaded=True)
