# 🎭 Brand Deconstruction Station

A standalone cyberpunk-themed application for AI-powered brand vulnerability analysis with satirical insights.

![Brand Deconstruction Station](https://img.shields.io/badge/Status-Operational-00ff41?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-Web%20App-red?style=for-the-badge&logo=flask)
![Electron](https://img.shields.io/badge/Electron-Desktop%20App-47848f?style=for-the-badge&logo=electron)

## 🎯 Features

- **🤖 Multi-Agent AI Analysis**: CEO, Research, Performance, and Image agents work in coordination
- **🎮 Cyberpunk Terminal Interface**: Retro-futuristic terminal design with matrix effects
- **📊 Brand Vulnerability Scoring**: Comprehensive analysis of corporate weaknesses
- **🎭 Satirical Attack Angles**: Creative insights for brand criticism
- **📄 Multiple Export Formats**: JSON, PDF, and HTML reports
- **🎨 Image Generation**: Satirical brand imagery (mock implementation)
- **⚡ Standalone Operation**: No complex setup required
- **🖥️ Desktop Application**: Native desktop app with Electron wrapper

## 🚀 Quick Start

### Option 1: Web Application

```bash
# Clone the repository
git clone https://github.com/cpconnor/brand-deconstruction-station.git
cd brand-deconstruction-station

# Automatic setup and launch
python3 run.py

# OR use shell launcher
./start.sh

# OR direct launch  
python3 app.py
```

### Option 2: Desktop Application

```bash
# Launch desktop app
cd desktop-launcher
./launch-desktop.sh

# OR manual launch
npm install
npm start
```

## 📡 Access

- **Web App**: http://localhost:3000
- **Desktop App**: Native window application

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

## 🖥️ Desktop Application

### Building Desktop Apps

```bash
cd desktop-launcher

# Install dependencies
npm install

# Development mode
npm run dev

# Build for current platform
npm run build

# Build for specific platforms
npm run build:mac
npm run build:win
npm run build:linux
```

### Desktop Features

- **Native Window**: Dedicated application window
- **System Integration**: Native menus and shortcuts
- **Auto-Updates**: Built-in update mechanism
- **Offline Capable**: Runs without internet connection
- **Cross-Platform**: macOS, Windows, Linux support

## 🛠️ Technical Stack

### Backend
- **Flask** (Python web framework)
- **OpenAI API** (optional, runs in mock mode without)
- **ReportLab** (PDF generation)
- **BeautifulSoup** (web scraping)

### Frontend
- **HTML5/CSS3/JavaScript** (cyberpunk interface)
- **Custom animations** (matrix effects, neon glows)
- **Responsive design** (desktop and mobile)

### Desktop
- **Electron** (cross-platform desktop wrapper)
- **Node.js** (runtime environment)
- **Electron Builder** (packaging and distribution)

## 📦 Dependencies

### Python Dependencies
```
flask==2.3.3
requests==2.31.0
reportlab==4.0.4
python-dotenv==1.0.0
beautifulsoup4==4.12.2
```

### Node.js Dependencies
```
electron
electron-builder
```

## 🎯 Use Cases

- **Brand Analysis**: Identify corporate vulnerabilities and weaknesses
- **Satirical Content**: Generate creative angles for brand criticism
- **Marketing Research**: Understand brand positioning and messaging
- **Educational Tool**: Learn about corporate communication patterns

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
2. **Missing Python dependencies**: Run `pip install -r requirements.txt`
3. **Missing Node dependencies**: Run `npm install` in `desktop-launcher/`
4. **Python version error**: Ensure Python 3.8+ is installed
5. **Permission denied**: Run `chmod +x start.sh` on macOS/Linux

### Desktop App Issues

1. **Electron not found**: Run `npm install` in `desktop-launcher/`
2. **Flask not starting**: Check Python dependencies in main directory
3. **Window not opening**: Check if port 3000 is available
4. **Build failing**: Ensure all dependencies are installed

## 📈 Future Enhancements

- Real AI integration with multiple LLM providers
- Image generation with DALL-E or Stable Diffusion
- Database persistence for analysis history
- User authentication and saved projects
- API endpoints for external integration
- Plugin system for custom analysis modules
- Advanced desktop features (notifications, system tray)

## 📜 License

MIT License - This project is for educational and satirical purposes. Use responsibly and respect brand trademarks and copyrights.

## 🎭 About

Brand Deconstruction Station is designed to provide critical analysis of corporate branding strategies through an entertaining cyberpunk interface. It combines serious analytical capabilities with satirical commentary to help users understand and critique modern brand messaging.

---

**🎮 Ready to deconstruct some brands? Choose your launch method and start your analysis!**

### 🌐 Web Application
```bash
python3 run.py
# Access at http://localhost:3000
```

### 🖥️ Desktop Application  
```bash
cd desktop-launcher && ./launch-desktop.sh
# Native desktop window
```
