# Docker Hub Deployment Guide

## Quick Deploy Checklist

### Prerequisites
- [ ] Docker installed and running
- [ ] Docker Hub account created at https://hub.docker.com
- [ ] Docker CLI logged in (`docker login`)
- [ ] `.dockerignore` file created (included below)
- [ ] Repository tested locally

### Step 1: Build Docker Image

```bash
cd /Users/cpconnor/projects/brand-deconstruction-station-standalone

# Build the image
docker build -t brand-deconstruction-station:latest .

# Test locally
docker run -d -p 3000:3000 \
  -e OPENAI_API_KEY="your_key" \
  -e ANTHROPIC_API_KEY="your_key" \
  -e GOOGLE_API_KEY="your_key" \
  -e HUGGINGFACE_API_TOKEN="your_token" \
  -e ELEVENLABS_API_KEY="your_key" \
  --name brand-station-test \
  brand-deconstruction-station:latest

# Verify it works
curl http://localhost:3000/api/health

# Stop and remove test container
docker stop brand-station-test
docker rm brand-station-test
```

### Step 2: Tag for Docker Hub

Replace `YOUR_DOCKERHUB_USERNAME` with your Docker Hub username:

```bash
# Tag with your Docker Hub username
docker tag brand-deconstruction-station:latest YOUR_DOCKERHUB_USERNAME/brand-deconstruction-station:latest

# Optional: Also tag with version
docker tag brand-deconstruction-station:latest YOUR_DOCKERHUB_USERNAME/brand-deconstruction-station:v1.0.0
```

### Step 3: Login to Docker Hub

```bash
docker login
# Enter your Docker Hub credentials when prompted
```

### Step 4: Push to Docker Hub

```bash
# Push latest tag
docker push YOUR_DOCKERHUB_USERNAME/brand-deconstruction-station:latest

# Push version tag (if created)
docker push YOUR_DOCKERHUB_USERNAME/brand-deconstruction-station:v1.0.0
```

### Step 5: Create Docker Hub Repository Description

On Docker Hub (https://hub.docker.com), go to your repository and add this description:

```markdown
# 🎭 Brand Deconstruction Station

AI-powered brand vulnerability analysis with cyberpunk terminal interface.

## Quick Start

docker run -d -p 3000:3000 \
  -e OPENAI_API_KEY="your_key" \
  -e ANTHROPIC_API_KEY="your_key" \
  -e GOOGLE_API_KEY="your_key" \
  -e HUGGINGFACE_API_TOKEN="your_token" \
  -e ELEVENLABS_API_KEY="your_key" \
  YOUR_DOCKERHUB_USERNAME/brand-deconstruction-station:latest

Access at http://localhost:3000

## Features
- Multi-agent AI analysis
- Cyberpunk terminal interface
- PDF/JSON/HTML export
- Image & video generation
- Real-time monitoring

## Documentation
GitHub: https://github.com/YOUR_GITHUB_USERNAME/brand-deconstruction-station-standalone
```

---

## For Public Users

### Using Docker

```bash
# Pull and run in one command
docker run -d -p 3000:3000 \
  -e OPENAI_API_KEY="sk-your-key" \
  -e ANTHROPIC_API_KEY="sk-ant-your-key" \
  -e GOOGLE_API_KEY="your-key" \
  -e HUGGINGFACE_API_TOKEN="hf_your-token" \
  -e ELEVENLABS_API_KEY="your-key" \
  --name brand-station \
  YOUR_DOCKERHUB_USERNAME/brand-deconstruction-station:latest

# View logs
docker logs -f brand-station

# Stop
docker stop brand-station

# Remove
docker rm brand-station
```

### Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  brand-station:
    image: YOUR_DOCKERHUB_USERNAME/brand-deconstruction-station:latest
    ports:
      - "3000:3000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - HUGGINGFACE_API_TOKEN=${HUGGINGFACE_API_TOKEN}
      - ELEVENLABS_API_KEY=${ELEVENLABS_API_KEY}
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
```

Create `.env` file:

```bash
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
GOOGLE_API_KEY=your-google-key-here
HUGGINGFACE_API_TOKEN=hf_your-token-here
ELEVENLABS_API_KEY=your-elevenlabs-key-here
SECRET_KEY=generate_with_python_secrets_token_hex
```

Run:

```bash
docker-compose up -d
```

---

## Environment Variables Reference

### Required (for AI features)
- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic Claude API key
- `GOOGLE_API_KEY` - Google AI API key (Imagen/Veo)
- `HUGGINGFACE_API_TOKEN` - Hugging Face token
- `ELEVENLABS_API_KEY` - ElevenLabs TTS API key

### Optional
- `SECRET_KEY` - Flask secret (auto-generated if not set)
- `FLASK_ENV` - Environment (default: production)
- `DEBUG` - Debug mode (default: false)
- `PORT` - Application port (default: 3000)
- `HOST` - Bind address (default: 0.0.0.0)

---

## Troubleshooting

### Container won't start
```bash
# Check logs
docker logs brand-station

# Verify environment variables
docker exec brand-station env | grep API_KEY
```

### Port already in use
```bash
# Use different port
docker run -d -p 3001:3000 YOUR_DOCKERHUB_USERNAME/brand-deconstruction-station:latest
```

### Out of memory
```bash
# Add memory limits
docker run -d -p 3000:3000 \
  --memory="2g" \
  --memory-swap="4g" \
  YOUR_DOCKERHUB_USERNAME/brand-deconstruction-station:latest
```

---

## Advanced Configuration

### Custom Configuration File

Create `custom.env` with your settings:

```bash
FLASK_ENV=production
DEBUG=false
RATE_LIMIT_ENABLED=true
FORCE_HTTPS=true
SENTRY_ENABLED=false
PROMETHEUS_ENABLED=true
LOG_LEVEL=INFO
```

Run with custom config:

```bash
docker run -d -p 3000:3000 \
  --env-file custom.env \
  -e OPENAI_API_KEY="..." \
  YOUR_DOCKERHUB_USERNAME/brand-deconstruction-station:latest
```

### Persistent Storage

```bash
# Create volumes for data persistence
docker volume create brand-station-data
docker volume create brand-station-logs

docker run -d -p 3000:3000 \
  -v brand-station-data:/app/data \
  -v brand-station-logs:/app/logs \
  YOUR_DOCKERHUB_USERNAME/brand-deconstruction-station:latest
```

### Health Check

```bash
# Add health check
docker run -d -p 3000:3000 \
  --health-cmd="curl -f http://localhost:3000/api/health || exit 1" \
  --health-interval=30s \
  --health-timeout=10s \
  --health-retries=3 \
  YOUR_DOCKERHUB_USERNAME/brand-deconstruction-station:latest
```

---

## GitHub Repository Setup (Optional)

If you want to link Docker Hub to GitHub for automated builds:

1. Push code to GitHub:
```bash
cd /Users/cpconnor/projects/brand-deconstruction-station-standalone
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/brand-deconstruction-station-standalone.git
git branch -M main
git push -u origin main
```

2. On Docker Hub:
   - Go to your repository
   - Click "Builds" tab
   - Connect to GitHub
   - Configure automated build on push

---

## Support & Documentation

- **GitHub**: https://github.com/YOUR_GITHUB_USERNAME/brand-deconstruction-station-standalone
- **Docker Hub**: https://hub.docker.com/r/YOUR_DOCKERHUB_USERNAME/brand-deconstruction-station
- **Issues**: Report at GitHub Issues

---

## Security Notes

- Never commit API keys to Git
- Use environment variables for all secrets
- Keep Docker image updated
- Run with non-root user in production (implemented in Dockerfile)
- Enable HTTPS in production (`FORCE_HTTPS=true`)

---

## License

Educational and satirical purposes. Respect brand trademarks.
