#!/usr/bin/env python3
"""
🎭 Brand Deconstruction Station
Corporate Vulnerability Analysis Engine with AI Agents
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
from dotenv import load_dotenv
import json
import time
import random
import requests
from datetime import datetime
import threading
from urllib.parse import urlparse
import tempfile
import zipfile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import logging
import asyncio

# Import security utilities
from security_utils import validate_url_input, validate_api_key, sanitize_filename, rate_limit_key

# Import Google media generation modules
from style_modifiers import StyleModifierEngine, StylePreset, MediaType
from media_generator import GoogleMediaGenerator
from mirror_vision_engine import MirrorVisionEngine, SatiricalTarget, VisualMetaphorPattern
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from logging_config import setup_logging, log_analysis
from monitoring import (
    setup_sentry,
    setup_prometheus,
    record_analysis,
    record_analysis_duration,
    increment_active_analyses,
    decrement_active_analyses,
    record_api_request
)

# Load environment variables from .env file
load_dotenv()
# Also try loading from Desktop keys.env if it exists
desktop_keys = os.path.expanduser('~/Desktop/keys.env')
if os.path.exists(desktop_keys):
    load_dotenv(desktop_keys, override=True)
    logger.info(f"Loaded API keys from {desktop_keys}") if 'logger' in dir() else None

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max request size
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(32).hex())

# Configure structured logging with rotation
logger = setup_logging(app)
logger.info("🎭 Brand Deconstruction Station starting...")

# Initialize monitoring
setup_sentry()
setup_prometheus(app)

# Configure rate limiting
limiter = Limiter(
    app=app,
    key_func=rate_limit_key,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
    strategy="fixed-window"
)

# Configure security headers
# Note: HTTPS enforcement disabled for local development
# Enable force_https=True in production
csp = {
    'default-src': ["'self'"],
    'script-src': ["'self'", "'unsafe-inline'"],  # TODO: Remove unsafe-inline in production
    'style-src': ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
    'font-src': ["'self'", "https://fonts.gstatic.com", "data:"],
    'img-src': ["'self'", "data:", "https:"],
    'connect-src': ["'self'"],
}

# Only apply Talisman in production
if os.getenv('FLASK_ENV') == 'production':
    Talisman(
        app,
        content_security_policy=csp,
        force_https=True,
        strict_transport_security=True,
        strict_transport_security_max_age=31536000,
        frame_options='DENY',
        referrer_policy='strict-origin-when-cross-origin'
    )
    logger.info("✅ Security headers enabled (production mode)")
else:
    # Development mode - no HTTPS enforcement
    Talisman(
        app,
        force_https=False,
        content_security_policy=False
    )
    logger.info("⚠️  Security headers relaxed (development mode)")

# Global state for agent simulation
agent_states = {
    'ceo': {'progress': 0, 'status': 'Standby', 'active': False},
    'research': {'progress': 0, 'status': 'Standby', 'active': False},
    'performance': {'progress': 0, 'status': 'Standby', 'active': False},
    'image': {'progress': 0, 'status': 'Standby', 'active': False}
}

analysis_results = {}
current_analysis_id = None

# Initialize Google media generation engines
style_engine = StyleModifierEngine()
google_api_key = os.getenv('GOOGLE_API_KEY')
logger.info(f"Google API Key present: {bool(google_api_key)}")
media_generator = GoogleMediaGenerator(
    google_api_key=google_api_key
)
logger.info(f"Media generator mock_mode: {media_generator.mock_mode}")

# Initialize Mirror Vision Prompt Crafter - RAW AND UNFILTERED
mirror_vision = MirrorVisionEngine()
logger.info("Mirror Vision engine initialized - NO PR LAYERS, COMPLETELY RAW")

class BrandAnalysisEngine:
    """AI-powered brand analysis engine with multi-agent coordination"""
    
    def __init__(self):
        # Prioritize OpenAI API - only requirement
        # Use validate_api_key to check for placeholder values
        self.openai_api_key = validate_api_key(os.getenv('OPENAI_API_KEY'), 'OpenAI')
        self.anthropic_api_key = validate_api_key(os.getenv('ANTHROPIC_API_KEY'), 'Anthropic')
        self.google_api_key = validate_api_key(os.getenv('GOOGLE_API_KEY'), 'Google')
        self.huggingface_token = validate_api_key(os.getenv('HUGGINGFACE_API_TOKEN'), 'HuggingFace')
        self.elevenlabs_api_key = validate_api_key(os.getenv('ELEVENLABS_API_KEY'), 'ElevenLabs')
        
        # OpenAI is the primary requirement
        if not self.openai_api_key:
            print("⚠️  Warning: OpenAI API key not found. Using enhanced mock mode.")
            print("   For real AI analysis, set OPENAI_API_KEY environment variable.")
        
        print("🔍 Brand Analysis Engine - API Status:")
        print(f"  OpenAI: {'✅' if self.openai_api_key else '❌'}")
        print(f"  Anthropic: {'✅' if self.anthropic_api_key else '❌'}")
        print(f"  Google: {'✅' if self.google_api_key else '❌'}")
        print(f"  Hugging Face: {'✅' if self.huggingface_token else '❌'}")
        print(f"  ElevenLabs: {'✅' if self.elevenlabs_api_key else '❌'}")
        
        # Initialize OpenAI client - primary AI engine
        self.openai_client = None
        self.ai_mode = 'mock'
        
        if self.openai_api_key:
            try:
                import openai
                self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
                self.ai_mode = 'openai'
                print("✅ OpenAI client initialized - Real AI analysis enabled")
            except ImportError:
                print("⚠️  OpenAI package not available, using enhanced mock mode")
            except Exception as e:
                print(f"⚠️  OpenAI client initialization failed: {e}")
        else:
            print("⚠️  Running in mock mode - set OpenAI API key for real analysis")

    def _build_mirror_vision_prompt(self, website_url, vulnerabilities, satirical_angles, image_number, severity="brutal"):
        """Build Mirror Vision YAML prompt - RAW AND UNFILTERED

        NO PR LAYERS - Complete brutal satire using photorealistic specifications
        Generates YAML structure optimized for MidJourney v6+ and Google Imagen
        """

        # Extract key elements
        primary_vulnerability = vulnerabilities[0] if vulnerabilities else "Corporate Contradictions"
        primary_angle = satirical_angles[0] if satirical_angles else "Generic corporate hypocrisy"
        brand_name = website_url.replace('https://', '').replace('http://', '').split('/')[0]

        # Determine satirical target type
        target_keywords = (primary_vulnerability + " " + primary_angle).lower()
        if any(word in target_keywords for word in ["tech", "ai", "algorithm", "data", "software", "platform"]):
            target_type = SatiricalTarget.TECH
        elif any(word in target_keywords for word in ["political", "government", "policy", "regulation"]):
            target_type = SatiricalTarget.POLITICAL
        else:
            target_type = SatiricalTarget.CORPORATE

        # Generate complete Mirror Vision prompt with YAML structure
        mirror_prompt = mirror_vision.generate_prompt(
            brand_name=brand_name,
            vulnerability=primary_vulnerability,
            satirical_angle=primary_angle,
            target_type=target_type,
            severity=severity  # brutal, ruthless, or lethal
        )

        return mirror_prompt
        
        
    def scrape_website(self, url):
        """Scrape basic website content for analysis"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Extract basic info
            content = response.text.lower()
            title = ""
            if "<title>" in content:
                title = content.split("<title>")[1].split("</title>")[0].strip()
            
            return {
                'url': url,
                'title': title,
                'content_length': len(response.text),
                'status_code': response.status_code,
                'scraped_at': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'url': url,
                'error': str(e),
                'scraped_at': datetime.now().isoformat()
            }
    
    def analyze_brand_vulnerabilities(self, website_data, analysis_type='deep'):
        """Generate brand vulnerability analysis with satirical insights using OpenAI or fallback"""
        
        # Determine analysis parameters
        if analysis_type == 'quick':
            num_vulnerabilities = 3
            num_angles = 3
        elif analysis_type == 'deep':
            num_vulnerabilities = 5
            num_angles = 5
        else:  # mega
            num_vulnerabilities = 8
            num_angles = 8
        
        # Use OpenAI for real analysis if available
        if self.ai_mode == 'openai' and self.openai_client:
            return self._analyze_with_openai(website_data, analysis_type, num_vulnerabilities, num_angles)
        else:
            return self._analyze_with_fallback(website_data, analysis_type, num_vulnerabilities, num_angles)
    
    def _analyze_with_openai(self, website_data, analysis_type, num_vulnerabilities, num_angles):
        """Real AI analysis using OpenAI GPT-4"""
        try:
            url = website_data.get('url', 'unknown website')
            title = website_data.get('title', 'unknown brand')
            
            # Create comprehensive analysis prompt
            prompt = f"""Analyze this brand for satirical vulnerabilities and corporate contradictions:

Website: {url}
Title: {title}
Analysis Depth: {analysis_type}

Generate {num_vulnerabilities} brand vulnerabilities and {num_angles} satirical attack angles.

For each vulnerability, provide:
1. Name (concise category)
2. Score (0-10, where 10 = most vulnerable)
3. Description (brief analysis)

For satirical angles, provide witty one-liners that expose corporate hypocrisy.

Return as JSON:
{{
    "vulnerabilities": [
        {{"name": "Category", "score": 8.5, "description": "Analysis here"}},
        ...
    ],
    "satirical_angles": [
        "Witty satirical angle 1",
        ...
    ]
}}

Be clever, satirical, and professionally critical without being offensive."""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.8
            )
            
            # Parse OpenAI response
            content = response.choices[0].message.content
            
            # Extract JSON from response
            try:
                import re
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    ai_analysis = json.loads(json_match.group())
                    vulnerabilities = ai_analysis.get('vulnerabilities', [])
                    satirical_angles = ai_analysis.get('satirical_angles', [])
                else:
                    raise ValueError("No valid JSON found in response")
            except:
                # Fallback parsing if JSON fails
                return self._analyze_with_fallback(website_data, analysis_type, num_vulnerabilities, num_angles)
            
            # Calculate overall score
            avg_score = sum(v.get('score', 5.0) for v in vulnerabilities) / len(vulnerabilities) if vulnerabilities else 7.5
            
            return {
                'vulnerability_score': round(avg_score, 1),
                'vulnerabilities': vulnerabilities[:num_vulnerabilities],
                'satirical_angles': satirical_angles[:num_angles],
                'analysis_type': analysis_type,
                'ai_mode': 'openai',
                'timestamp': datetime.now().isoformat(),
                'website_data': website_data
            }
            
        except Exception as e:
            print(f"OpenAI analysis failed: {e}")
            return self._analyze_with_fallback(website_data, analysis_type, num_vulnerabilities, num_angles)
    
    def _analyze_with_fallback(self, website_data, analysis_type, num_vulnerabilities, num_angles):
        """Fallback analysis with enhanced templates"""
        
        vulnerability_templates = [
            {
                'categories': ['Premium Pricing', 'Artificial Scarcity', 'Feature Removal'],
                'satirical_angles': [
                    'The "courage" to charge more for less',
                    'Revolutionary simplicity through elimination',
                    'Premium minimalism at maximum cost'
                ]
            },
            {
                'categories': ['Innovation Theater', 'Marketing Buzzwords', 'Trend Hijacking'],
                'satirical_angles': [
                    'Disrupting disruption with disruptive innovation',
                    'AI-powered everything (including toasters)',
                    'Sustainable unsustainability initiatives'
                ]
            },
            {
                'categories': ['Customer Lock-in', 'Ecosystem Dependency', 'Planned Obsolescence'],
                'satirical_angles': [
                    'Freedom through proprietary standards',
                    'Infinite compatibility with finite products',
                    'Future-proofing through forced upgrades'
                ]
            }
        ]
        
        # Generate vulnerabilities
        vulnerabilities = []
        for i in range(num_vulnerabilities):
            template = random.choice(vulnerability_templates)
            category = random.choice(template['categories'])
            score = round(random.uniform(6.5, 9.8), 1)
            vulnerabilities.append({
                'name': category,
                'score': score,
                'description': f'Analysis of {category.lower()} patterns in brand strategy'
            })
        
        # Generate satirical angles
        all_angles = []
        for template in vulnerability_templates:
            all_angles.extend(template['satirical_angles'])
        
        satirical_angles = random.sample(all_angles, min(num_angles, len(all_angles)))
        
        # Calculate overall vulnerability score
        avg_score = sum(v['score'] for v in vulnerabilities) / len(vulnerabilities)
        
        return {
            'vulnerability_score': round(avg_score, 1),
            'vulnerabilities': vulnerabilities,
            'satirical_angles': satirical_angles,
            'analysis_type': analysis_type,
            'ai_mode': 'fallback',
            'timestamp': datetime.now().isoformat(),
            'website_data': website_data
        }
    
    def generate_satirical_images(self, analysis_data, count=1, severity="brutal"):
        """Generate satirical brand image concepts using Mirror Vision YAML prompts - RAW AND UNFILTERED"""
        try:
            # Get brand analysis data
            website_url = analysis_data.get('website_data', {}).get('url', 'unknown brand')
            vulnerabilities = [v.get('name', '') for v in analysis_data.get('vulnerabilities', [])]
            satirical_angles = analysis_data.get('satirical_angles', [])

            images = []
            for i in range(count):
                # Generate Mirror Vision YAML prompt - NO PR LAYERS
                mirror_prompt = self._build_mirror_vision_prompt(
                    website_url,
                    vulnerabilities,
                    satirical_angles,
                    i+1,
                    severity=severity
                )

                # Convert to YAML string for storage and display
                yaml_prompt = mirror_prompt.to_yaml()

                # Get Imagen-compatible prompt for actual generation
                imagen_prompt = mirror_prompt.to_imagen_prompt()

                # Extract caption for display
                caption = mirror_prompt.caption

                images.append({
                    'id': f'img_{i+1}_{int(time.time())}',
                    'concept': imagen_prompt,  # Use Imagen-compatible prompt as concept
                    'yaml_prompt': yaml_prompt,  # Full YAML structure
                    'caption': caption,  # Mirror Universe Pete caption
                    'prompt': imagen_prompt,  # For backward compatibility
                    'status': 'mirror_vision_generated',
                    'timestamp': datetime.now().isoformat(),
                    'source': 'mirror-vision-unfiltered',
                    'severity': severity,
                    'metadata': {
                        'resolution': mirror_prompt.resolution,
                        'camera': mirror_prompt.camera,
                        'parameters': mirror_prompt.parameters
                    }
                })

            return images

        except Exception as e:
            print(f"Mirror Vision generation error: {e}")
            # Fallback with basic Mirror Vision structure
            images = []
            brand_name = website_url.replace('https://', '').replace('http://', '').split('/')[0] if 'website_url' in locals() else 'Unknown Brand'
            primary_vulnerability = vulnerabilities[0] if 'vulnerabilities' in locals() and vulnerabilities else 'corporate contradictions'

            for i in range(count):
                fallback_concept = f"Photorealistic corporate environment exposing {brand_name}'s {primary_vulnerability}. 12K resolution, Path-traced, ARRI Alexa 65, Zeiss Otus 85mm f/1.4. Brutal visual metaphor showing the gap between corporate messaging and reality."

                images.append({
                    'id': f'img_{i+1}_{int(time.time())}',
                    'concept': fallback_concept,
                    'yaml_prompt': f"# Mirror Vision Fallback\ndescription: {fallback_concept}",
                    'caption': f"The evidence speaks for itself. {brand_name}'s {primary_vulnerability} exposed through architectural truth-telling.",
                    'prompt': fallback_concept,
                    'status': 'mirror_vision_fallback',
                    'timestamp': datetime.now().isoformat(),
                    'source': 'mirror-vision-emergency-fallback',
                    'severity': severity
                })
            return images

# Initialize the analysis engine
brand_engine = BrandAnalysisEngine()

@app.route('/')
def index():
    """Main application interface"""
    return render_template('brand_station.html')

@app.route('/favicon.ico')
def favicon():
    """Serve cyberpunk-themed favicon"""
    # Create a simple SVG favicon with cyberpunk theme
    favicon_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
        <rect fill="#000011" width="32" height="32"/>
        <circle cx="16" cy="16" r="12" fill="none" stroke="#00ff41" stroke-width="2"/>
        <text x="16" y="20" text-anchor="middle" fill="#00ff41" font-family="monospace" font-size="14" font-weight="bold">🎭</text>
        <rect x="4" y="4" width="24" height="2" fill="#00ff41" opacity="0.7"/>
        <rect x="4" y="26" width="24" height="2" fill="#00ff41" opacity="0.7"/>
    </svg>'''
    
    from flask import Response
    response = Response(favicon_svg, mimetype='image/svg+xml')
    response.headers['Cache-Control'] = 'public, max-age=86400'  # Cache for 1 day
    return response

@app.route('/api/analyze', methods=['POST'])
@limiter.limit("10 per minute")  # Rate limit: 10 analyses per minute
@validate_url_input
def analyze_brand():
    """Start brand analysis process with SSRF protection and rate limiting"""
    global current_analysis_id, analysis_results

    data = request.get_json()
    url = data.get('url')
    analysis_type = data.get('type', 'deep')

    # URL is already validated by @validate_url_input decorator
    # Generate unique analysis ID
    analysis_id = f'analysis_{int(time.time())}_{random.randint(1000, 9999)}'
    current_analysis_id = analysis_id

    # Log analysis start with structured data
    log_analysis(logger, analysis_id, url, analysis_type, 'started')
    
    # Reset agent states
    for agent in agent_states:
        agent_states[agent] = {'progress': 0, 'status': 'Initializing...', 'active': True}
    
    # Start analysis in background thread
    def run_analysis():
        start_time = time.time()
        increment_active_analyses()

        try:
            # Step 1: Website scraping (Research Agent)
            agent_states['research']['status'] = 'Scraping website...'
            website_data = brand_engine.scrape_website(url)

            # Simulate progress for research agent
            for progress in range(0, 101, 20):
                agent_states['research']['progress'] = progress
                time.sleep(0.5)
            agent_states['research']['status'] = 'Complete'

            # Step 2: Brand analysis (CEO Agent)
            agent_states['ceo']['status'] = 'Analyzing brand strategy...'
            for progress in range(0, 101, 15):
                agent_states['ceo']['progress'] = progress
                time.sleep(0.7)

            brand_analysis = brand_engine.analyze_brand_vulnerabilities(website_data, analysis_type)
            agent_states['ceo']['status'] = 'Complete'

            # Step 3: Performance metrics (Performance Agent)
            agent_states['performance']['status'] = 'Calculating metrics...'
            for progress in range(0, 101, 25):
                agent_states['performance']['progress'] = progress
                time.sleep(0.4)
            agent_states['performance']['status'] = 'Complete'

            # Step 4: Image concepts (Image Agent)
            agent_states['image']['status'] = 'Generating concepts...'
            for progress in range(0, 101, 30):
                agent_states['image']['progress'] = progress
                time.sleep(0.3)
            agent_states['image']['status'] = 'Complete'

            # Store results
            analysis_results[analysis_id] = brand_analysis

            # Mark all agents as inactive
            for agent in agent_states:
                agent_states[agent]['active'] = False

            # Record successful analysis
            duration = time.time() - start_time
            record_analysis(analysis_type, 'success')
            record_analysis_duration(analysis_type, duration)
            log_analysis(logger, analysis_id, url, analysis_type, 'completed')

        except Exception as e:
            logger.error(f"Analysis error for {analysis_id}: {e}", exc_info=True)
            for agent in agent_states:
                agent_states[agent]['status'] = 'Error'
                agent_states[agent]['active'] = False

            # Record failed analysis
            duration = time.time() - start_time
            record_analysis(analysis_type, 'error')
            record_analysis_duration(analysis_type, duration)
            log_analysis(logger, analysis_id, url, analysis_type, 'failed')

        finally:
            decrement_active_analyses()
    
    # Start analysis thread
    thread = threading.Thread(target=run_analysis)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'analysis_id': analysis_id,
        'status': 'started',
        'estimated_duration': {'quick': 30, 'deep': 180, 'mega': 600}.get(analysis_type, 180)
    })

@app.route('/api/agent-status')
@limiter.limit("2000 per hour")  # Allow polling every ~2 seconds
def get_agent_status():
    """Get current agent status and progress"""
    return jsonify(agent_states)

@app.route('/api/results/<analysis_id>')
def get_results(analysis_id):
    """Get analysis results"""
    if analysis_id in analysis_results:
        return jsonify(analysis_results[analysis_id])
    else:
        return jsonify({'error': 'Analysis not found'}), 404

@app.route('/api/generate-images', methods=['POST'])
def generate_images():
    """Generate satirical brand images"""
    data = request.get_json()
    analysis_id = data.get('analysis_id', 'current')
    count = data.get('count', 1)
    
    # Use current analysis if 'current' is specified
    if analysis_id == 'current' and current_analysis_id:
        analysis_id = current_analysis_id
    
    if analysis_id not in analysis_results:
        return jsonify({'error': 'Analysis not found. Please run analysis first.'}), 404
    
    analysis_data = analysis_results[analysis_id]
    
    try:
        # Generate images using GPT-4o
        agent_states['image']['active'] = True
        agent_states['image']['status'] = 'Generating concepts...'
        agent_states['image']['progress'] = 50
        
        images = brand_engine.generate_satirical_images(analysis_data, count)
        
        # Store in analysis results
        analysis_results[analysis_id]['generated_images'] = images
        
        agent_states['image']['status'] = 'Complete'
        agent_states['image']['progress'] = 100
        agent_states['image']['active'] = False
        
        return jsonify({
            'status': 'complete',
            'images': images,
            'count': len(images)
        })
        
    except Exception as e:
        agent_states['image']['status'] = 'Error'
        agent_states['image']['active'] = False
        return jsonify({'error': f'Image generation failed: {str(e)}'}), 500

@app.route('/api/export/<format>/<analysis_id>')
def export_results(format, analysis_id):
    """Export analysis results in various formats"""
    if analysis_id not in analysis_results:
        return jsonify({'error': 'Analysis not found'}), 404
    
    data = analysis_results[analysis_id]
    
    if format == 'json':
        # Create JSON file
        json_data = json.dumps(data, indent=2)
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        temp_file.write(json_data)
        temp_file.close()
        
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=f'brand_analysis_{analysis_id}.json',
            mimetype='application/json'
        )
    
    elif format == 'pdf':
        # Create PDF report
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        
        # Title
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, 750, "🎭 Brand Deconstruction Report")
        
        # Basic info
        pdf.setFont("Helvetica", 12)
        y_pos = 720
        pdf.drawString(50, y_pos, f"URL: {data.get('website_data', {}).get('url', 'N/A')}")
        y_pos -= 20
        pdf.drawString(50, y_pos, f"Analysis Type: {data.get('analysis_type', 'N/A')}")
        y_pos -= 20
        pdf.drawString(50, y_pos, f"Vulnerability Score: {data.get('vulnerability_score', 'N/A')}/10")
        y_pos -= 40
        
        # Vulnerabilities
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(50, y_pos, "Key Vulnerabilities:")
        y_pos -= 20
        
        pdf.setFont("Helvetica", 10)
        for vuln in data.get('vulnerabilities', []):
            if y_pos < 100:
                pdf.showPage()
                y_pos = 750
            pdf.drawString(70, y_pos, f"• {vuln['name']}: {vuln['score']}/10")
            y_pos -= 15
        
        y_pos -= 20
        
        # Satirical angles
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(50, y_pos, "Satirical Angles:")
        y_pos -= 20
        
        pdf.setFont("Helvetica", 10)
        for angle in data.get('satirical_angles', []):
            if y_pos < 100:
                pdf.showPage()
                y_pos = 750
            pdf.drawString(70, y_pos, f"• {angle}")
            y_pos -= 15
        
        pdf.save()
        buffer.seek(0)
        
        return send_file(
            io.BytesIO(buffer.read()),
            as_attachment=True,
            download_name=f'brand_analysis_{analysis_id}.pdf',
            mimetype='application/pdf'
        )
    
    elif format == 'html':
        # Create HTML report
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Brand Analysis Report</title>
            <style>
                body {{ font-family: monospace; background: #000; color: #00ff00; padding: 20px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .score {{ font-size: 24px; color: #ff0000; font-weight: bold; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #00ff00; }}
                .vulnerability {{ margin: 10px 0; padding: 10px; background: rgba(0,255,0,0.1); }}
                .angle {{ margin: 5px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎭 Brand Deconstruction Report</h1>
                <p>Target: {data.get('website_data', {}).get('url', 'N/A')}</p>
                <p>Analysis Type: {data.get('analysis_type', 'N/A')}</p>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="section">
                <h2>Vulnerability Score</h2>
                <div class="score">{data.get('vulnerability_score', 'N/A')}/10</div>
            </div>
            
            <div class="section">
                <h2>Key Vulnerabilities</h2>
                {''.join([f'<div class="vulnerability">• {v["name"]}: {v["score"]}/10</div>' for v in data.get('vulnerabilities', [])])}
            </div>
            
            <div class="section">
                <h2>Satirical Angles</h2>
                {''.join([f'<div class="angle">• {angle}</div>' for angle in data.get('satirical_angles', [])])}
            </div>
        </body>
        </html>
        """
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html')
        temp_file.write(html_content)
        temp_file.close()
        
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=f'brand_analysis_{analysis_id}.html',
            mimetype='text/html'
        )
    
    else:
        return jsonify({'error': 'Unsupported format'}), 400

@app.route('/api/generate-actual-images', methods=['POST'])
@limiter.limit("5 per minute")
def generate_actual_images():
    """Generate actual images using Google Imagen API with style modifiers"""
    data = request.json
    analysis_id = data.get('analysis_id')
    style_preset_str = data.get('style_preset', 'editorial')
    custom_modifiers = data.get('custom_modifiers', [])

    # Debug logging
    logger.info(f"Generate actual images request - Analysis ID: {analysis_id}")
    logger.info(f"Current analysis IDs in memory: {list(analysis_results.keys())}")

    if not analysis_id or analysis_id not in analysis_results:
        logger.error(f"Analysis ID {analysis_id} not found in results")
        return jsonify({'error': 'Invalid analysis ID'}), 400

    analysis = analysis_results[analysis_id]
    logger.info(f"Found analysis with keys: {list(analysis.keys())}")

    # Check if we have image concepts (stored in 'generated_images' key)
    if 'generated_images' not in analysis or not analysis['generated_images']:
        logger.error(f"No image concepts in analysis. Available keys: {list(analysis.keys())}")
        return jsonify({'error': 'No image concepts available for this analysis. Please generate image prompts first.'}), 400

    # Convert string to StylePreset enum
    try:
        style_preset = StylePreset(style_preset_str)
    except ValueError:
        style_preset = StylePreset.EDITORIAL

    generated_images = []

    # Run async generation in sync context
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        for concept in analysis['generated_images'][:1]:  # Generate only 1 image
            # Apply style modifiers to the concept (key is 'concept' not 'description')
            styled_prompt = style_engine.apply_modifiers(
                base_prompt=concept['concept'],
                style_preset=style_preset,
                media_type=MediaType.IMAGE,
                custom_modifiers=custom_modifiers
            )

            # Generate actual image
            result = loop.run_until_complete(
                media_generator.generate_image(
                    prompt=styled_prompt,
                    style_preset=style_preset,
                    custom_modifiers=custom_modifiers
                )
            )

            # Check for 'complete' status (not 'success') - matches media_generator return value
            if result['status'] == 'complete':
                generated_images.append({
                    'original_concept': concept['concept'],
                    'styled_prompt': styled_prompt,
                    'image_url': result['image_url'],  # Use 'image_url' key from media_generator
                    'metadata': result.get('metadata', {})
                })
            else:
                generated_images.append({
                    'original_concept': concept['concept'],
                    'error': result.get('error', 'Generation failed')
                })

        return jsonify({
            'status': 'success',
            'analysis_id': analysis_id,
            'style_preset': style_preset.value,  # Convert enum to string
            'generated_images': generated_images,
            'mock_mode': media_generator.mock_mode
        })

    except Exception as e:
        logger.error(f"Image generation error: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        loop.close()

@app.route('/api/generate-videos', methods=['POST'])
@limiter.limit("2 per minute")
def generate_videos():
    """Generate videos using Google Veo API with style modifiers"""
    data = request.json
    analysis_id = data.get('analysis_id')
    style_preset_str = data.get('style_preset', 'cinematic')
    duration = data.get('duration', 6)  # 4, 6, or 8 seconds
    aspect_ratio = data.get('aspect_ratio', '16:9')  # 16:9 or 9:16
    resolution = data.get('resolution', '1080p')  # 720p or 1080p

    if not analysis_id or analysis_id not in analysis_results:
        return jsonify({'error': 'Invalid analysis ID'}), 400

    analysis = analysis_results[analysis_id]

    # Get brand vulnerabilities for video generation
    vulnerabilities = analysis.get('vulnerabilities', [])
    satirical_angles = analysis.get('satirical_angles', [])

    if not vulnerabilities:
        return jsonify({'error': 'No vulnerabilities available for video generation'}), 400

    # Convert string to StylePreset enum
    try:
        style_preset = StylePreset(style_preset_str)
    except ValueError:
        style_preset = StylePreset.CINEMATIC

    # Run async generation in sync context
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # Create video prompt based on primary vulnerability
        primary_vuln = vulnerabilities[0]
        subject = f"Corporate brand showing {primary_vuln['name']}"
        action = satirical_angles[0] if satirical_angles else "revealing corporate contradictions"

        # Generate Veo prompt with modifiers
        veo_prompt = style_engine.generate_veo_prompt(
            subject=subject,
            action=action,
            style_preset=style_preset,
            duration=duration,
            aspect_ratio=aspect_ratio,
            resolution=resolution
        )

        # Generate video
        result = loop.run_until_complete(
            media_generator.generate_video(
                prompt=veo_prompt['full_text'],
                style_preset=style_preset,
                duration=duration,
                aspect_ratio=aspect_ratio,
                resolution=resolution
            )
        )

        if result['status'] in ['processing', 'pending']:
            # Video generation started, return job ID for status checking
            return jsonify({
                'status': 'processing',
                'job_id': result['job_id'],
                'veo_prompt': veo_prompt,
                'estimated_time': f"{duration + 10} seconds",
                'mock_mode': media_generator.mock_mode
            })
        else:
            return jsonify({
                'status': 'error',
                'error': result.get('error', 'Video generation failed')
            }), 500

    except Exception as e:
        logger.error(f"Video generation error: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        loop.close()

@app.route('/api/video-status/<job_id>')
@limiter.limit("1000 per hour")  # Allow frequent polling (1 request every 3.6 seconds)
def check_video_status(job_id):
    """Check the status of a video generation job"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        status = loop.run_until_complete(
            media_generator.check_video_status(job_id)
        )
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error checking video status: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        loop.close()

@app.route('/api/style-presets')
def get_style_presets():
    """Get available style presets for media generation"""
    # Get the preset names from the style engine
    preset_names = ['editorial', 'photorealistic', 'cyberpunk', 'vintage', 'documentary', 'cinematic', 'satirical']
    return jsonify({
        'image_presets': preset_names,
        'video_presets': preset_names,
        'preset_descriptions': {
            'editorial': 'Professional, publication-ready style',
            'photorealistic': 'Hyper-realistic with deep detail',
            'cyberpunk': 'Dark, neon-lit dystopian aesthetic',
            'vintage': 'Film noir and retro aesthetics',
            'documentary': 'Raw, authentic visual journalism',
            'cinematic': 'Epic, movie-quality production',
            'satirical': 'Exaggerated, darkly humorous style'
        }
    })

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'operational',
        'timestamp': datetime.now().isoformat(),
        'agents': len(agent_states),
        'ai_mode': brand_engine.ai_mode,
        'openai_available': brand_engine.openai_client is not None,
        'live_mode': brand_engine.ai_mode == 'openai',
        'google_media_available': not media_generator.mock_mode
    })

if __name__ == '__main__':
    print("🎭 Brand Deconstruction Station Starting...")
    print("📡 Server: http://localhost:3000")
    print("🤖 AI Agents: Initialized")
    print("🎮 Interface: Cyberpunk Terminal")
    
    # Status will be shown by BrandAnalysisEngine initialization
    print("\n" + "="*50)
    print("🚀 Ready for brand deconstruction!")
    print("="*50 + "\n")
    
    app.run(host='0.0.0.0', port=3000, debug=True, threaded=True)
