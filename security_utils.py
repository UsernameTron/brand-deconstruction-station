#!/usr/bin/env python3
"""
Security utilities for Brand Deconstruction Station
Comprehensive input validation and SSRF protection
"""

from functools import wraps
from urllib.parse import urlparse
from ipaddress import ip_address, ip_network
import socket
import logging
from flask import request, jsonify

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
    ip_network('0.0.0.0/8'),           # Current network
    ip_network('100.64.0.0/10'),       # Shared address space
    ip_network('192.0.0.0/24'),        # IETF Protocol
    ip_network('192.0.2.0/24'),        # TEST-NET-1
    ip_network('198.18.0.0/15'),       # Benchmarking
    ip_network('198.51.100.0/24'),     # TEST-NET-2
    ip_network('203.0.113.0/24'),      # TEST-NET-3
    ip_network('::1/128'),             # IPv6 loopback
    ip_network('fc00::/7'),            # IPv6 private
    ip_network('fe80::/10'),           # IPv6 link-local
    ip_network('ff00::/8'),            # IPv6 multicast
    ip_network('::/128'),              # IPv6 unspecified
    ip_network('::ffff:0:0/96'),       # IPv4-mapped IPv6
]

# Cloud metadata endpoints (AWS, GCP, Azure, DigitalOcean, etc.)
BLOCKED_HOSTNAMES = [
    'metadata.google.internal',        # GCP
    '169.254.169.254',                 # AWS/Azure/DigitalOcean metadata
    'metadata',                        # Generic
    'instance-data',                   # EC2
    'metadata.azure.com',              # Azure
    'metadata.packet.net',             # Packet
    'metadata.platformequinix.com',    # Equinix Metal
]

# Blocked URL schemes
ALLOWED_SCHEMES = ['http', 'https']


def is_safe_url(url):
    """
    Comprehensive URL safety validation to prevent SSRF attacks.

    Protects against:
    - Private IPv4/IPv6 addresses
    - Loopback addresses
    - Link-local addresses
    - Cloud metadata endpoints
    - DNS rebinding attacks
    - Invalid URL schemes

    Args:
        url: The URL to validate

    Returns:
        tuple: (is_safe: bool, message: str)
    """
    try:
        # Basic URL parsing
        parsed = urlparse(url)

        # Check scheme
        if parsed.scheme not in ALLOWED_SCHEMES:
            return False, f"Invalid scheme: {parsed.scheme}. Only http and https allowed"

        hostname = parsed.hostname
        if not hostname:
            return False, "Missing hostname"

        # Check for blocked hostnames
        hostname_lower = hostname.lower()
        for blocked in BLOCKED_HOSTNAMES:
            if blocked in hostname_lower:
                logger.warning(f"Blocked metadata endpoint attempt: {hostname}")
                return False, "Access to metadata endpoints is not allowed"

        # Resolve DNS and check IP (prevents DNS rebinding)
        try:
            # Get all IP addresses for hostname
            addr_info = socket.getaddrinfo(hostname, None)

            for addr in addr_info:
                ip_str = addr[4][0]

                try:
                    ip = ip_address(ip_str)

                    # Check against blocked networks
                    for blocked in BLOCKED_NETWORKS:
                        if ip in blocked:
                            logger.warning(f"Blocked private/internal IP: {ip} from {hostname}")
                            return False, "Access to private or internal IP addresses is not allowed"

                    # Additional checks
                    if ip.is_private:
                        return False, "Private IP addresses are not allowed"

                    if ip.is_loopback:
                        return False, "Loopback addresses are not allowed"

                    if ip.is_link_local:
                        return False, "Link-local addresses are not allowed"

                    if ip.is_multicast:
                        return False, "Multicast addresses are not allowed"

                    if ip.is_reserved:
                        return False, "Reserved IP addresses are not allowed"

                except ValueError as e:
                    logger.error(f"Invalid IP address format: {ip_str} - {e}")
                    return False, f"Invalid IP address format"

        except socket.gaierror as e:
            logger.error(f"DNS resolution failed for {hostname}: {e}")
            return False, "DNS resolution failed"
        except Exception as e:
            logger.error(f"Error resolving hostname {hostname}: {e}")
            return False, f"Error resolving hostname"

        return True, "OK"

    except Exception as e:
        logger.error(f"URL validation error for {url}: {e}")
        return False, f"Invalid URL format: {str(e)}"


def validate_url_input(f):
    """
    Decorator to validate URL inputs with comprehensive SSRF protection.

    Usage:
        @app.route('/api/analyze', methods=['POST'])
        @validate_url_input
        def analyze_brand():
            # URL is already validated
            pass
    """
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
            return jsonify({'error': 'URL too long (max 2048 characters)'}), 400

        # Comprehensive SSRF check
        is_safe, message = is_safe_url(url)
        if not is_safe:
            logger.warning(f"Blocked unsafe URL: {url} - Reason: {message}")
            return jsonify({
                'error': 'Invalid URL',
                'details': message
            }), 400

        return f(*args, **kwargs)

    return decorated_function


def validate_api_key(key, service_name):
    """
    Validate API key format before use.

    Args:
        key: The API key to validate
        service_name: Name of the service (for logging)

    Returns:
        str or None: Validated key or None if invalid
    """
    if not key:
        return None

    # Remove whitespace
    key = key.strip()

    # Check for minimum length
    if len(key) < 20:
        logger.warning(f"Invalid {service_name} API key format (too short)")
        return None

    # Check for placeholder values
    placeholder_patterns = [
        'your-',
        'your_api_key',
        'placeholder',
        'example',
        'test_key',
        'sk-1234567890',  # Common test pattern
    ]

    key_lower = key.lower()
    for pattern in placeholder_patterns:
        if pattern in key_lower:
            logger.warning(f"Placeholder {service_name} API key detected: {pattern}")
            return None

    return key


def sanitize_filename(filename):
    """
    Sanitize filename to prevent path traversal attacks.

    Args:
        filename: The filename to sanitize

    Returns:
        str: Sanitized filename
    """
    import re

    # Remove path components
    filename = filename.replace('/', '_').replace('\\', '_')

    # Remove directory traversal attempts
    filename = filename.replace('..', '')

    # Allow only alphanumeric, dash, underscore, and dot
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)

    # Limit length
    if len(filename) > 255:
        filename = filename[:255]

    return filename


def rate_limit_key():
    """
    Get rate limiting key based on client IP or API key.

    Returns:
        str: Rate limit key
    """
    # Try to get real IP from headers (if behind proxy)
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        # Get first IP in chain
        return forwarded_for.split(',')[0].strip()

    return request.remote_addr


# Export all utilities
__all__ = [
    'is_safe_url',
    'validate_url_input',
    'validate_api_key',
    'sanitize_filename',
    'rate_limit_key',
    'BLOCKED_NETWORKS',
    'BLOCKED_HOSTNAMES',
    'ALLOWED_SCHEMES',
]
