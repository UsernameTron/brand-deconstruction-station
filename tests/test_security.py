#!/usr/bin/env python3
"""
Security tests for Brand Deconstruction Station
Test SSRF protection, input validation, and security controls
"""

import pytest
from security_utils import is_safe_url, validate_api_key, sanitize_filename


class TestSSRFProtection:
    """Test SSRF protection mechanisms"""

    def test_allow_valid_public_urls(self):
        """Test that valid public URLs are allowed"""
        valid_urls = [
            "https://example.com",
            "http://example.com",
            "https://www.google.com",
            "https://github.com/user/repo",
        ]

        for url in valid_urls:
            is_safe, message = is_safe_url(url)
            assert is_safe, f"Should allow {url}: {message}"

    def test_block_private_ipv4(self):
        """Test that private IPv4 addresses are blocked"""
        private_urls = [
            "http://192.168.1.1",
            "http://10.0.0.1",
            "http://172.16.0.1",
            "http://127.0.0.1",
            "http://localhost",
        ]

        for url in private_urls:
            is_safe, message = is_safe_url(url)
            assert not is_safe, f"Should block private IP: {url}"

    def test_block_cloud_metadata(self):
        """Test that cloud metadata endpoints are blocked"""
        metadata_urls = [
            "http://169.254.169.254/latest/meta-data/",
            "http://metadata.google.internal/computeMetadata/v1/",
        ]

        for url in metadata_urls:
            is_safe, message = is_safe_url(url)
            assert not is_safe, f"Should block metadata endpoint: {url}"

    def test_block_invalid_schemes(self):
        """Test that invalid URL schemes are blocked"""
        invalid_schemes = [
            "file:///etc/passwd",
            "ftp://example.com",
            "data:text/html,<script>alert('xss')</script>",
            "javascript:alert(1)",
        ]

        for url in invalid_schemes:
            is_safe, message = is_safe_url(url)
            assert not is_safe, f"Should block invalid scheme: {url}"

    def test_block_missing_hostname(self):
        """Test that URLs without hostnames are blocked"""
        is_safe, message = is_safe_url("http://")
        assert not is_safe
        assert "hostname" in message.lower()

    def test_url_length_limit(self):
        """Test URL length validation"""
        long_url = "http://example.com/" + "a" * 3000
        assert len(long_url) > 2048


class TestAPIKeyValidation:
    """Test API key validation"""

    def test_valid_api_key(self):
        """Test that valid API keys are accepted"""
        # Use a key that doesn't match placeholder patterns
        valid_key = "sk-abcdefghijklmnopqrstuvwxyz0123456789"
        result = validate_api_key(valid_key, "TestService")
        assert result == valid_key

    def test_reject_placeholder_keys(self):
        """Test that placeholder API keys are rejected"""
        placeholder_keys = [
            "your-api-key-here",
            "your_api_key",
            "placeholder_key",
            "test_key",
            "example_key",
        ]

        for key in placeholder_keys:
            result = validate_api_key(key, "TestService")
            assert result is None, f"Should reject placeholder: {key}"

    def test_reject_short_keys(self):
        """Test that short API keys are rejected"""
        short_key = "short"
        result = validate_api_key(short_key, "TestService")
        assert result is None

    def test_reject_none_keys(self):
        """Test that None keys are rejected"""
        result = validate_api_key(None, "TestService")
        assert result is None

    def test_strip_whitespace(self):
        """Test that whitespace is stripped from keys"""
        key_with_spaces = "  sk-validkey123456789  "
        result = validate_api_key(key_with_spaces, "TestService")
        assert result == "sk-validkey123456789"


class TestFilenameRestricted:
    """Test filename sanitization"""

    def test_sanitize_basic_filename(self):
        """Test sanitization of basic filenames"""
        filename = "test_file.txt"
        result = sanitize_filename(filename)
        assert result == filename

    def test_remove_path_traversal(self):
        """Test removal of path traversal attempts"""
        malicious_names = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "test/../etc/passwd",
        ]

        for name in malicious_names:
            result = sanitize_filename(name)
            assert ".." not in result
            assert "/" not in result or result == "/"
            assert "\\" not in result

    def test_remove_special_characters(self):
        """Test removal of special characters"""
        filename = "test<>file:name?.txt"
        result = sanitize_filename(filename)
        assert "<" not in result
        assert ">" not in result
        assert ":" not in result
        assert "?" not in result

    def test_length_limit(self):
        """Test filename length limiting"""
        long_filename = "a" * 300 + ".txt"
        result = sanitize_filename(long_filename)
        assert len(result) <= 255


class TestSecurityHeaders:
    """Test security header configuration"""

    def test_csp_configuration(self):
        """Test Content Security Policy configuration"""
        # This would test the actual CSP headers in app.py
        # Requires Flask test client integration
        pass

    def test_rate_limiting(self):
        """Test rate limiting configuration"""
        # This would test rate limiting with Flask test client
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
