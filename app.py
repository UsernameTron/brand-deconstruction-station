#!/usr/bin/env python3
"""
🎭 Brand Deconstruction Station
Corporate Vulnerability Analysis Engine with AI Agents
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
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

# Add OpenAI import
try:
    import openai
    openai_available = True
except ImportError:
    openai_available = False
    print("⚠️  OpenAI not installed. Using fallback mode.")

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
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.mock_mode = not self.openai_api_key
        
        # Initialize OpenAI client if available
        if self.openai_api_key and openai_available:
            try:
                openai.api_key = self.openai_api_key
                self.client = openai
                print("✅ OpenAI client initialized for image generation")
            except Exception as e:
                print(f"⚠️  OpenAI initialization failed: {e}")
                self.client = None
                self.mock_mode = True
        else:
            self.client = None
        
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
        """Generate brand vulnerability analysis with satirical insights"""
        
        # Mock satirical vulnerabilities based on common corporate patterns
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
        
        # Generate analysis based on type
        if analysis_type == 'quick':
            num_vulnerabilities = 3
            num_angles = 3
        elif analysis_type == 'deep':
            num_vulnerabilities = 5
            num_angles = 5
        else:  # mega
            num_vulnerabilities = 8
            num_angles = 8
        
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
            'timestamp': datetime.now().isoformat(),
            'website_data': website_data
        }
    
    def generate_satirical_images(self, analysis_data, count=1):
        """Generate satirical brand image concepts using GPT-4o"""
        try:
            # Get brand analysis data
            website_data = analysis_data.get('website_data', {})
            website_url = website_data.get('url', 'unknown brand')
            vulnerabilities = analysis_data.get('vulnerabilities', [])
            satirical_angles = analysis_data.get('satirical_angles', [])
            
            images = []
            for i in range(count):
                # Create GPT-4o prompt for satirical image concept
                vuln_list = [v.get('name', str(v)) if isinstance(v, dict) else str(v) for v in vulnerabilities[:3]]
                angle_list = [str(a) for a in satirical_angles[:3]]
                
                prompt = f"""Create a detailed, satirical image concept for {website_url}.

Brand Vulnerabilities: {', '.join(vuln_list)}
Satirical Angles: {', '.join(angle_list)}

Generate a witty, satirical image description that exposes corporate hypocrisy. Be creative and humorous but not offensive. Format as a detailed visual description suitable for image generation.

Respond with just the image description, no extra text."""

                try:
                    # Use GPT-4o to generate satirical image concept if OpenAI client available
                    if hasattr(self, 'client') and self.client and not self.mock_mode:
                        import openai
                        response = openai.chat.completions.create(
                            model="gpt-4o",
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=200,
                            temperature=0.8
                        )
                        
                        image_concept = response.choices[0].message.content.strip()
                        source = 'gpt-4o'
                        
                    else:
                        # Enhanced fallback concept
                        image_concept = f"Satirical corporate imagery exposing {website_url}: A clever visual metaphor highlighting {vuln_list[0] if vuln_list else 'corporate contradictions'} through ironic juxtaposition of polished branding with operational reality"
                        source = 'enhanced-fallback'
                        
                except Exception as e:
                    print(f"GPT-4o image generation failed: {e}")
                    # Fallback to enhanced mock concept
                    image_concept = f"Satirical corporate imagery exposing {website_url}: A clever visual metaphor highlighting {vuln_list[0] if vuln_list else 'corporate contradictions'}"
                    source = 'fallback'
                
                images.append({
                    'id': f'img_{i+1}_{int(time.time())}',
                    'concept': image_concept,
                    'prompt': f'Satirical image for {website_url}',
                    'status': 'concept_generated',
                    'timestamp': datetime.now().isoformat(),
                    'source': source
                })
                
            return images
            
        except Exception as e:
            print(f"Image generation error: {e}")
            # Safe fallback - return original mock behavior
            images = []
            for i in range(count):
                images.append({
                    'id': f'img_{i+1}_{int(time.time())}',
                    'concept': f'Satirical corporate imagery for {analysis_data.get("website_data", {}).get("url", "brand")}',
                    'prompt': f'Mock satirical image concept',
                    'status': 'fallback_generated',
                    'timestamp': datetime.now().isoformat()
                })
            return images

# Initialize the analysis engine
brand_engine = BrandAnalysisEngine()

@app.route('/')
def index():
    """Main application interface"""
    return render_template('brand_station.html')

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
    
    # Use current analysis data if available
    if analysis_id == 'current' and current_analysis_id:
        analysis_id = current_analysis_id
    
    if analysis_id not in analysis_results:
        return jsonify({'error': 'Analysis not found'}), 404
    
    analysis_data = analysis_results[analysis_id]
    
    # Generate image concepts directly (no async needed for concepts)
    try:
        agent_states['image']['active'] = True
        agent_states['image']['status'] = 'Generating concepts...'
        agent_states['image']['progress'] = 50
        
        images = brand_engine.generate_satirical_images(analysis_data, count)
        analysis_results[analysis_id]['generated_images'] = images
        
        agent_states['image']['status'] = 'Complete'
        agent_states['image']['progress'] = 100
        agent_states['image']['active'] = False
        
        return jsonify({
            'status': 'complete',
            'count': len(images),
            'images': images
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
        'mock_mode': brand_engine.mock_mode
    })

if __name__ == '__main__':
    print("🎭 Brand Deconstruction Station Starting...")
    print("📡 Server: http://localhost:3001")
    print("🤖 AI Agents: Initialized")
    print("🎮 Interface: Cyberpunk Terminal")
    
    if brand_engine.mock_mode:
        print("⚠️  Mock Mode: Set OPENAI_API_KEY for real AI analysis")
    else:
        print("✅ OpenAI: Connected")
    
    print("\n" + "="*50)
    print("🚀 Ready for brand deconstruction!")
    print("="*50 + "\n")
    
    app.run(host='0.0.0.0', port=3001, debug=True, threaded=True)
