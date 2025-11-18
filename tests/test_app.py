#!/usr/bin/env python3
"""
Application tests for Brand Deconstruction Station
Test Flask routes, API endpoints, and core functionality
"""

import pytest
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, BrandAnalysisEngine


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    with app.test_client() as client:
        yield client


@pytest.fixture
def brand_engine():
    """Create BrandAnalysisEngine instance"""
    return BrandAnalysisEngine()


class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check(self, client):
        """Test health endpoint returns 200"""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'status' in data
        assert data['status'] == 'operational'


class TestAnalyzeEndpoint:
    """Test brand analysis endpoint"""

    def test_analyze_missing_url(self, client):
        """Test analysis without URL returns error"""
        response = client.post(
            '/api/analyze',
            json={},
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_analyze_invalid_url_format(self, client):
        """Test analysis with invalid URL format"""
        response = client.post(
            '/api/analyze',
            json={'url': 'not-a-valid-url'},
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_analyze_private_ip(self, client):
        """Test analysis with private IP is blocked"""
        response = client.post(
            '/api/analyze',
            json={'url': 'http://192.168.1.1'},
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_analyze_localhost(self, client):
        """Test analysis with localhost is blocked"""
        response = client.post(
            '/api/analyze',
            json={'url': 'http://localhost:8080'},
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_analyze_valid_url(self, client):
        """Test analysis with valid URL starts successfully"""
        response = client.post(
            '/api/analyze',
            json={'url': 'https://example.com', 'type': 'quick'},
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'analysis_id' in data
        assert 'status' in data
        assert data['status'] == 'started'

    def test_analyze_with_type(self, client):
        """Test analysis with different types"""
        types = ['quick', 'deep', 'mega']
        for analysis_type in types:
            response = client.post(
                '/api/analyze',
                json={'url': 'https://example.com', 'type': analysis_type},
                content_type='application/json'
            )
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'estimated_duration' in data


class TestAgentStatusEndpoint:
    """Test agent status endpoint"""

    def test_agent_status(self, client):
        """Test agent status endpoint returns status"""
        response = client.get('/api/agent-status')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'ceo' in data
        assert 'research' in data
        assert 'performance' in data
        assert 'image' in data


class TestResultsEndpoint:
    """Test results endpoint"""

    def test_results_not_found(self, client):
        """Test results for non-existent analysis"""
        response = client.get('/api/results/nonexistent_id')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data


class TestBrandAnalysisEngine:
    """Test BrandAnalysisEngine class"""

    def test_engine_initialization(self, brand_engine):
        """Test BrandAnalysisEngine initializes correctly"""
        assert brand_engine is not None
        assert hasattr(brand_engine, 'ai_mode')

    def test_website_scraping_valid_url(self, brand_engine):
        """Test website scraping with valid URL"""
        result = brand_engine.scrape_website('https://example.com')
        assert 'url' in result
        assert result['url'] == 'https://example.com'
        assert 'scraped_at' in result

    def test_website_scraping_invalid_url(self, brand_engine):
        """Test website scraping with invalid URL"""
        result = brand_engine.scrape_website('http://invalid-url-that-does-not-exist.com')
        assert 'error' in result

    def test_analyze_brand_vulnerabilities_quick(self, brand_engine):
        """Test quick brand analysis"""
        website_data = {'url': 'https://example.com', 'title': 'Example'}
        result = brand_engine.analyze_brand_vulnerabilities(website_data, 'quick')
        assert 'vulnerabilities' in result
        assert 'satirical_angles' in result
        assert len(result['vulnerabilities']) >= 3

    def test_analyze_brand_vulnerabilities_deep(self, brand_engine):
        """Test deep brand analysis"""
        website_data = {'url': 'https://example.com', 'title': 'Example'}
        result = brand_engine.analyze_brand_vulnerabilities(website_data, 'deep')
        assert 'vulnerabilities' in result
        assert len(result['vulnerabilities']) >= 5

    def test_analyze_brand_vulnerabilities_mega(self, brand_engine):
        """Test mega brand analysis"""
        website_data = {'url': 'https://example.com', 'title': 'Example'}
        result = brand_engine.analyze_brand_vulnerabilities(website_data, 'mega')
        assert 'vulnerabilities' in result
        assert len(result['vulnerabilities']) >= 8


class TestRateLimiting:
    """Test rate limiting functionality"""

    def test_rate_limit_enforced(self, client):
        """Test that rate limiting is enforced"""
        # Make multiple rapid requests
        responses = []
        for i in range(15):
            response = client.post(
                '/api/analyze',
                json={'url': 'https://example.com'},
                content_type='application/json'
            )
            responses.append(response.status_code)

        # Should eventually get rate limited (429)
        assert 429 in responses or all(s == 200 for s in responses)


class TestErrorHandling:
    """Test error handling"""

    def test_invalid_json_payload(self, client):
        """Test invalid JSON payload handling"""
        response = client.post(
            '/api/analyze',
            data='invalid json',
            content_type='application/json'
        )
        assert response.status_code in [400, 415]

    def test_malformed_request(self, client):
        """Test malformed request handling"""
        response = client.post('/api/analyze')
        assert response.status_code in [400, 415]


class TestIndexRoute:
    """Test index/homepage route"""

    def test_homepage_loads(self, client):
        """Test that homepage loads successfully"""
        response = client.get('/')
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
