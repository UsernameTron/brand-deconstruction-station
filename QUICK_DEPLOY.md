# Quick Deployment Guide

## Production Launch in 5 Minutes

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy and edit production config
cp environments/production.env .env

# Required: Set your API keys
export OPENAI_API_KEY="sk-your-actual-key"
export ANTHROPIC_API_KEY="sk-ant-your-actual-key"
export GOOGLE_API_KEY="your-actual-key"
export HUGGINGFACE_API_TOKEN="hf_your-actual-token"
export ELEVENLABS_API_KEY="your-actual-key"

# Required: Set a secure secret key
export SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')

# Optional: Enable Sentry (if resolved dependency conflict)
export SENTRY_DSN="https://your-sentry-dsn"
export SENTRY_ENABLED=true
```

### 3. Security Verification
```bash
# Run security tests
pytest tests/test_security.py -v

# Run security scan
bandit -r . -ll
```

### 4. Launch Production Server
```bash
# Using Gunicorn (recommended)
gunicorn -w 4 -b 0.0.0.0:3000 app:app

# Or using Flask (development only)
python3 app.py
```

### 5. Verify Deployment
```bash
# Health check
curl http://localhost:3000/api/health

# Test SSRF protection
curl -X POST http://localhost:3000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"url":"http://192.168.1.1"}'
# Should return: {"error": "Invalid URL"}

# Check metrics
curl http://localhost:3000/metrics
```

---

## Docker Deployment (Alternative)

```bash
# Build image
docker build -t brand-station:latest .

# Run container
docker run -d -p 3000:3000 \
  -e OPENAI_API_KEY="$OPENAI_API_KEY" \
  -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  -e GOOGLE_API_KEY="$GOOGLE_API_KEY" \
  -e HUGGINGFACE_API_TOKEN="$HUGGINGFACE_API_TOKEN" \
  -e ELEVENLABS_API_KEY="$ELEVENLABS_API_KEY" \
  -e SECRET_KEY="$SECRET_KEY" \
  -e FLASK_ENV=production \
  --name brand-station \
  brand-station:latest

# Check logs
docker logs brand-station
```

---

## Production Checklist

- [x] All dependencies installed
- [x] All 5 API keys configured
- [x] SECRET_KEY set to random value (not default)
- [x] FLASK_ENV=production
- [x] HTTPS enabled (FORCE_HTTPS=true)
- [x] Security headers enabled
- [x] Rate limiting enabled
- [x] Monitoring configured (Prometheus/Sentry)
- [ ] Firewall configured (only ports 80/443 open)
- [ ] SSL/TLS certificate installed
- [ ] Log rotation configured
- [ ] Backup strategy in place
- [ ] Monitoring alerts configured

---

## Troubleshooting

### App won't start
```bash
# Check Python version (3.8+ required)
python3 --version

# Verify dependencies
pip list | grep -i flask

# Check logs
tail -f logs/app.json.log
```

### Sentry not working
The Sentry SDK has a known dependency conflict with eventlet. The app will function normally without Sentry using Prometheus metrics and structured logging instead.

To resolve:
```bash
# Create clean virtual environment
python3 -m venv venv-clean
source venv-clean/bin/activate
pip install -r requirements.txt
```

### Rate limiting too aggressive
Edit your `.env` file:
```bash
RATELIMIT_ANALYSIS_PER_MINUTE=20  # Increase from 10
RATELIMIT_GLOBAL_PER_HOUR=100     # Increase from 50
```

---

## Support

- Full documentation: [PRODUCTION_DEPLOYMENT_COMPLETE.md](PRODUCTION_DEPLOYMENT_COMPLETE.md)
- Security details: [PRODUCTION_READY.md](PRODUCTION_READY.md)
- Test coverage: Run `pytest --cov=. --cov-report=html`
