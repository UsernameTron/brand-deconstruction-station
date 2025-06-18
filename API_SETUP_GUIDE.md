# 🔑 Complete API Setup Guide - All Services

## 📋 API Keys You Have Available

Based on your setup, you have access to these AI services:
- ✅ **OpenAI** (GPT-4, TTS, Image Generation)
- ✅ **Anthropic** (Claude AI)
- 🔧 **Google Gemini** (Advanced AI)
- 🔧 **Hugging Face** (Open Source Models)
- 🔧 **ElevenLabs** (Premium Voice Synthesis)

## 🚀 Current Configuration Status

### Already Configured ✅
```bash
OPENAI_API_KEY=sk-proj-GmNP... (Active)
ANTHROPIC_API_KEY=sk-ant-api03... (Active)
```

### Need Configuration 🔧
```bash
GOOGLE_API_KEY=your-google-gemini-api-key-here
HUGGINGFACE_API_TOKEN=your-huggingface-token-here
ELEVENLABS_API_KEY=your-elevenlabs-api-key-here
```

## 🔑 Getting Missing API Keys

### 1. Google Gemini API Key

**Steps to get your key:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key (starts with `AIza`)

**Add to your shell config:**
```bash
echo 'export GOOGLE_API_KEY="your-actual-google-key"' >> ~/.zshrc
```

### 2. Hugging Face API Token

**Steps to get your token:**
1. Go to [Hugging Face](https://huggingface.co/settings/tokens)
2. Sign up/Login to your account
3. Click "New token"
4. Select "Read" permissions
5. Copy the token (starts with `hf_`)

**Add to your shell config:**
```bash
echo 'export HUGGINGFACE_API_TOKEN="your-actual-hf-token"' >> ~/.zshrc
```

### 3. ElevenLabs API Key

**Steps to get your key:**
1. Go to [ElevenLabs](https://elevenlabs.io)
2. Sign up/Login to your account
3. Go to Profile → API Key
4. Copy your API key
5. Consider upgrading for more characters

**Add to your shell config:**
```bash
echo 'export ELEVENLABS_API_KEY="your-actual-elevenlabs-key"' >> ~/.zshrc
```

## ⚙️ Configuration Steps

### Option 1: Shell Environment (Recommended)
Add all keys to your `~/.zshrc` file:

```bash
# Open your shell config
nano ~/.zshrc

# Add these lines:
export GOOGLE_API_KEY="your-actual-google-key"
export HUGGINGFACE_API_TOKEN="your-actual-hf-token"
export ELEVENLABS_API_KEY="your-actual-elevenlabs-key"

# Reload your shell
source ~/.zshrc
```

### Option 2: Project Environment Files
Update the `.env` and `tts.env` files in your project directory.

## 🎯 Service Capabilities

### OpenAI (✅ Active)
- **TTS**: 6 neural voices (Alloy, Echo, Fable, Onyx, Nova, Shimmer)
- **GPT-4**: Advanced text generation and analysis
- **Image Generation**: DALL-E integration
- **Cost**: $15/1M characters (TTS), $0.01-0.03/1K tokens (GPT)

### Anthropic (✅ Active)
- **Claude**: Constitutional AI for safer, more helpful responses
- **Advanced reasoning**: Better at analysis and research tasks
- **Cost**: $0.01-0.08/1K tokens depending on model

### Google Gemini (🔧 Setup Needed)
- **Multimodal AI**: Text, image, and code understanding
- **Fast inference**: Optimized for speed
- **Cost**: Free tier available, then pay-per-use

### Hugging Face (🔧 Setup Needed)
- **Open Source**: Access to thousands of models
- **TTS Models**: FastSpeech2, Tacotron2, and more
- **Cost**: Free for most models, paid for hosted inference

### ElevenLabs (🔧 Setup Needed)
- **Premium TTS**: High-quality voice synthesis
- **Voice cloning**: Custom voice creation
- **Emotional control**: Fine-tune voice expression
- **Cost**: $5-22/month for various character limits

## 🧪 Testing Your Setup

### 1. Test All Services
Run this command to check all API keys:
```bash
cd /Users/cpconnor/projects/brand-deconstruction-station-standalone
source ~/.zshrc
python3 -c "
import os
services = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GOOGLE_API_KEY', 'HUGGINGFACE_API_TOKEN', 'ELEVENLABS_API_KEY']
for service in services:
    key = os.getenv(service)
    status = '✅' if key and not key.startswith('your-') else '❌'
    print(f'{service}: {status}')
"
```

### 2. Test TTS Application
```bash
# Launch TTS Terminal
source ~/.zshrc
python3 tts_app.py
```

### 3. Test Brand Analysis
```bash
# Launch Brand Deconstruction Station
source ~/.zshrc
python3 app.py
```

## 🔐 Security Best Practices

### Environment Variables
- ✅ Store keys in shell environment (`~/.zshrc`)
- ✅ Never commit API keys to version control
- ✅ Use different keys for development/production

### Key Management
- 🔄 Rotate keys periodically (every 3-6 months)
- 📊 Monitor usage in service dashboards
- 🚨 Set up billing alerts for paid services

### Access Control
- 🔒 Keep API keys private and secure
- 👥 Don't share keys in team environments
- 🌐 Use environment-specific keys when possible

## 💰 Cost Management

### Free Tiers
- **Google Gemini**: Generous free tier
- **Hugging Face**: Most models free
- **OpenAI**: $5 free credit for new accounts

### Paid Services
- **OpenAI**: Pay-per-use, predictable pricing
- **Anthropic**: Similar to OpenAI pricing
- **ElevenLabs**: Monthly subscription model

### Cost Optimization
- Use free services for testing
- Monitor usage dashboards
- Set billing limits where available
- Choose appropriate model sizes

## 🆘 Troubleshooting

### Common Issues

**"API Key Not Found"**
```bash
# Check if key is in environment
echo $OPENAI_API_KEY
# Reload shell environment
source ~/.zshrc
```

**"Invalid API Key"**
- Verify key format (OpenAI: sk-*, Anthropic: sk-ant-*)
- Check for typos or extra spaces
- Verify key permissions in service dashboard

**"Quota Exceeded"**
- Check usage in service dashboard
- Add billing information if needed
- Consider upgrading plan

### Getting Help
1. Check service status pages
2. Review API documentation
3. Test keys with simple curl commands
4. Contact service support if needed

---

**🎭 Brand Deconstruction Station**  
*Complete API Integration Guide*

*Secure Corporate Network • All Systems Operational*
