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

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Global state for agent simulation
agent_states = {
    'ceo': {'progress': 0, 'status': 'Standby', 'active': False},
    'research': {'progress': 0, 'status': 'Standby', 'active': False},
    'performance': {'progress': 0, 'status': 'Standby', 'active': False},
    'image': {'progress': 0, 'status': 'Standby', 'active': False}
}

analysis_results = {}
current_analysis_id = None

class BrandAnalysisEngine:
    """AI-powered brand analysis engine with multi-agent coordination"""
    
    def __init__(self):
        # Prioritize OpenAI API - only requirement
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.huggingface_token = os.getenv('HUGGINGFACE_API_TOKEN')
        self.elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
        
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
    
    def _build_pentagram_prompt(self, website_url, vulnerabilities, satirical_angles, image_number):
        """Build structured prompt using PENTAGRAM framework for image generation
        
        P - Purpose: Define the core satirical intent
        E - Elements: Key visual components and symbols
        N - Narrative: Story or message being conveyed
        T - Tone: Emotional and stylistic approach
        A - Audience: Target understanding and cultural context
        G - Guidelines: Technical and creative constraints
        R - Results: Expected output characteristics
        A - Aesthetics: Visual style and artistic direction
        M - Metaphors: Symbolic representations and analogies
        """
        
        # Extract key elements for framework
        primary_vulnerability = vulnerabilities[0] if vulnerabilities else "Corporate Contradictions"
        primary_angle = satirical_angles[0] if satirical_angles else "Generic corporate hypocrisy"
        brand_name = website_url.replace('https://', '').replace('http://', '').split('/')[0]
        
        pentagram_structure = f"""
P - PURPOSE: Create satirical visual commentary exposing "{primary_vulnerability}" in {brand_name}'s brand strategy
E - ELEMENTS: Corporate imagery, visual metaphors, symbolic contradictions, brand iconography subversion
N - NARRATIVE: "{primary_angle}" - revealing the gap between corporate messaging and reality
T - TONE: Witty, clever, incisive yet professional - satirical without being offensive or crude
A - AUDIENCE: Media-literate consumers who understand corporate marketing tactics and visual symbolism
G - GUIDELINES: Professional quality, suitable for editorial use, legally defensible parody/commentary
R - RESULTS: Single powerful image concept that immediately communicates the satirical point
A - AESTHETICS: Contemporary editorial illustration style, clean composition, symbolic clarity
M - METAPHORS: Visual symbols that represent {primary_vulnerability} through recognizable corporate imagery

TARGET VULNERABILITIES: {', '.join(vulnerabilities[:3])}
SATIRICAL PERSPECTIVES: {', '.join(satirical_angles[:2])}
BRAND CONTEXT: {brand_name}
IMAGE SEQUENCE: #{image_number} of conceptual series"""
        
        return pentagram_structure
        
        
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
    
    def generate_satirical_images(self, analysis_data, count=1):
        """Generate satirical brand image concepts using PENTAGRAM framework"""
        try:
            # Get brand analysis data
            website_url = analysis_data.get('website_data', {}).get('url', 'unknown brand')
            vulnerabilities = [v.get('name', '') for v in analysis_data.get('vulnerabilities', [])]
            satirical_angles = analysis_data.get('satirical_angles', [])
            
            images = []
            for i in range(count):
                # Apply PENTAGRAM Framework for structured prompt generation
                pentagram_prompt = self._build_pentagram_prompt(website_url, vulnerabilities, satirical_angles, i+1)
                
                # Create enhanced prompt using PENTAGRAM structure
                prompt = f"""PENTAGRAM PROMPT FRAMEWORK - SATIRICAL BRAND ANALYSIS

{pentagram_prompt}

DIRECTIVE: Generate a witty, satirical image description that exposes corporate hypocrisy through visual metaphor. Be creative and humorous but not offensive. Format as a detailed visual description suitable for professional image generation.

OUTPUT: Respond with just the image description, no preamble or extra text."""

                try:
                    if self.openai_client:
                        # Use GPT-4o to generate satirical image concept
                        response = self.openai_client.chat.completions.create(
                            model="gpt-4o",
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=200,
                            temperature=0.8
                        )
                        
                        content = response.choices[0].message.content
                        image_concept = content.strip() if content else "No image concept generated"
                        source = 'gpt-4o'
                    else:
                        raise Exception("OpenAI client not available")
                        
                except Exception as e:
                    print(f"GPT-4o image generation failed: {e}")
                    # Fallback to enhanced PENTAGRAM-structured concept
                    brand_name = website_url.replace('https://', '').replace('http://', '').split('/')[0]
                    primary_vulnerability = vulnerabilities[0] if vulnerabilities else 'corporate contradictions'
                    primary_angle = satirical_angles[0] if satirical_angles else 'generic corporate hypocrisy'
                    
                    image_concept = f"PENTAGRAM-Structured Satirical Concept: Visual metaphor exposing {brand_name}'s {primary_vulnerability} through {primary_angle}. A professionally composed editorial illustration that cleverly subverts corporate imagery to reveal underlying contradictions in brand messaging."
                    source = 'pentagram-fallback'
                
                images.append({
                    'id': f'img_{i+1}_{int(time.time())}',
                    'concept': image_concept,
                    'prompt': prompt,
                    'status': 'concept_generated',
                    'timestamp': datetime.now().isoformat(),
                    'source': source
                })
                
            return images
            
        except Exception as e:
            print(f"Image generation error: {e}")
            # Safe fallback with PENTAGRAM structure awareness
            images = []
            brand_name = website_url.replace('https://', '').replace('http://', '').split('/')[0] if 'website_url' in locals() else 'Unknown Brand'
            for i in range(count):
                images.append({
                    'id': f'img_{i+1}_{int(time.time())}',
                    'concept': f'PENTAGRAM Framework Concept #{i+1}: Satirical editorial illustration analyzing {brand_name} corporate messaging contradictions through visual metaphor',
                    'prompt': f'PENTAGRAM fallback prompt for {brand_name}',
                    'status': 'pentagram_fallback_generated',
                    'timestamp': datetime.now().isoformat(),
                    'source': 'pentagram-emergency-fallback'
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
def analyze_brand():
    """Start brand analysis process"""
    global current_analysis_id, analysis_results
    
    data = request.get_json()
    url = data.get('url')
    analysis_type = data.get('type', 'deep')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Generate unique analysis ID
    analysis_id = f'analysis_{int(time.time())}_{random.randint(1000, 9999)}'
    current_analysis_id = analysis_id
    
    # Reset agent states
    for agent in agent_states:
        agent_states[agent] = {'progress': 0, 'status': 'Initializing...', 'active': True}
    
    # Start analysis in background thread
    def run_analysis():
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
                
        except Exception as e:
            print(f"Analysis error: {e}")
            for agent in agent_states:
                agent_states[agent]['status'] = 'Error'
                agent_states[agent]['active'] = False
    
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

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'operational',
        'timestamp': datetime.now().isoformat(),
        'agents': len(agent_states),
        'ai_mode': brand_engine.ai_mode,
        'openai_available': brand_engine.openai_client is not None,
        'live_mode': brand_engine.ai_mode == 'openai'
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
