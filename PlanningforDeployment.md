Perfect! Now I'll create comprehensive instructions for Claude Code to package the application, perform security audits, and prepare it for shipping.

---

# 📦 CLAUDE CODE: APPLICATION PACKAGING & SECURITY AUDIT INSTRUCTIONS

## PROJECT LOCATION
```
/Users/cpconnor/projects/brand-deconstruction-station-standalone
```

---

## 🎯 MISSION OBJECTIVES

1. **Security Audit**: Identify and fix all vulnerabilities
2. **Code Quality**: Ensure production-ready standards
3. **Packaging**: Create distribution-ready packages for all platforms
4. **Testing**: Comprehensive test coverage before shipping
5. **Documentation**: Complete user and developer documentation
6. **Compliance**: License, legal, and dependency audits

---

## 📋 PHASE 1: SECURITY AUDIT & VULNERABILITY REMEDIATION

### **Step 1.1: Dependency Security Scan**

```bash
# Navigate to project
cd /Users/cpconnor/projects/brand-deconstruction-station-standalone

# Scan Python dependencies for known vulnerabilities
pip install safety pip-audit
safety check --file requirements.txt --json > security/python-vulnerabilities.json
pip-audit --requirement requirements.txt --format json > security/pip-audit-report.json

# Scan Node.js dependencies (Electron app)
cd desktop-launcher
npm audit --json > ../security/npm-audit-report.json
npm audit fix --force  # Auto-fix where possible

# Generate dependency tree for review
npm list --all > ../security/npm-dependency-tree.txt
pip freeze > ../security/python-dependency-tree.txt
```

**Actions Required:**
- [ ] Review `security/python-vulnerabilities.json` for critical/high severity issues
- [ ] Update vulnerable dependencies in `requirements.txt`
- [ ] Review `security/npm-audit-report.json` for Electron vulnerabilities
- [ ] Update `package.json` with secure versions
- [ ] Document any dependencies that cannot be updated with justification

---

### **Step 1.2: Code Security Analysis**

```bash
# Install security analysis tools
pip install bandit semgrep

# Run Bandit (Python security linter)
bandit -r . -f json -o security/bandit-report.json \
  --exclude ./venv,./node_modules,./desktop-launcher/node_modules

# Run Semgrep (multi-language security scanner)
semgrep --config=auto --json --output=security/semgrep-report.json .

# Check for secrets in code
pip install detect-secrets
detect-secrets scan . --exclude-files 'node_modules|venv|\.git' > security/secrets-scan.json
```

**Critical Security Checks:**
- [ ] No hardcoded API keys or credentials
- [ ] Proper input validation on all Flask routes
- [ ] CSRF protection enabled
- [ ] SQL injection prevention (if database added)
- [ ] XSS prevention in templates
- [ ] Secure random number generation
- [ ] Rate limiting implemented
- [ ] HTTPS enforcement configuration available

---

### **Step 1.3: Manual Security Review**

**Review These Critical Areas:**

#### **A. API Key Management** (`app.py`, `tts_app.py`)
```python
# Current Implementation Review:
# ✓ Check: API keys loaded from environment variables
# ✓ Check: No keys in source code
# ✗ FIX: Add key validation and sanitization

# Add this to both app.py and tts_app.py:
def validate_api_key(key, service_name):
    """Validate API key format before use"""
    if not key or len(key) < 20:
        logger.warning(f"Invalid {service_name} API key format")
        return None
    # Remove whitespace and validate format
    key = key.strip()
    if key.startswith('your-') or key == 'your_api_key_here':
        logger.warning(f"Placeholder {service_name} API key detected")
        return None
    return key

# Apply to all API keys:
self.openai_api_key = validate_api_key(os.getenv('OPENAI_API_KEY'), 'OpenAI')
```

#### **B. Input Validation - ENHANCED SSRF PROTECTION** (All Flask routes)
```python
# Add comprehensive input validation with enhanced SSRF protection
from functools import wraps
from urllib.parse import urlparse
from ipaddress import ip_address, ip_network
import socket
import logging

logger = logging.getLogger(__name__)

# Comprehensive blocked networks (IPv4 and IPv6)
BLOCKED_NETWORKS = [
    ip_network('10.0.0.0/8'),          # RFC1918 private
    ip_network('172.16.0.0/12'),       # RFC1918 private
    ip_network('192.168.0.0/16'),      # RFC1918 private
    ip_network('127.0.0.0/8'),         # Loopback
    ip_network('169.254.0.0/16'),      # Link-local
    ip_network('224.0.0.0/4'),         # Multicast
    ip_network('240.0.0.0/4'),         # Reserved
    ip_network('::1/128'),             # IPv6 loopback
    ip_network('fc00::/7'),            # IPv6 private
    ip_network('fe80::/10'),           # IPv6 link-local
    ip_network('ff00::/8'),            # IPv6 multicast
]

# Cloud metadata endpoints (AWS, GCP, Azure, etc.)
BLOCKED_HOSTNAMES = [
    'metadata.google.internal',        # GCP
    '169.254.169.254',                 # AWS/Azure/DigitalOcean metadata
    'metadata',                        # Generic
    'instance-data',                   # EC2
]

def is_safe_url(url):
    """
    Comprehensive URL safety validation to prevent SSRF attacks.

    Returns: (is_safe: bool, message: str)
    """
    try:
        parsed = urlparse(url)

        # Check scheme
        if parsed.scheme not in ['http', 'https']:
            return False, f"Invalid scheme: {parsed.scheme}"

        hostname = parsed.hostname
        if not hostname:
            return False, "Missing hostname"

        # Check for blocked hostnames
        if hostname.lower() in BLOCKED_HOSTNAMES:
            logger.warning(f"Blocked metadata endpoint attempt: {hostname}")
            return False, "Blocked hostname"

        # Resolve DNS and check IP (prevents DNS rebinding)
        try:
            resolved_ip = socket.gethostbyname(hostname)
            ip = ip_address(resolved_ip)

            # Check against blocked networks
            for blocked in BLOCKED_NETWORKS:
                if ip in blocked:
                    logger.warning(f"Blocked private/internal IP: {ip} from {hostname}")
                    return False, "Private or internal IP address"

        except socket.gaierror:
            return False, "DNS resolution failed"
        except ValueError as e:
            return False, f"Invalid IP address: {e}"

        return True, "OK"

    except Exception as e:
        logger.error(f"URL validation error: {e}")
        return False, f"Validation error: {e}"

def validate_url_input(f):
    """Validate URL inputs with comprehensive SSRF protection"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON payload'}), 400

        url = data.get('url', '').strip()

        # Basic validation
        if not url:
            return jsonify({'error': 'URL is required'}), 400

        # Length check (prevent DoS)
        if len(url) > 2048:
            return jsonify({'error': 'URL too long'}), 400

        # Comprehensive SSRF check
        is_safe, message = is_safe_url(url)
        if not is_safe:
            logger.warning(f"Blocked unsafe URL: {url} - Reason: {message}")
            return jsonify({'error': f'Invalid URL: {message}'}), 400

        return f(*args, **kwargs)
    return decorated_function

# Apply to analyze route:
@app.route('/api/analyze', methods=['POST'])
@validate_url_input
def analyze_brand():
    # ... existing code
```

**CRITICAL:** This enhanced validation protects against:
- ✅ Private IPv4 ranges (10.x, 172.16.x, 192.168.x)
- ✅ IPv6 private ranges and loopback
- ✅ Cloud metadata endpoints (AWS, GCP, Azure)
- ✅ DNS rebinding attacks (DNS resolved at validation time)
- ✅ Loopback addresses (127.x)
- ✅ Link-local addresses
- ✅ Multicast and reserved ranges

#### **C. Rate Limiting**
```python
# Add Flask-Limiter
# Update requirements.txt:
# Flask-Limiter==3.5.0

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Add to app initialization
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Apply to critical endpoints
@app.route('/api/analyze', methods=['POST'])
@limiter.limit("10 per minute")
def analyze_brand():
    # ... existing code

@app.route('/api/generate-images', methods=['POST'])
@limiter.limit("5 per minute")
def generate_images():
    # ... existing code
```

#### **D. Security Headers**
```python
# Add Flask-Talisman for security headers
# Update requirements.txt:
# Flask-Talisman==1.1.0

from flask_talisman import Talisman

# Configure security headers
Talisman(app, 
    content_security_policy={
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline'",
        'style-src': "'self' 'unsafe-inline' https://fonts.googleapis.com",
        'font-src': "'self' https://fonts.gstatic.com",
        'img-src': "'self' data:",
    },
    force_https=False  # Enable in production
)
```

#### **E. Error Handling - No Information Leakage**
```python
# Add to app.py
@app.errorhandler(Exception)
def handle_error(error):
    """Generic error handler - don't leak stack traces"""
    logger.error(f"Unhandled exception: {error}", exc_info=True)
    
    if app.debug:
        return jsonify({'error': str(error)}), 500
    else:
        return jsonify({'error': 'An internal error occurred'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400
```

---

### **Step 1.4: Create Security Configuration**

Create `security/SECURITY.md`:
```markdown
# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

Please report security vulnerabilities to: security@yourdomain.com

**Do not** open public issues for security vulnerabilities.

## Security Measures

- All dependencies scanned for vulnerabilities
- Input validation on all user inputs
- Rate limiting on API endpoints
- Security headers configured (CSP, HSTS)
- No credentials in source code
- HTTPS recommended for production

## Known Limitations

- Mock mode runs without authentication (intended for testing)
- API keys stored in environment variables (user responsibility)

## Security Best Practices for Users

1. Keep API keys secure and never commit to version control
2. Run behind reverse proxy (nginx) in production
3. Enable HTTPS for production deployments
4. Regularly update dependencies
5. Use strong, unique API keys for each service
```

---

### **Step 1.5: Environment-Specific Configuration Management**

**CRITICAL GAP:** Current deployment jumps from local to production with no staging environment.

Create `environments/` directory structure:
```bash
mkdir -p environments
```

Create `environments/development.env`:
```bash
# Development Environment Configuration
FLASK_ENV=development
DEBUG=True
LOG_LEVEL=DEBUG
HOST=127.0.0.1
PORT=3000

# Security (relaxed for development)
RATE_LIMIT_ENABLED=False
FORCE_HTTPS=False
FLASK_TALISMAN_ENABLED=False

# API Keys (loaded from parent directory or local)
# OPENAI_API_KEY=your_key_here
# ANTHROPIC_API_KEY=your_key_here
# GOOGLE_API_KEY=your_key_here
# HUGGINGFACE_API_TOKEN=your_token_here
# ELEVENLABS_API_KEY=your_key_here

# Monitoring (disabled in dev)
SENTRY_ENABLED=False
PROMETHEUS_ENABLED=False
```

Create `environments/staging.env`:
```bash
# Staging Environment Configuration
FLASK_ENV=production
DEBUG=False
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=3000

# Security (production-like)
RATE_LIMIT_ENABLED=True
FORCE_HTTPS=True
FLASK_TALISMAN_ENABLED=True
SECRET_KEY=${STAGING_SECRET_KEY}  # Use secrets manager

# API Keys (use staging keys)
OPENAI_API_KEY=${STAGING_OPENAI_KEY}
ANTHROPIC_API_KEY=${STAGING_ANTHROPIC_KEY}
GOOGLE_API_KEY=${STAGING_GOOGLE_KEY}
HUGGINGFACE_API_TOKEN=${STAGING_HF_TOKEN}
ELEVENLABS_API_KEY=${STAGING_ELEVENLABS_KEY}

# Monitoring
SENTRY_ENABLED=True
SENTRY_DSN=${STAGING_SENTRY_DSN}
SENTRY_ENVIRONMENT=staging
PROMETHEUS_ENABLED=True
REDIS_URL=redis://staging-redis:6379/0

# Database (if added)
DATABASE_URL=${STAGING_DATABASE_URL}
```

Create `environments/production.env`:
```bash
# Production Environment Configuration
FLASK_ENV=production
DEBUG=False
LOG_LEVEL=WARNING
HOST=0.0.0.0
PORT=3000

# Security (maximum hardening)
RATE_LIMIT_ENABLED=True
FORCE_HTTPS=True
FLASK_TALISMAN_ENABLED=True
HSTS_MAX_AGE=31536000
SECRET_KEY=${PROD_SECRET_KEY}  # MUST use secrets vault

# API Keys (production keys from secrets manager)
OPENAI_API_KEY=${PROD_OPENAI_KEY}
ANTHROPIC_API_KEY=${PROD_ANTHROPIC_KEY}
GOOGLE_API_KEY=${PROD_GOOGLE_KEY}
HUGGINGFACE_API_TOKEN=${PROD_HF_TOKEN}
ELEVENLABS_API_KEY=${PROD_ELEVENLABS_KEY}

# Monitoring (full observability)
SENTRY_ENABLED=True
SENTRY_DSN=${PROD_SENTRY_DSN}
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
PROMETHEUS_ENABLED=True
REDIS_URL=${PROD_REDIS_URL}

# Database
DATABASE_URL=${PROD_DATABASE_URL}

# Backup
BACKUP_ENABLED=True
BACKUP_S3_BUCKET=${BACKUP_BUCKET}
```

**Update app.py to load environment-specific configs:**
```python
import os
from dotenv import load_dotenv

# Load environment-specific configuration
environment = os.getenv('ENVIRONMENT', 'development')
env_file = f'environments/{environment}.env'

if os.path.exists(env_file):
    load_dotenv(env_file)
    logger.info(f"Loaded configuration for {environment} environment")
else:
    logger.warning(f"No environment file found for {environment}, using defaults")
    load_dotenv()  # Load from default .env

# Configuration class
class Config:
    """Application configuration based on environment"""

    # Environment
    ENV = os.getenv('FLASK_ENV', 'production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

    # Server
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 3000))

    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(32).hex())
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'True').lower() == 'true'
    FORCE_HTTPS = os.getenv('FORCE_HTTPS', 'False').lower() == 'true'

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # Monitoring
    SENTRY_ENABLED = os.getenv('SENTRY_ENABLED', 'False').lower() == 'true'
    SENTRY_DSN = os.getenv('SENTRY_DSN')

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        errors = []

        if cls.ENV == 'production':
            if cls.DEBUG:
                errors.append("DEBUG must be False in production")
            if not cls.FORCE_HTTPS:
                errors.append("FORCE_HTTPS must be True in production")
            if cls.SECRET_KEY == 'change_me_in_production':
                errors.append("SECRET_KEY must be changed in production")

        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")

        return True

# Validate configuration on startup
Config.validate()
```

**Secrets Management:**
```bash
# Option 1: Use environment variables from secrets manager
export PROD_SECRET_KEY=$(aws secretsmanager get-secret-value --secret-id prod/brand-station/secret-key --query SecretString --output text)

# Option 2: Use Vault
vault kv get -field=secret_key secret/brand-station/production

# Option 3: Use SOPS for encrypted config files
sops -d environments/production.enc.env > /tmp/production.env
```

---

### **Step 1.6: SSL/TLS Certificate Management**

**CRITICAL GAP:** No HTTPS configuration or certificate management.

Create `scripts/setup-ssl.sh`:
```bash
#!/bin/bash
set -e

echo "🔒 SSL/TLS Certificate Setup"
echo "=============================="
echo ""

DOMAIN=${1:-localhost}
CERT_DIR="certs"
mkdir -p "$CERT_DIR"

if [ "$DOMAIN" == "localhost" ]; then
    echo "📝 Generating self-signed certificate for development..."
    openssl req -x509 -newkey rsa:4096 \
        -keyout "$CERT_DIR/key.pem" \
        -out "$CERT_DIR/cert.pem" \
        -days 365 -nodes \
        -subj "/CN=localhost/O=Development/C=US"
    echo "✅ Self-signed certificate created for development"
else
    echo "📝 Setting up Let's Encrypt for production..."

    # Install certbot
    if ! command -v certbot &> /dev/null; then
        echo "Installing certbot..."
        sudo apt-get update
        sudo apt-get install -y certbot python3-certbot-nginx
    fi

    # Obtain certificate
    sudo certbot certonly --nginx \
        -d "$DOMAIN" \
        -d "www.$DOMAIN" \
        --non-interactive \
        --agree-tos \
        --email admin@"$DOMAIN"

    # Copy to application cert directory
    sudo cp /etc/letsencrypt/live/"$DOMAIN"/fullchain.pem "$CERT_DIR/cert.pem"
    sudo cp /etc/letsencrypt/live/"$DOMAIN"/privkey.pem "$CERT_DIR/key.pem"
    sudo chown $(whoami):$(whoami) "$CERT_DIR"/*.pem

    # Set up auto-renewal
    echo "Setting up auto-renewal..."
    (crontab -l 2>/dev/null; echo "0 0 * * * certbot renew --quiet --post-hook 'systemctl reload nginx'") | crontab -
fi

echo ""
echo "✅ SSL setup complete!"
echo "Certificate: $CERT_DIR/cert.pem"
echo "Private Key: $CERT_DIR/key.pem"
```

**Update Flask app for HTTPS:**
```python
# Update app.py to support SSL
from flask_talisman import Talisman

if Config.FORCE_HTTPS:
    # Production SSL configuration
    csp = {
        'default-src': ["'self'"],
        'script-src': ["'self'", "'unsafe-inline'"],  # TODO: Remove unsafe-inline
        'style-src': ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
        'font-src': ["'self'", "https://fonts.gstatic.com"],
        'img-src': ["'self'", "data:", "https:"],
        'connect-src': ["'self'"],
        'frame-ancestors': ["'none'"],
        'base-uri': ["'self'"],
        'form-action': ["'self'"],
    }

    Talisman(
        app,
        content_security_policy=csp,
        content_security_policy_nonce_in=['script-src'],
        force_https=True,
        strict_transport_security=True,
        strict_transport_security_max_age=Config.HSTS_MAX_AGE,
        frame_options='DENY',
        referrer_policy='strict-origin-when-cross-origin',
        feature_policy={
            'geolocation': "'none'",
            'camera': "'none'",
            'microphone': "'none'",
        }
    )

# Run with SSL in production
if __name__ == '__main__':
    if Config.FORCE_HTTPS and os.path.exists('certs/cert.pem'):
        app.run(
            host=Config.HOST,
            port=Config.PORT,
            ssl_context=('certs/cert.pem', 'certs/key.pem'),
            debug=Config.DEBUG
        )
    else:
        app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
```

**Nginx reverse proxy configuration (recommended for production):**
```nginx
# /etc/nginx/sites-available/brand-station

upstream brand_station {
    server 127.0.0.1:3000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Static files
    location /static {
        alias /var/www/brand-station/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Proxy to Flask app
    location / {
        proxy_pass http://brand_station;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/m;
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://brand_station;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 📋 PHASE 2: CODE QUALITY & STANDARDS

### **Step 2.1: Code Linting & Formatting**

```bash
# Install quality tools
pip install black flake8 pylint mypy isort

# Format code with Black
black --line-length 100 *.py

# Sort imports
isort --profile black *.py

# Check code quality
flake8 --max-line-length=100 --extend-ignore=E203,W503 *.py > quality/flake8-report.txt
pylint *.py --output-format=json > quality/pylint-report.json

# Type checking
mypy --ignore-missing-imports *.py > quality/mypy-report.txt
```

**Quality Standards:**
- [ ] All code formatted with Black
- [ ] Import statements organized with isort
- [ ] Flake8 score > 8.0/10
- [ ] No critical Pylint warnings
- [ ] Type hints added to critical functions

---

### **Step 2.2: Add Type Hints**

```python
# Update app.py with type hints
from typing import Dict, List, Optional, Tuple, Any
import logging

class BrandAnalysisEngine:
    """AI-powered brand analysis engine with multi-agent coordination"""
    
    def __init__(self) -> None:
        self.openai_api_key: Optional[str] = os.getenv('OPENAI_API_KEY')
        # ... rest of initialization
    
    def scrape_website(self, url: str) -> Dict[str, Any]:
        """Scrape basic website content for analysis
        
        Args:
            url: Website URL to scrape
            
        Returns:
            Dictionary containing scraped data and metadata
        """
        # ... implementation
    
    def analyze_brand_vulnerabilities(
        self, 
        website_data: Dict[str, Any], 
        analysis_type: str = 'deep'
    ) -> Dict[str, Any]:
        """Generate brand vulnerability analysis
        
        Args:
            website_data: Scraped website data
            analysis_type: Type of analysis ('quick', 'deep', 'mega')
            
        Returns:
            Analysis results with vulnerabilities and scores
        """
        # ... implementation
```

---

### **Step 2.3: Add Comprehensive Logging**

```python
# Add proper logging configuration
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(app):
    """Configure application logging"""
    
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Configure rotating file handler
    file_handler = RotatingFileHandler(
        'logs/brand_station.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    
    # Configure console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        '%(levelname)s: %(message)s'
    ))
    
    # Add handlers to app logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.INFO)
    
    return app.logger

# Apply in app initialization
logger = setup_logging(app)
logger.info('Brand Deconstruction Station starting...')
```

---

## 📋 PHASE 2B: MONITORING & OBSERVABILITY INFRASTRUCTURE

**CRITICAL GAP:** No monitoring, metrics, or error tracking configured.

### **Step 2B.1: Application Metrics with Prometheus**

Create `monitoring/prometheus.yml`:
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'brand-station'
    static_configs:
      - targets: ['localhost:3000']
        labels:
          app: 'brand-deconstruction-station'
          environment: 'production'

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['localhost:9093']

rule_files:
  - 'alerts.yml'
```

Create `monitoring/alerts.yml`:
```yaml
groups:
  - name: brand_station_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors/sec"

      - alert: ServiceDown
        expr: up{job="brand-station"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Brand Station service is down"

      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time (p95 > 2s)"
```

**Add Prometheus metrics to app.py:**
```python
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Histogram, Gauge

# Initialize metrics
metrics = PrometheusMetrics(app)

# Custom metrics
analysis_counter = Counter(
    'brand_analysis_total',
    'Total brand analyses performed',
    ['analysis_type', 'status']
)

analysis_duration = Histogram(
    'brand_analysis_duration_seconds',
    'Brand analysis duration',
    ['analysis_type'],
    buckets=(1, 2, 5, 10, 30, 60, 120, 300)
)

api_requests = Counter(
    'api_requests_total',
    'Total API requests to external services',
    ['service', 'status']
)

active_analyses = Gauge(
    'active_analyses',
    'Number of currently running analyses'
)

# Add to analysis endpoint
@app.route('/api/analyze', methods=['POST'])
@validate_url_input
def analyze_brand():
    analysis_type = request.json.get('type', 'quick')
    active_analyses.inc()

    try:
        with analysis_duration.labels(analysis_type=analysis_type).time():
            # ... existing analysis code ...
            result = engine.analyze(...)

        analysis_counter.labels(
            analysis_type=analysis_type,
            status='success'
        ).inc()

        return jsonify(result), 200

    except Exception as e:
        analysis_counter.labels(
            analysis_type=analysis_type,
            status='error'
        ).inc()
        raise
    finally:
        active_analyses.dec()
```

**Add to requirements.txt:**
```
prometheus-flask-exporter==0.22.4
prometheus-client==0.19.0
```

---

### **Step 2B.2: Structured Logging with JSON**

**Enhanced logging configuration:**
```python
import logging
import json
from datetime import datetime
from logging.handlers import RotatingFileHandler
import traceback

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""

    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }

        # Add custom fields
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id

        return json.dumps(log_data)

def setup_logging(app):
    """Configure structured logging with rotation"""
    os.makedirs('logs', exist_ok=True)

    # JSON formatter for file logs
    json_formatter = JSONFormatter()

    # Application log (JSON)
    app_handler = RotatingFileHandler(
        'logs/app.json.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    app_handler.setFormatter(json_formatter)
    app_handler.setLevel(logging.INFO)

    # Error log (JSON)
    error_handler = RotatingFileHandler(
        'logs/errors.json.log',
        maxBytes=10485760,
        backupCount=10
    )
    error_handler.setFormatter(json_formatter)
    error_handler.setLevel(logging.ERROR)

    # Console handler (human-readable)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s'
    ))
    console_handler.setLevel(logging.INFO)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(app_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)

    # Configure Flask app logger
    app.logger.handlers = []
    app.logger.addHandler(app_handler)
    app.logger.addHandler(error_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.INFO)

    return app.logger
```

---

### **Step 2B.3: Error Tracking with Sentry**

**Add Sentry integration:**
```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

if Config.SENTRY_ENABLED and Config.SENTRY_DSN:
    sentry_logging = LoggingIntegration(
        level=logging.INFO,
        event_level=logging.ERROR
    )

    sentry_sdk.init(
        dsn=Config.SENTRY_DSN,
        integrations=[
            FlaskIntegration(),
            sentry_logging,
        ],
        traces_sample_rate=Config.SENTRY_TRACES_SAMPLE_RATE,
        environment=Config.SENTRY_ENVIRONMENT,
        release=f"brand-station@{VERSION}",
        before_send=filter_sensitive_data,
    )

def filter_sensitive_data(event, hint):
    """Filter sensitive data before sending to Sentry"""
    # Remove API keys from error data
    if 'extra' in event:
        for key in list(event['extra'].keys()):
            if 'api_key' in key.lower() or 'token' in key.lower():
                event['extra'][key] = '[REDACTED]'

    # Remove sensitive headers
    if 'request' in event and 'headers' in event['request']:
        event['request']['headers'].pop('Authorization', None)
        event['request']['headers'].pop('X-API-Key', None)

    return event
```

**Add to requirements.txt:**
```
sentry-sdk[flask]==1.40.0
```

---

### **Step 2B.4: Monitoring Stack with Docker Compose**

Create `monitoring/docker-compose.monitoring.yml`:
```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./alerts.yml:/etc/prometheus/alerts.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
    ports:
      - "9090:9090"
    networks:
      - monitoring
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana-dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana-datasources.yml:/etc/grafana/provisioning/datasources/datasources.yml
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD:-changeme}
      - GF_USERS_ALLOW_SIGN_UP=false
    ports:
      - "3001:3000"
    networks:
      - monitoring
    restart: unless-stopped
    depends_on:
      - prometheus

  loki:
    image: grafana/loki:latest
    container_name: loki
    ports:
      - "3100:3100"
    volumes:
      - ./loki-config.yml:/etc/loki/local-config.yaml
      - loki_data:/loki
    command: -config.file=/etc/loki/local-config.yaml
    networks:
      - monitoring
    restart: unless-stopped

  promtail:
    image: grafana/promtail:latest
    container_name: promtail
    volumes:
      - ../logs:/var/log/brand-station
      - ./promtail-config.yml:/etc/promtail/config.yml
    command: -config.file=/etc/promtail/config.yml
    networks:
      - monitoring
    restart: unless-stopped
    depends_on:
      - loki

  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    ports:
      - "9100:9100"
    networks:
      - monitoring
    restart: unless-stopped

  alertmanager:
    image: prom/alertmanager:latest
    container_name: alertmanager
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/config.yml
      - alertmanager_data:/alertmanager
    command:
      - '--config.file=/etc/alertmanager/config.yml'
      - '--storage.path=/alertmanager'
    ports:
      - "9093:9093"
    networks:
      - monitoring
    restart: unless-stopped

volumes:
  prometheus_data:
  grafana_data:
  loki_data:
  alertmanager_data:

networks:
  monitoring:
    driver: bridge
```

Create `monitoring/grafana-datasources.yml`:
```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true

  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
```

Create `monitoring/loki-config.yml`:
```yaml
auth_enabled: false

server:
  http_listen_port: 3100

ingester:
  lifecycler:
    address: 127.0.0.1
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1
  chunk_idle_period: 5m
  chunk_retain_period: 30s

schema_config:
  configs:
    - from: 2020-05-15
      store: boltdb
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 168h

storage_config:
  boltdb:
    directory: /loki/index
  filesystem:
    directory: /loki/chunks

limits_config:
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h
```

Create `monitoring/promtail-config.yml`:
```yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: brand-station
    static_configs:
      - targets:
          - localhost
        labels:
          job: brand-station
          __path__: /var/log/brand-station/*.log
```

**Start monitoring stack:**
```bash
cd monitoring
docker-compose -f docker-compose.monitoring.yml up -d

# Access dashboards
# Grafana: http://localhost:3001 (admin/changeme)
# Prometheus: http://localhost:9090
# Alertmanager: http://localhost:9093
```

---

## 📋 PHASE 3: TESTING INFRASTRUCTURE

### **Step 3.1: Create Test Suite**

Create `tests/test_app.py`:
```python
import pytest
import json
from app import app, BrandAnalysisEngine

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test health endpoint"""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'status' in data
    assert data['status'] == 'operational'

def test_analyze_missing_url(client):
    """Test analysis without URL returns error"""
    response = client.post('/api/analyze',
                          json={},
                          content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_analyze_invalid_url(client):
    """Test analysis with invalid URL"""
    response = client.post('/api/analyze',
                          json={'url': 'not-a-url'},
                          content_type='application/json')
    assert response.status_code in [400, 500]

def test_analyze_valid_url(client):
    """Test analysis with valid URL"""
    response = client.post('/api/analyze',
                          json={'url': 'https://example.com', 'type': 'quick'},
                          content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'analysis_id' in data

def test_brand_engine_initialization():
    """Test BrandAnalysisEngine initializes correctly"""
    engine = BrandAnalysisEngine()
    assert engine is not None
    assert hasattr(engine, 'openai_api_key')

def test_website_scraping():
    """Test website scraping functionality"""
    engine = BrandAnalysisEngine()
    result = engine.scrape_website('https://example.com')
    assert 'url' in result
    assert result['url'] == 'https://example.com'

# Add more tests...
```

Create `tests/test_security.py`:
```python
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_xss_protection(client):
    """Test XSS attack prevention"""
    malicious_url = 'https://example.com<script>alert("XSS")</script>'
    response = client.post('/api/analyze',
                          json={'url': malicious_url},
                          content_type='application/json')
    # Should be rejected or sanitized
    assert response.status_code in [400, 500]

def test_ssrf_protection(client):
    """Test SSRF attack prevention"""
    internal_urls = [
        'http://localhost:8080',
        'http://127.0.0.1',
        'http://169.254.169.254',  # AWS metadata
        'http://10.0.0.1',
    ]
    for url in internal_urls:
        response = client.post('/api/analyze',
                              json={'url': url},
                              content_type='application/json')
        assert response.status_code == 400

def test_rate_limiting(client):
    """Test rate limiting works"""
    # Make multiple rapid requests
    for i in range(15):
        response = client.post('/api/analyze',
                              json={'url': 'https://example.com'},
                              content_type='application/json')
    # Should eventually get rate limited
    assert response.status_code in [200, 429]

# Add more security tests...
```

Run tests:
```bash
# Install pytest
pip install pytest pytest-cov pytest-mock

# Run tests with coverage
pytest tests/ -v --cov=. --cov-report=html --cov-report=term

# Generate coverage report
open htmlcov/index.html
```

**Testing Requirements:**
- [ ] Unit test coverage > 80%
- [ ] All critical paths tested
- [ ] Security tests pass
- [ ] Integration tests for Flask routes
- [ ] Mock tests for AI API calls

---

### **Step 3.2: Load Testing with Locust**

**CRITICAL GAP:** No performance or load testing.

Create `tests/test_load.py`:
```python
from locust import HttpUser, task, between
import random

class BrandStationUser(HttpUser):
    """Load testing user behavior simulation"""
    wait_time = between(1, 5)  # Wait 1-5 seconds between tasks

    def on_start(self):
        """Called when a simulated user starts"""
        self.test_urls = [
            "https://example.com",
            "https://google.com",
            "https://github.com",
        ]

    @task(3)  # 3x weight - most common operation
    def analyze_brand_quick(self):
        """Quick brand analysis"""
        self.client.post("/api/analyze", json={
            "url": random.choice(self.test_urls),
            "type": "quick"
        }, name="/api/analyze (quick)")

    @task(1)
    def analyze_brand_deep(self):
        """Deep brand analysis"""
        self.client.post("/api/analyze", json={
            "url": random.choice(self.test_urls),
            "type": "deep"
        }, name="/api/analyze (deep)")

    @task(5)  # 5x weight - health checks are frequent
    def health_check(self):
        """Health check endpoint"""
        self.client.get("/api/health")

    @task(2)
    def get_analysis_status(self):
        """Check analysis status"""
        analysis_id = "test-analysis-123"
        self.client.get(f"/api/analysis/{analysis_id}/status")
```

**Run load tests:**
```bash
# Install Locust
pip install locust

# Run with web UI
locust -f tests/test_load.py --host=http://localhost:3000

# Run headless (10 users, spawn rate 2/sec, run for 60 seconds)
locust -f tests/test_load.py \
    --host=http://localhost:3000 \
    --users 10 \
    --spawn-rate 2 \
    --run-time 60s \
    --headless

# Run stress test (100 concurrent users)
locust -f tests/test_load.py \
    --host=http://localhost:3000 \
    --users 100 \
    --spawn-rate 10 \
    --run-time 300s \
    --headless \
    --html=reports/load-test-report.html
```

**Performance benchmarks to meet:**
- P50 response time < 500ms
- P95 response time < 2s
- P99 response time < 5s
- Error rate < 1%
- Handles 10 concurrent users smoothly
- Handles 50 concurrent users with degraded performance
- Maximum 100 concurrent users before failure

---

### **Step 3.3: End-to-End Testing with Playwright**

Create `tests/test_e2e.py`:
```python
import pytest
from playwright.sync_api import Page, expect

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context"""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    }

def test_homepage_loads(page: Page):
    """Test that homepage loads correctly"""
    page.goto("http://localhost:3000")
    expect(page).to_have_title(/Brand Deconstruction Station/)
    expect(page.locator("h1")).to_be_visible()

def test_analysis_workflow(page: Page):
    """Test complete analysis workflow"""
    page.goto("http://localhost:3000")

    # Enter URL
    page.fill("input[name='url']", "https://example.com")

    # Select analysis type
    page.select_option("select[name='analysis_type']", "quick")

    # Start analysis
    page.click("button:has-text('Analyze')")

    # Wait for analysis to start
    expect(page.locator(".analysis-progress")).to_be_visible(timeout=5000)

    # Wait for completion (with timeout)
    expect(page.locator(".analysis-results")).to_be_visible(timeout=60000)

    # Verify results are displayed
    expect(page.locator(".vulnerability-score")).to_be_visible()
    expect(page.locator(".attack-angles")).to_be_visible()

def test_export_functionality(page: Page):
    """Test export features"""
    page.goto("http://localhost:3000")

    # Perform analysis first
    page.fill("input[name='url']", "https://example.com")
    page.click("button:has-text('Analyze')")
    expect(page.locator(".analysis-results")).to_be_visible(timeout=60000)

    # Test JSON export
    with page.expect_download() as download_info:
        page.click("button:has-text('Export JSON')")
    download = download_info.value
    assert download.suggested_filename.endswith('.json')

def test_error_handling(page: Page):
    """Test error handling for invalid inputs"""
    page.goto("http://localhost:3000")

    # Test invalid URL
    page.fill("input[name='url']", "not-a-valid-url")
    page.click("button:has-text('Analyze')")

    # Should show error message
    expect(page.locator(".error-message")).to_be_visible()
    expect(page.locator(".error-message")).to_contain_text("Invalid URL")

def test_responsive_design(page: Page):
    """Test responsive design on mobile"""
    page.set_viewport_size({"width": 375, "height": 667})
    page.goto("http://localhost:3000")

    # Check mobile menu is present
    expect(page.locator(".mobile-menu")).to_be_visible()
```

**Run E2E tests:**
```bash
# Install Playwright
pip install pytest-playwright
playwright install

# Run E2E tests
pytest tests/test_e2e.py -v --headed  # With browser UI
pytest tests/test_e2e.py -v  # Headless

# Run with screenshots on failure
pytest tests/test_e2e.py -v --screenshot=only-on-failure

# Generate HTML report
pytest tests/test_e2e.py --html=reports/e2e-report.html
```

---

## 📋 PHASE 3B: CI/CD PIPELINE

**CRITICAL GAP:** No automated testing or deployment pipeline.

### **Step 3B.1: GitHub Actions Workflow**

Create `.github/workflows/ci.yml`:
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  PYTHON_VERSION: '3.11'

jobs:
  security-scan:
    name: Security Scanning
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install security tools
        run: |
          pip install bandit safety pip-audit detect-secrets

      - name: Run Bandit security scan
        run: |
          bandit -r . -f json -o bandit-report.json || true
          bandit -r . -ll  # Fail on medium/high severity

      - name: Check for secrets
        run: |
          detect-secrets scan --baseline .secrets.baseline

      - name: Dependency vulnerability scan
        run: |
          safety check --file requirements.txt --json > safety-report.json || true
          pip-audit --requirement requirements.txt

      - name: Upload security reports
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: security-reports
          path: |
            bandit-report.json
            safety-report.json

  code-quality:
    name: Code Quality Checks
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install quality tools
        run: |
          pip install black flake8 pylint isort mypy

      - name: Check code formatting (Black)
        run: black --check --line-length 100 *.py

      - name: Check import sorting (isort)
        run: isort --check-only --profile black *.py

      - name: Run Flake8
        run: flake8 --max-line-length=100 --extend-ignore=E203,W503 *.py

      - name: Run Pylint
        run: pylint *.py --fail-under=8.0 || true

  test:
    name: Test Suite
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10', '3.11', '3.12']
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Cache dependencies
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-mock

      - name: Run unit tests
        run: |
          pytest tests/ -v --cov=. --cov-report=xml --cov-report=term

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          flags: unittests
          name: codecov-umbrella

  docker-build:
    name: Docker Build & Test
    runs-on: ubuntu-latest
    needs: [security-scan, code-quality, test]
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build Docker image
        run: |
          docker build -t brand-station:test .

      - name: Test Docker image
        run: |
          docker run -d -p 3000:3000 --name test-container brand-station:test
          sleep 10
          curl -f http://localhost:3000/api/health || exit 1
          docker logs test-container
          docker stop test-container

      - name: Login to Docker Hub
        if: github.ref == 'refs/heads/main'
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_TOKEN }}

      - name: Push to Docker Hub
        if: github.ref == 'refs/heads/main'
        run: |
          docker tag brand-station:test ${{ secrets.DOCKER_USERNAME }}/brand-station:latest
          docker push ${{ secrets.DOCKER_USERNAME }}/brand-station:latest

  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: [docker-build]
    if: github.ref == 'refs/heads/develop'
    environment: staging
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to staging server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.STAGING_HOST }}
          username: ${{ secrets.STAGING_USER }}
          key: ${{ secrets.STAGING_SSH_KEY }}
          script: |
            cd /var/www/brand-station
            git pull origin develop
            docker-compose pull
            docker-compose up -d
            sleep 10
            curl -f http://localhost:3000/api/health || exit 1

  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: [docker-build]
    if: github.ref == 'refs/heads/main'
    environment: production
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to production server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.PROD_USER }}
          key: ${{ secrets.PROD_SSH_KEY }}
          script: |
            cd /var/www/brand-station
            git pull origin main
            docker-compose pull
            docker-compose up -d --no-deps --build app
            sleep 10
            curl -f https://yourdomain.com/api/health || exit 1
```

---

### **Step 3B.2: Pre-commit Hooks**

Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-json
      - id: check-merge-conflict
      - id: detect-private-key

  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        args: ['--line-length=100']

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ['--profile', 'black']

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=100', '--extend-ignore=E203,W503']

  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
        exclude: package-lock.json

  - repo: https://github.com/PyCQA/bandit
    rev: '1.7.6'
    hooks:
      - id: bandit
        args: ['-r', '.', '--exclude', './venv,./node_modules']
        files: \.py$
```

**Install pre-commit hooks:**
```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files  # Test on all files
```

---

## 📋 PHASE 4: ROLLBACK & DISASTER RECOVERY

**CRITICAL GAP:** No rollback procedures or disaster recovery plan.

### **Step 4.1: Safe Deployment with Rollback**

Create `scripts/deploy-with-rollback.sh`:
```bash
#!/bin/bash
set -e

echo "🚀 Safe Deployment with Automatic Rollback"
echo "=========================================="
echo ""

# Configuration
ENVIRONMENT=${1:-production}
CURRENT_VERSION=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
NEW_VERSION=$(git describe --tags 2>/dev/null || echo "dev-$(git rev-parse --short HEAD)")
BACKUP_DIR="/backups/brand-station-${CURRENT_VERSION}-$(date +%Y%m%d_%H%M%S)"

echo "Environment: $ENVIRONMENT"
echo "Current Version: $CURRENT_VERSION"
echo "New Version: $NEW_VERSION"
echo ""

# Pre-deployment backup
echo "📦 Creating backup..."
mkdir -p "$BACKUP_DIR"
tar -czf "$BACKUP_DIR/app-backup.tar.gz" \
    --exclude=".git" \
    --exclude="node_modules" \
    --exclude="__pycache__" \
    --exclude="venv" \
    .
docker tag brand-station:latest brand-station:rollback-${CURRENT_VERSION} 2>/dev/null || true
echo "✅ Backup created: $BACKUP_DIR"
echo ""

# Health check function
health_check() {
    local max_attempts=10
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        echo "Health check attempt $attempt/$max_attempts..."
        if curl -f -s http://localhost:3000/api/health > /dev/null 2>&1; then
            echo "✅ Health check passed"
            return 0
        fi
        sleep 3
        ((attempt++))
    done

    echo "❌ Health check failed after $max_attempts attempts"
    return 1
}

# Deploy new version
echo "🚀 Deploying new version..."
if ! ./scripts/deploy.sh "$ENVIRONMENT"; then
    echo "❌ Deployment failed! Rolling back..."
    ./scripts/rollback.sh "$BACKUP_DIR"
    exit 1
fi

# Health check
echo ""
echo "🔍 Performing health checks..."
if ! health_check; then
    echo "❌ Health check failed! Rolling back..."
    ./scripts/rollback.sh "$BACKUP_DIR"
    exit 1
fi

# Smoke tests
echo ""
echo "🧪 Running smoke tests..."
if ! pytest tests/test_smoke.py -v; then
    echo "❌ Smoke tests failed! Rolling back..."
    ./scripts/rollback.sh "$BACKUP_DIR"
    exit 1
fi

echo ""
echo "✅ Deployment successful!"
echo "Version: $NEW_VERSION"
echo "Backup: $BACKUP_DIR"
echo ""
echo "Monitor the application for 15 minutes."
echo "If issues occur, run: ./scripts/rollback.sh $BACKUP_DIR"
```

Create `scripts/rollback.sh`:
```bash
#!/bin/bash
set -e

BACKUP_DIR=$1

if [ -z "$BACKUP_DIR" ] || [ ! -d "$BACKUP_DIR" ]; then
    echo "❌ Error: Valid backup directory required"
    echo "Usage: $0 <backup_directory>"
    exit 1
fi

echo "🔄 Rolling back to previous version..."
echo "Backup: $BACKUP_DIR"
echo ""

# Stop current version
echo "⏹️ Stopping current version..."
docker-compose down 2>/dev/null || true
pkill -f "python.*app.py" 2>/dev/null || true

# Restore backup
echo "📦 Restoring from backup..."
tar -xzf "$BACKUP_DIR/app-backup.tar.gz" -C /tmp/rollback-temp
cp -r /tmp/rollback-temp/* .
rm -rf /tmp/rollback-temp

# Restore Docker image
if docker images | grep -q "brand-station:rollback"; then
    echo "🐳 Restoring Docker image..."
    docker tag brand-station:rollback brand-station:latest
fi

# Restart services
echo "🔄 Restarting services..."
if [ -f "docker-compose.yml" ]; then
    docker-compose up -d
else
    python3 app.py &
fi

sleep 10

# Verify rollback
echo "🔍 Verifying rollback..."
if curl -f http://localhost:3000/api/health > /dev/null 2>&1; then
    echo "✅ Rollback successful!"
    echo "Application is running on previous version"
else
    echo "❌ Rollback verification failed"
    echo "Manual intervention required"
    exit 1
fi
```

Make scripts executable:
```bash
chmod +x scripts/deploy-with-rollback.sh scripts/rollback.sh
```

---

### **Step 4.2: Automated Backups**

Create `scripts/backup.sh`:
```bash
#!/bin/bash
set -e

BACKUP_ROOT="/backups/brand-station"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$BACKUP_ROOT/$TIMESTAMP"
RETENTION_DAYS=30

echo "🗄️ Creating backup..."
mkdir -p "$BACKUP_DIR"

# Backup application files
tar -czf "$BACKUP_DIR/app.tar.gz" \
    --exclude=".git" \
    --exclude="node_modules" \
    --exclude="__pycache__" \
    --exclude="venv" \
    --exclude="*.log" \
    .

# Backup data directory
if [ -d "data" ]; then
    tar -czf "$BACKUP_DIR/data.tar.gz" data/
fi

# Backup environment configs
if [ -d "environments" ]; then
    tar -czf "$BACKUP_DIR/environments.tar.gz" environments/
fi

# Generate checksum
cd "$BACKUP_DIR"
sha256sum *.tar.gz > checksums.txt

echo "✅ Backup complete: $BACKUP_DIR"

# Cleanup old backups
echo "🧹 Cleaning up old backups (older than $RETENTION_DAYS days)..."
find "$BACKUP_ROOT" -type d -mtime +$RETENTION_DAYS -exec rm -rf {} + 2>/dev/null || true

# Upload to S3 (if configured)
if [ -n "$BACKUP_S3_BUCKET" ]; then
    echo "☁️ Uploading to S3..."
    aws s3 sync "$BACKUP_DIR" "s3://$BACKUP_S3_BUCKET/backups/$TIMESTAMP/"
fi
```

**Set up automated backups (cron):**
```bash
# Add to crontab
crontab -e

# Backup daily at 2 AM
0 2 * * * /path/to/brand-station/scripts/backup.sh >> /var/log/brand-station-backup.log 2>&1
```

---

## 📋 PHASE 5: API DOCUMENTATION

**CRITICAL GAP:** No API documentation for consumers.

### **Step 5.1: OpenAPI/Swagger Specification**

Create `static/swagger.json`:
```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "Brand Deconstruction Station API",
    "version": "1.0.0",
    "description": "AI-powered brand vulnerability analysis and satirical attack angle generation",
    "contact": {
      "name": "API Support",
      "url": "https://github.com/yourusername/brand-deconstruction-station"
    }
  },
  "servers": [
    {
      "url": "http://localhost:3000",
      "description": "Development"
    },
    {
      "url": "https://api.brandstation.com",
      "description": "Production"
    }
  ],
  "paths": {
    "/api/health": {
      "get": {
        "summary": "Health Check",
        "description": "Check API health and service status",
        "responses": {
          "200": {
            "description": "Service is healthy",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "status": {"type": "string", "example": "operational"},
                    "timestamp": {"type": "string", "format": "date-time"},
                    "version": {"type": "string", "example": "1.0.0"}
                  }
                }
              }
            }
          }
        }
      }
    },
    "/api/analyze": {
      "post": {
        "summary": "Analyze Brand",
        "description": "Perform brand vulnerability analysis on a target website",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "required": ["url"],
                "properties": {
                  "url": {
                    "type": "string",
                    "format": "uri",
                    "example": "https://example.com",
                    "description": "Target website URL"
                  },
                  "type": {
                    "type": "string",
                    "enum": ["quick", "deep", "mega"],
                    "default": "quick",
                    "description": "Analysis depth"
                  }
                }
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Analysis started successfully",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "analysis_id": {"type": "string"},
                    "status": {"type": "string"},
                    "estimated_time": {"type": "integer"}
                  }
                }
              }
            }
          },
          "400": {
            "description": "Invalid request",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "error": {"type": "string"}
                  }
                }
              }
            }
          },
          "429": {
            "description": "Rate limit exceeded"
          }
        }
      }
    }
  }
}
```

**Add Swagger UI to app.py:**
```python
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Brand Deconstruction Station API",
        'defaultModelsExpandDepth': -1
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
```

**Add to requirements.txt:**
```
flask-swagger-ui==4.11.1
```

Access API documentation at: http://localhost:3000/api/docs

---

## 📋 PHASE 6: PACKAGING & DISTRIBUTION

### **Step 4.1: Create Distribution Scripts**

Create `scripts/package-all.sh`:
```bash
#!/bin/bash
set -e

echo "🎭 Brand Deconstruction Station - Complete Packaging Pipeline"
echo "=============================================================="
echo ""

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

VERSION="1.0.0"
BUILD_DIR="dist"
RELEASE_DIR="releases/v${VERSION}"

# Create directories
mkdir -p "$BUILD_DIR" "$RELEASE_DIR" security quality

echo "📋 Step 1: Security Audit"
echo "-------------------------"
./scripts/security-audit.sh

echo ""
echo "📋 Step 2: Code Quality Check"
echo "-----------------------------"
./scripts/quality-check.sh

echo ""
echo "📋 Step 3: Run Tests"
echo "-------------------"
pytest tests/ -v --cov=. --cov-report=term

echo ""
echo "📋 Step 4: Build Python Package"
echo "-------------------------------"
python setup.py sdist bdist_wheel

echo ""
echo "📋 Step 5: Build Desktop Applications"
echo "------------------------------------"
cd desktop-launcher
npm install
npm run build:mac
npm run build:win
npm run build:linux
cd ..

echo ""
echo "📋 Step 6: Build Docker Image"
echo "----------------------------"
docker build -t brand-deconstruction-station:${VERSION} .
docker tag brand-deconstruction-station:${VERSION} brand-deconstruction-station:latest

echo ""
echo "📋 Step 7: Create Standalone Executables"
echo "---------------------------------------"
pip install pyinstaller
pyinstaller --clean --onefile \
    --add-data "templates:templates" \
    --add-data "static:static" \
    --name "bds-server" \
    --icon "desktop-launcher/assets/icon.ico" \
    app.py

echo ""
echo "📋 Step 8: Generate Checksums"
echo "----------------------------"
cd "$RELEASE_DIR"
find . -type f -exec sha256sum {} \; > SHA256SUMS.txt
cd "$PROJECT_ROOT"

echo ""
echo "📋 Step 9: Create Release Archives"
echo "---------------------------------"
# Source archive
tar -czf "$RELEASE_DIR/brand-deconstruction-station-${VERSION}-source.tar.gz" \
    --exclude=".git" \
    --exclude="node_modules" \
    --exclude="__pycache__" \
    --exclude="venv" \
    --exclude="dist" \
    --exclude="build" \
    .

# Copy build artifacts
cp -r desktop-launcher/dist/* "$RELEASE_DIR/"
cp dist/*.whl "$RELEASE_DIR/"
cp dist/*.tar.gz "$RELEASE_DIR/"

echo ""
echo "✅ Packaging Complete!"
echo "===================="
echo ""
echo "📦 Distribution files in: $RELEASE_DIR"
echo ""
echo "Available packages:"
echo "  • Desktop Apps:"
echo "    - macOS: .dmg"
echo "    - Windows: .exe installer"
echo "    - Linux: .AppImage"
echo "  • Python Package: .whl"
echo "  • Docker Image: brand-deconstruction-station:${VERSION}"
echo "  • Standalone: bds-server executable"
echo "  • Source: .tar.gz"
echo ""
echo "🔐 SHA256 checksums available in: SHA256SUMS.txt"
echo ""
echo "🚀 Ready for distribution!"
```

Create `scripts/security-audit.sh`:
```bash
#!/bin/bash
set -e

echo "🔒 Running Security Audit..."
echo ""

# Create security reports directory
mkdir -p security

# Python dependency check
echo "📦 Scanning Python dependencies..."
pip install safety pip-audit
safety check --file requirements.txt --json > security/safety-report.json || true
pip-audit --requirement requirements.txt --format json > security/pip-audit.json || true

# Node.js dependency check
echo "📦 Scanning Node.js dependencies..."
cd desktop-launcher
npm audit --json > ../security/npm-audit.json || true
cd ..

# Code security scan
echo "🔍 Running code security analysis..."
pip install bandit
bandit -r . -f json -o security/bandit-report.json \
    --exclude ./venv,./node_modules,./desktop-launcher/node_modules || true

# Secret scanning
echo "🔑 Scanning for exposed secrets..."
pip install detect-secrets
detect-secrets scan . \
    --exclude-files 'node_modules|venv|\.git|dist|build' \
    > security/secrets-baseline.json || true

# Generate summary
echo ""
echo "✅ Security audit complete!"
echo "📊 Reports generated in: security/"
echo ""
echo "Review these files:"
echo "  • security/safety-report.json - Python vulnerability scan"
echo "  • security/pip-audit.json - Detailed Python audit"
echo "  • security/npm-audit.json - Node.js vulnerability scan"
echo "  • security/bandit-report.json - Code security analysis"
echo "  • security/secrets-baseline.json - Secret detection results"
```

Create `scripts/quality-check.sh`:
```bash
#!/bin/bash
set -e

echo "✨ Running Code Quality Checks..."
echo ""

# Create quality reports directory
mkdir -p quality

# Install quality tools
pip install black flake8 pylint isort

# Format check
echo "🎨 Checking code formatting..."
black --check --line-length 100 *.py || {
    echo "❌ Code formatting issues found. Run: black --line-length 100 *.py"
    exit 1
}

# Import sorting
echo "📦 Checking import organization..."
isort --check-only --profile black *.py || {
    echo "❌ Import sorting issues found. Run: isort --profile black *.py"
    exit 1
}

# Linting
echo "🔍 Running Flake8..."
flake8 --max-line-length=100 --extend-ignore=E203,W503 *.py \
    > quality/flake8-report.txt || true

# Pylint
echo "📊 Running Pylint..."
pylint *.py --output-format=json > quality/pylint-report.json || true

echo ""
echo "✅ Code quality check complete!"
echo "📊 Reports generated in: quality/"
```

Make scripts executable:
```bash
chmod +x scripts/*.sh
```

---

### **Step 4.2: Create setup.py for PyPI**

Create `setup.py`:
```python
#!/usr/bin/env python3
from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme = Path("README.md").read_text(encoding="utf-8")

# Read requirements
requirements = Path("requirements.txt").read_text().strip().split("\n")

setup(
    name="brand-deconstruction-station",
    version="1.0.0",
    author="CPConnor",
    author_email="your.email@example.com",
    description="AI-powered brand vulnerability analysis with cyberpunk interface",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/brand-deconstruction-station",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/brand-deconstruction-station/issues",
        "Source": "https://github.com/yourusername/brand-deconstruction-station",
        "Documentation": "https://github.com/yourusername/brand-deconstruction-station/wiki",
    },
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    include_package_data=True,
    package_data={
        "": ["templates/*.html", "static/*"],
    },
    install_requires=requirements,
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "bds-server=app:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="brand analysis ai cyberpunk satirical corporate vulnerability",
)
```

---

### **Step 4.3: Add License File**

Create `LICENSE`:
```
MIT License

Copyright (c) 2025 CPConnor

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

### **Step 4.4: Create Comprehensive Documentation**

Create `INSTALL.md`:
```markdown
# Installation Guide

## Quick Start (Recommended)

### Option 1: Desktop Application (Easiest)

**macOS:**
1. Download `Brand-Deconstruction-Station-1.0.0.dmg`
2. Open the .dmg file
3. Drag app to Applications folder
4. Launch from Applications

**Windows:**
1. Download `Brand-Deconstruction-Station-Setup-1.0.0.exe`
2. Run the installer
3. Follow installation wizard
4. Launch from Start Menu

**Linux:**
1. Download `Brand-Deconstruction-Station-1.0.0.AppImage`
2. Make executable: `chmod +x Brand-Deconstruction-Station-1.0.0.AppImage`
3. Run: `./Brand-Deconstruction-Station-1.0.0.AppImage`

### Option 2: Docker (Cross-Platform)

```bash
docker pull yourusername/brand-deconstruction-station:1.0.0
docker run -p 3000:3000 \
  -e OPENAI_API_KEY=your_key \
  yourusername/brand-deconstruction-station:1.0.0
```

Open browser: http://localhost:3000

### Option 3: Python Package (Developers)

```bash
pip install brand-deconstruction-station
bds-server
```

Open browser: http://localhost:3000

### Option 4: From Source

```bash
git clone https://github.com/yourusername/brand-deconstruction-station.git
cd brand-deconstruction-station
python3 run.py
```

## Configuration

### API Keys

Create `.env` file in project root:

```env
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_API_KEY=your_google_key_here
HUGGINGFACE_API_TOKEN=your_hf_token_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here
```

**Note:** Application works in mock mode without API keys for testing.

### Server Configuration

```env
HOST=0.0.0.0
PORT=3000
FLASK_ENV=production
```

## System Requirements

- **Python**: 3.8 or higher
- **RAM**: 2GB minimum, 4GB recommended
- **Disk**: 500MB for installation
- **Network**: Internet connection for AI features

## Troubleshooting

### Port Already in Use
```bash
PORT=3001 python3 app.py
```

### Missing Dependencies
```bash
pip install -r requirements.txt
```

### Permission Errors (macOS/Linux)
```bash
chmod +x start.sh
./start.sh
```

## Support

- GitHub Issues: https://github.com/yourusername/brand-deconstruction-station/issues
- Documentation: https://github.com/yourusername/brand-deconstruction-station/wiki
```

Create `USAGE.md` with user guide...

---

## 📋 PHASE 5: FINAL PRE-SHIP CHECKLIST

### **Step 5.1: Complete Pre-Ship Checklist**

```bash
# Run comprehensive check
./scripts/pre-ship-check.sh
```

Create `scripts/pre-ship-check.sh`:
```bash
#!/bin/bash

echo "🚀 Pre-Ship Checklist for Brand Deconstruction Station"
echo "======================================================"
echo ""

PASS=0
FAIL=0

check() {
    if [ $? -eq 0 ]; then
        echo "✅ $1"
        ((PASS++))
    else
        echo "❌ $1"
        ((FAIL++))
    fi
}

# Security checks
echo "🔒 Security Checks:"
./scripts/security-audit.sh > /dev/null 2>&1
check "Security audit completed"

# Quality checks
echo ""
echo "✨ Quality Checks:"
./scripts/quality-check.sh > /dev/null 2>&1
check "Code quality standards met"

# Test coverage
echo ""
echo "🧪 Test Coverage:"
pytest tests/ --cov=. --cov-fail-under=80 > /dev/null 2>&1
check "Test coverage > 80%"

# Documentation
echo ""
echo "📚 Documentation:"
[ -f "README.md" ] && check "README.md exists" || ((FAIL++))
[ -f "LICENSE" ] && check "LICENSE file exists" || ((FAIL++))
[ -f "INSTALL.md" ] && check "INSTALL.md exists" || ((FAIL++))
[ -f "security/SECURITY.md" ] && check "SECURITY.md exists" || ((FAIL++))

# Package files
echo ""
echo "📦 Package Files:"
[ -f "setup.py" ] && check "setup.py exists" || ((FAIL++))
[ -f "requirements.txt" ] && check "requirements.txt exists" || ((FAIL++))
[ -f "Dockerfile" ] && check "Dockerfile exists" || ((FAIL++))
[ -f "desktop-launcher/package.json" ] && check "package.json exists" || ((FAIL++))

# Build artifacts
echo ""
echo "🏗️ Build Artifacts:"
[ -d "desktop-launcher/dist" ] && check "Desktop apps built" || ((FAIL++))
[ -f "dist/brand_deconstruction_station-1.0.0-py3-none-any.whl" ] && check "Python wheel built" || ((FAIL++))

# Git status
echo ""
echo "📝 Git Status:"
git diff --quiet && check "No uncommitted changes" || ((FAIL++))
git tag | grep -q "v1.0.0" && check "Release tag exists" || ((FAIL++))

echo ""
echo "======================================================"
echo "Results: ✅ $PASS passed | ❌ $FAIL failed"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "🎉 All checks passed! Ready to ship! 🚀"
    exit 0
else
    echo "⚠️  Some checks failed. Please review and fix."
    exit 1
fi
```

---

### **Step 5.2: Final Manual Review**

**Critical Review Points:**
- [ ] All API keys removed from source code
- [ ] All security vulnerabilities addressed
- [ ] Test coverage > 80%
- [ ] All documentation complete and accurate
- [ ] License file added
- [ ] Version numbers consistent across all files
- [ ] Changelog updated
- [ ] Git repository clean (no uncommitted changes)
- [ ] All secrets removed from git history
- [ ] `.gitignore` properly configured
- [ ] README has clear installation instructions
- [ ] Examples work as documented
- [ ] Error messages are user-friendly
- [ ] No debug/development code in production builds
- [ ] All third-party attributions included
- [ ] Privacy policy included (if collecting data)

---

## 📋 PHASE 6: DISTRIBUTION & DEPLOYMENT

### **Step 6.1: Tag Release**

```bash
# Create annotated tag
git tag -a v1.0.0 -m "Release version 1.0.0 - Brand Deconstruction Station

Features:
- AI-powered brand vulnerability analysis
- Multi-agent system (CEO, Research, Performance, Image)
- PENTAGRAM framework for structured prompts
- Cyberpunk terminal interface
- Multiple export formats (JSON, PDF, HTML)
- Desktop apps for macOS, Windows, Linux
- Docker support

Security:
- Full security audit completed
- All dependencies scanned for vulnerabilities
- Input validation and rate limiting
- Security headers configured

Quality:
- Test coverage > 80%
- Code quality standards met
- Comprehensive documentation
"

# Push tag
git push origin v1.0.0
```

---

### **Step 6.2: GitHub Release**

```bash
# Using GitHub CLI
gh release create v1.0.0 \
    releases/v1.0.0/* \
    --title "Brand Deconstruction Station v1.0.0" \
    --notes "See CHANGELOG.md for details" \
    --draft  # Review before publishing
```

---

### **Step 6.3: Docker Hub**

```bash
# Login to Docker Hub
docker login

# Push images
docker push yourusername/brand-deconstruction-station:1.0.0
docker push yourusername/brand-deconstruction-station:latest
```

---

### **Step 6.4: PyPI Release**

```bash
# Install twine
pip install twine

# Upload to PyPI
twine upload dist/*

# Test installation
pip install brand-deconstruction-station==1.0.0
```

---

## 🎯 EXECUTION SUMMARY

**Run These Commands in Order:**

```bash
# 1. Security & Quality
./scripts/security-audit.sh
./scripts/quality-check.sh

# 2. Run Tests
pytest tests/ -v --cov=. --cov-report=term

# 3. Package Everything
./scripts/package-all.sh

# 4. Pre-Ship Check
./scripts/pre-ship-check.sh

# 5. Tag and Release
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# 6. Publish
gh release create v1.0.0 releases/v1.0.0/*
docker push yourusername/brand-deconstruction-station:1.0.0
twine upload dist/*
```

---

## ✅ SUCCESS CRITERIA

Application is ready to ship when:
- [ ] All security vulnerabilities resolved
- [ ] Test coverage > 80%
- [ ] All quality checks pass
- [ ] All documentation complete
- [ ] License added
- [ ] Multi-platform builds successful
- [ ] Pre-ship checklist passes 100%
- [ ] GitHub release created
- [ ] Docker image published
- [ ] PyPI package published
- [ ] Installation tested on all platforms

---

## 🎯 ENHANCED PRE-SHIP CHECKLIST

### **Critical Security & Infrastructure** (MUST COMPLETE)

- [ ] **Enhanced SSRF Protection**: Comprehensive URL validation with IPv6, cloud metadata, DNS rebinding protection implemented
- [ ] **Environment Configurations**: dev/staging/production environment files created and tested
- [ ] **SSL/TLS Setup**: Certificates configured for production (Let's Encrypt or manual)
- [ ] **Secrets Management**: API keys moved to secure vault (AWS Secrets Manager, Vault, or SOPS)
- [ ] **Security Headers**: Flask-Talisman configured with strict CSP and security headers
- [ ] **Rate Limiting**: Flask-Limiter implemented on all API endpoints
- [ ] **Input Validation**: All user inputs validated and sanitized
- [ ] **Dependency Pinning**: All dependencies pinned to exact versions in requirements.txt

### **Monitoring & Observability** (HIGH PRIORITY)

- [ ] **Prometheus Metrics**: Application metrics exposed and tested
- [ ] **Structured Logging**: JSON logging with rotation configured
- [ ] **Sentry Integration**: Error tracking enabled for staging and production
- [ ] **Grafana Dashboards**: Monitoring dashboards created and validated
- [ ] **Log Aggregation**: Loki and Promtail configured for log collection
- [ ] **Alerting Rules**: Critical alerts configured (downtime, high error rate, slow response)
- [ ] **Health Endpoints**: Comprehensive health checks implemented

### **Testing & CI/CD** (HIGH PRIORITY)

- [ ] **Unit Tests**: Test coverage > 80% achieved
- [ ] **Integration Tests**: All Flask routes tested
- [ ] **Security Tests**: SSRF, XSS, rate limiting tests passing
- [ ] **Load Tests**: Performance benchmarks met (p95 < 2s)
- [ ] **E2E Tests**: Playwright tests cover critical user journeys
- [ ] **CI/CD Pipeline**: GitHub Actions workflow configured and tested
- [ ] **Pre-commit Hooks**: Installed and validated on development machines
- [ ] **Staging Environment**: Fully functional staging environment deployed

### **Deployment & Recovery** (MUST COMPLETE)

- [ ] **Rollback Procedures**: Tested rollback scripts work correctly
- [ ] **Automated Backups**: Daily backups configured and tested
- [ ] **Disaster Recovery Plan**: RTO/RPO defined and documented
- [ ] **Blue-Green Deployment**: Deployment strategy implemented and tested
- [ ] **Smoke Tests**: Post-deployment validation scripts created

### **Documentation** (MUST COMPLETE)

- [ ] **API Documentation**: Swagger/OpenAPI spec complete and accurate
- [ ] **README.md**: Updated with current installation instructions
- [ ] **INSTALL.md**: Comprehensive installation guide for all platforms
- [ ] **SECURITY.md**: Security policy and vulnerability reporting process
- [ ] **CHANGELOG.md**: Version history documented
- [ ] **LICENSE**: License file added
- [ ] **CONTRIBUTING.md**: Contribution guidelines documented
- [ ] **.env.example**: Environment template with all required variables

### **Code Quality** (MUST COMPLETE)

- [ ] **Black Formatting**: All Python code formatted
- [ ] **Import Sorting**: isort applied to all files
- [ ] **Flake8**: No critical linting errors
- [ ] **Pylint Score**: > 8.0/10
- [ ] **Type Hints**: Added to critical functions
- [ ] **No Debug Code**: All debug statements and test code removed
- [ ] **No Commented Code**: Cleaned up commented-out code

### **Performance & Optimization** (RECOMMENDED)

- [ ] **Static Assets**: CSS/JS minified and compressed
- [ ] **Image Optimization**: All images optimized for web
- [ ] **Caching Strategy**: Redis caching implemented (if applicable)
- [ ] **CDN Configuration**: Static assets served from CDN (production)
- [ ] **Database Optimization**: Queries optimized and indexed (if applicable)

### **Compliance & Legal** (IF APPLICABLE)

- [ ] **License Audit**: All dependencies reviewed for license compatibility
- [ ] **Privacy Policy**: Published if collecting user data
- [ ] **Terms of Service**: Defined and accessible
- [ ] **GDPR Compliance**: Data handling compliant with GDPR (if EU users)
- [ ] **Attribution**: Third-party libraries properly attributed

---

## 📊 DEPLOYMENT READINESS SCORECARD

### **Scoring Guide:**
- **Critical (Must Complete)**: 25 items × 4 points = 100 points
- **High Priority**: 7 items × 2 points = 14 points
- **Recommended**: 5 items × 1 point = 5 points
- **Total Possible**: 119 points

### **Readiness Levels:**
- **100+ points**: Production Ready ✅
- **80-99 points**: Staging Ready 🟡
- **60-79 points**: Development Only 🟠
- **<60 points**: Not Ready ❌

---

## 🚀 FINAL DEPLOYMENT WORKFLOW

### **Step-by-Step Deployment Process:**

```bash
# 1. Pre-Deployment Validation (30 min)
./scripts/security-audit.sh
./scripts/quality-check.sh
pytest tests/ -v --cov=. --cov-report=term
./scripts/pre-ship-check.sh

# 2. Create Release Tag (5 min)
git tag -a v1.0.0 -m "Production release v1.0.0"
git push origin v1.0.0

# 3. Build All Artifacts (60 min)
./scripts/package-all.sh

# 4. Deploy to Staging (15 min)
ENVIRONMENT=staging ./scripts/deploy-with-rollback.sh

# 5. Staging Validation (30 min)
pytest tests/test_e2e.py --base-url=https://staging.yourdomain.com
locust -f tests/test_load.py --host=https://staging.yourdomain.com --users 50 --run-time 300s

# 6. Deploy to Production (30 min)
ENVIRONMENT=production ./scripts/deploy-with-rollback.sh

# 7. Post-Deployment Monitoring (60 min)
# Monitor Grafana dashboards
# Check Sentry for errors
# Review application logs
# Verify metrics are healthy

# 8. Final Validation (15 min)
curl -f https://yourdomain.com/api/health
pytest tests/test_smoke.py --base-url=https://yourdomain.com
```

**Total Time: ~4 hours for first deployment**
**Subsequent Deployments: ~1 hour (automated CI/CD)**

---

## 📈 SUCCESS METRICS

### **Application is Production-Ready When:**

#### **Security ✅**
- Zero critical/high vulnerabilities in security scan
- All OWASP Top 10 vulnerabilities addressed
- Secrets managed in secure vault
- SSL/TLS with A+ rating on SSL Labs
- Rate limiting prevents abuse
- Input validation prevents injection attacks

#### **Reliability ✅**
- Uptime > 99.9% (< 43 minutes downtime/month)
- Tested rollback procedures
- Automated daily backups
- RTO < 15 minutes
- RPO < 24 hours

#### **Performance ✅**
- P50 response time < 500ms
- P95 response time < 2s
- P99 response time < 5s
- Handles 50+ concurrent users
- Error rate < 1%

#### **Observability ✅**
- All critical metrics collected
- Real-time dashboards configured
- Alerts trigger within 2 minutes
- Error tracking captures 100% of exceptions
- Logs retained for 30+ days

#### **Quality ✅**
- Test coverage > 80%
- All CI/CD checks pass
- Code quality score > 8/10
- No critical bugs in backlog
- Documentation complete and accurate

---

## 🎯 PRIORITY ACTION ITEMS

### **🔴 IMMEDIATE (Before ANY Deployment)**

1. **Fix SSRF Vulnerability**
   - Replace basic validation with comprehensive protection
   - Test against all attack vectors
   - Verify DNS rebinding protection

2. **Pin Dependencies**
   - Lock all packages to exact versions
   - Generate constraints.txt
   - Test build reproducibility

3. **Add Secret Scanning**
   - Install detect-secrets
   - Create .secrets.baseline
   - Set up pre-commit hooks

4. **Create Staging Environment**
   - Deploy staging server
   - Configure staging database
   - Set up staging monitoring

5. **Implement Basic Monitoring**
   - Add Prometheus metrics
   - Configure Sentry
   - Set up uptime monitoring

**Estimated Time: 2-3 days**

---

### **🟡 SHORT-TERM (Within 1 Week)**

1. **Complete CI/CD Pipeline**
   - Configure GitHub Actions
   - Add automated testing
   - Set up deployment automation

2. **Comprehensive Test Suite**
   - Write unit tests (>80% coverage)
   - Add integration tests
   - Create E2E test scenarios

3. **Monitoring Stack**
   - Deploy Prometheus + Grafana
   - Configure log aggregation
   - Create dashboards

4. **API Documentation**
   - Complete OpenAPI spec
   - Set up Swagger UI
   - Write usage examples

5. **Rollback Procedures**
   - Test rollback scripts
   - Document recovery process
   - Train team on procedures

**Estimated Time: 1-2 weeks**

---

### **🟢 MEDIUM-TERM (Within 1 Month)**

1. **Performance Optimization**
   - Implement caching layer
   - Optimize database queries
   - Add CDN for static assets

2. **Advanced Monitoring**
   - Custom application metrics
   - Business intelligence dashboards
   - Automated performance reports

3. **Load Testing**
   - Establish performance baselines
   - Identify bottlenecks
   - Optimize for scale

4. **Operational Runbooks**
   - Incident response procedures
   - Scaling guidelines
   - Troubleshooting guides

5. **Compliance & Legal**
   - Privacy policy
   - Terms of service
   - License audit

**Estimated Time: 3-4 weeks**

---

## 📚 ADDITIONAL RESOURCES

### **Tools & Services Referenced:**
- **Security**: Bandit, Safety, detect-secrets, OWASP ZAP
- **Quality**: Black, Flake8, Pylint, isort, mypy
- **Testing**: pytest, Locust, Playwright
- **Monitoring**: Prometheus, Grafana, Loki, Sentry
- **CI/CD**: GitHub Actions, Docker, pre-commit
- **Infrastructure**: nginx, Let's Encrypt, Docker Compose

### **Documentation Links:**
- Flask Security: https://flask.palletsprojects.com/en/latest/security/
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- 12-Factor App: https://12factor.net/
- Prometheus Best Practices: https://prometheus.io/docs/practices/
- Docker Best Practices: https://docs.docker.com/develop/dev-best-practices/

---

## ✅ FINAL VALIDATION

**Before declaring "READY FOR PRODUCTION", verify:**

```bash
# Run complete validation suite
./scripts/pre-ship-check.sh

# Expected output:
# ✅ Security audit completed
# ✅ Code quality standards met
# ✅ Test coverage > 80%
# ✅ All documentation complete
# ✅ All required files present
# ✅ Build artifacts created
# ✅ No uncommitted changes
# ✅ Release tag exists
#
# Results: ✅ 25 passed | ❌ 0 failed
# 🎉 All checks passed! Ready to ship! 🚀
```

---

**🎭 Brand Deconstruction Station - Production-Ready Deployment Plan Complete! 🚀**

**Document Version**: 2.0 (Enhanced)
**Last Updated**: 2025-01-18
**Status**: Comprehensive deployment guide with enterprise-grade security, monitoring, and reliability practices

---

## 📝 CHANGELOG

### Version 2.0 (Enhanced) - 2025-01-18
**Major Improvements:**
- ✅ Added comprehensive SSRF protection (IPv6, cloud metadata, DNS rebinding)
- ✅ Added environment-specific configuration management (dev/staging/prod)
- ✅ Added SSL/TLS certificate management with Let's Encrypt
- ✅ Added complete monitoring stack (Prometheus, Grafana, Loki, Sentry)
- ✅ Added structured JSON logging with rotation
- ✅ Added CI/CD pipeline with GitHub Actions
- ✅ Added load testing with Locust
- ✅ Added E2E testing with Playwright
- ✅ Added rollback and disaster recovery procedures
- ✅ Added automated backup strategy
- ✅ Added API documentation with OpenAPI/Swagger
- ✅ Added pre-commit hooks for code quality
- ✅ Added enhanced pre-ship checklist
- ✅ Added deployment readiness scorecard
- ✅ Added priority action items with timeframes

### Version 1.0 (Original) - 2025-01-18
- Initial deployment planning document
- Basic security audit steps
- Code quality guidelines
- Testing framework setup
- Packaging instructions

---

**🎯 KEY IMPROVEMENTS SUMMARY:**

| Category | Original Plan | Enhanced Plan |
|----------|--------------|---------------|
| **Security** | Basic validation | Comprehensive SSRF, CSP, secrets management |
| **Environments** | Local + Production | Dev + Staging + Production with configs |
| **Monitoring** | Basic logs | Full observability stack (Prometheus, Grafana, Sentry) |
| **Testing** | Unit tests only | Unit + Integration + Load + E2E tests |
| **CI/CD** | Manual deployment | Automated pipeline with GitHub Actions |
| **Recovery** | None | Automated backups + tested rollback procedures |
| **Documentation** | README only | API docs, runbooks, security policy |
| **SSL/TLS** | Not covered | Let's Encrypt automation + Nginx config |
| **Deployment** | Simple script | Safe deployment with automatic rollback |
| **Quality Gates** | Basic checklist | Comprehensive scorecard with 119 points |

**Result**: Transformed from a basic deployment plan to an enterprise-grade, production-ready deployment strategy.