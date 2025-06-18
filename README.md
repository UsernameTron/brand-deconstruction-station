# 🎭 Brand Deconstruction Station

A standalone cyberpunk-themed application for AI-powered brand vulnerability analysis with satirical insights.

## 🎯 Features

- **🤖 Multi-Agent AI Analysis**: CEO, Research, Performance, and Image agents work in coordination
- **🎮 Cyberpunk Terminal Interface**: Retro-futuristic terminal design with matrix effects
- **📊 Brand Vulnerability Scoring**: Comprehensive analysis of corporate weaknesses
- **🎭 Satirical Attack Angles**: Creative insights for brand criticism
- **📄 Multiple Export Formats**: JSON, PDF, and HTML reports
- **🎨 Image Generation**: Satirical brand imagery (mock implementation)
- **⚡ Standalone Operation**: No complex setup required

## 🚀 Quick Start

### Option 1: Automatic Setup (Recommended)

```bash
cd brand-deconstruction-app
python3 run.py
```

The automatic setup will:
- Check Python version compatibility
- Install all dependencies
- Create launcher scripts
- Set up environment configuration
- Launch the application

### Option 2: Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Start the application
python3 app.py
```

### Option 3: Use Launcher Script

```bash
# macOS/Linux
./start.sh

# Windows
start.bat
```

## 📡 Access

Once running, access the application at:
- **Local**: http://localhost:3000
- **Network**: http://your-ip:3000

## 🎮 Interface

The cyberpunk terminal interface includes:

- **Target Acquisition Panel**: Enter URLs and select analysis depth
- **Agent Status Monitor**: Real-time progress of AI agents
- **Vulnerability Assessment**: Detailed scoring and analysis
- **Export Controls**: Download results in multiple formats

## 🔧 Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# Optional - enables real AI analysis
export OPENAI_API_KEY="your_openai_api_key_here"

# Server configuration (optional)
export HOST="0.0.0.0"
export PORT="3000"
```

### Analysis Modes

- **Quick**: ~30 seconds, 3 vulnerabilities
- **Deep**: ~3 minutes, 5 vulnerabilities  
- **Mega**: ~10 minutes, 8 vulnerabilities

## 🤖 AI Agents

The application simulates a multi-agent system:

1. **👑 CEO Agent**: Strategic brand analysis and vulnerability assessment
2. **🔍 Research Agent**: Website scraping and data collection
3. **📊 Performance Agent**: Metrics calculation and scoring
4. **🎨 Image Agent**: Satirical image concept generation

## 📄 Export Formats

- **JSON**: Raw analysis data for developers
- **PDF**: Professional report format
- **HTML**: Styled web report with cyberpunk theme

## 🎯 Use Cases

- **Brand Analysis**: Identify corporate vulnerabilities and weaknesses
- **Satirical Content**: Generate creative angles for brand criticism
- **Marketing Research**: Understand brand positioning and messaging
- **Educational Tool**: Learn about corporate communication patterns

## 🛠️ Technical Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Custom cyberpunk terminal theme
- **AI Integration**: OpenAI API (optional, runs in mock mode without)
- **Export**: ReportLab (PDF), JSON, HTML
- **Web Scraping**: Requests, BeautifulSoup

## 📦 Dependencies

Core dependencies (automatically installed):

```
flask==2.3.3
requests==2.31.0
reportlab==4.0.4
python-dotenv==1.0.0
beautifulsoup4==4.12.2
```

## 🔐 Security Notes

- The application runs in mock mode by default (no external API calls)
- Set `OPENAI_API_KEY` only if you want real AI analysis
- Web scraping respects robots.txt and rate limits
- No data is stored permanently (analysis results are session-based)

## 🎨 Cyberpunk Aesthetic

The interface features:
- **Matrix-style background**: Animated falling characters
- **Neon glow effects**: Green/red/blue color scheme
- **Terminal font**: Fira Code monospace
- **Retro animations**: Flicker effects and progress bars
- **Responsive design**: Works on desktop and mobile

## 🚨 Troubleshooting

### Common Issues

1. **Port already in use**: Change port in `.env` or use `PORT=3001 python3 app.py`
2. **Missing dependencies**: Run `pip install -r requirements.txt`
3. **Python version error**: Ensure Python 3.8+ is installed
4. **Permission denied**: Run `chmod +x start.sh` on macOS/Linux

### Debug Mode

Enable debug mode for development:

```bash
export FLASK_DEBUG=True
python3 app.py
```

## 📈 Future Enhancements

- Real AI integration with multiple LLM providers
- Image generation with DALL-E or Stable Diffusion
- Database persistence for analysis history
- User authentication and saved projects
- API endpoints for external integration
- Plugin system for custom analysis modules

## 📜 License

This project is for educational and satirical purposes. Use responsibly and respect brand trademarks and copyrights.

## 🎭 About

Brand Deconstruction Station is designed to provide critical analysis of corporate branding strategies through an entertaining cyberpunk interface. It combines serious analytical capabilities with satirical commentary to help users understand and critique modern brand messaging.

---

**🎮 Ready to deconstruct some brands? Launch the application and start your analysis!**
