#!/usr/bin/env python3
"""
Monitoring and observability for Brand Deconstruction Station
Prometheus metrics and Sentry error tracking
"""

import os
import logging
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Histogram, Gauge

logger = logging.getLogger(__name__)

# Try to import Sentry SDK (optional dependency)
try:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    SENTRY_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️  Sentry SDK not available: {e}")
    SENTRY_AVAILABLE = False
except Exception as e:
    logger.warning(f"⚠️  Sentry SDK import failed: {e}")
    SENTRY_AVAILABLE = False

# Custom Prometheus metrics
analysis_counter = None
analysis_duration = None
api_requests = None
active_analyses = None
metrics = None


def filter_sensitive_data(event, hint):
    """
    Filter sensitive data before sending to Sentry.

    Args:
        event: Sentry event dictionary
        hint: Additional context

    Returns:
        Modified event or None to drop the event
    """
    # Remove API keys from error data
    if 'extra' in event:
        for key in list(event['extra'].keys()):
            if any(sensitive in key.lower() for sensitive in ['api_key', 'token', 'secret', 'password']):
                event['extra'][key] = '[REDACTED]'

    # Remove sensitive headers
    if 'request' in event and 'headers' in event['request']:
        sensitive_headers = ['Authorization', 'X-API-Key', 'Cookie', 'X-Auth-Token']
        for header in sensitive_headers:
            event['request']['headers'].pop(header, None)

    # Remove sensitive query parameters
    if 'request' in event and 'query_string' in event['request']:
        query_string = event['request']['query_string']
        if query_string and any(param in query_string.lower() for param in ['key', 'token', 'secret']):
            event['request']['query_string'] = '[REDACTED]'

    return event


def setup_sentry():
    """
    Initialize Sentry error tracking if enabled.

    Returns:
        bool: True if Sentry was initialized successfully
    """
    if not os.getenv('SENTRY_ENABLED', 'False').lower() == 'true':
        logger.info("⚠️  Sentry monitoring disabled")
        return False

    sentry_dsn = os.getenv('SENTRY_DSN')
    if not sentry_dsn:
        logger.warning("⚠️  SENTRY_DSN not set, skipping Sentry initialization")
        return False

    try:
        # Configure logging integration
        sentry_logging = LoggingIntegration(
            level=logging.INFO,  # Capture info and above as breadcrumbs
            event_level=logging.ERROR  # Send errors as events
        )

        # Initialize Sentry
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[
                FlaskIntegration(),
                sentry_logging,
            ],
            traces_sample_rate=float(os.getenv('SENTRY_TRACES_SAMPLE_RATE', '0.1')),
            environment=os.getenv('SENTRY_ENVIRONMENT', 'development'),
            release=f"brand-station@{os.getenv('VERSION', '1.0.0')}",
            before_send=filter_sensitive_data,
            attach_stacktrace=True,
            send_default_pii=False,  # Don't send PII
        )

        logger.info("✅ Sentry error tracking enabled")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to initialize Sentry: {e}")
        return False


def setup_prometheus(app):
    """
    Initialize Prometheus metrics for the Flask application.

    Args:
        app: Flask application instance

    Returns:
        PrometheusMetrics instance
    """
    global metrics, analysis_counter, analysis_duration, api_requests, active_analyses

    if not os.getenv('PROMETHEUS_ENABLED', 'False').lower() == 'true':
        logger.info("⚠️  Prometheus metrics disabled")
        return None

    try:
        # Initialize Flask metrics exporter
        metrics = PrometheusMetrics(app)

        # Custom metrics for brand analysis
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
            'external_api_requests_total',
            'Total API requests to external services',
            ['service', 'status']
        )

        active_analyses = Gauge(
            'active_analyses',
            'Number of currently running analyses'
        )

        logger.info("✅ Prometheus metrics enabled at /metrics")
        return metrics

    except Exception as e:
        logger.error(f"❌ Failed to initialize Prometheus: {e}")
        return None


def record_analysis(analysis_type, status):
    """
    Record a brand analysis event in Prometheus.

    Args:
        analysis_type: Type of analysis (quick/deep/mega)
        status: Status of analysis (success/error)
    """
    if analysis_counter:
        analysis_counter.labels(
            analysis_type=analysis_type,
            status=status
        ).inc()


def record_analysis_duration(analysis_type, duration):
    """
    Record the duration of a brand analysis.

    Args:
        analysis_type: Type of analysis
        duration: Duration in seconds
    """
    if analysis_duration:
        analysis_duration.labels(
            analysis_type=analysis_type
        ).observe(duration)


def increment_active_analyses():
    """Increment the active analyses counter."""
    if active_analyses:
        active_analyses.inc()


def decrement_active_analyses():
    """Decrement the active analyses counter."""
    if active_analyses:
        active_analyses.dec()


def record_api_request(service, status):
    """
    Record an external API request.

    Args:
        service: Name of the service (openai/anthropic/google/etc)
        status: Status of request (success/error)
    """
    if api_requests:
        api_requests.labels(
            service=service,
            status=status
        ).inc()


# Export monitoring functions
__all__ = [
    'setup_sentry',
    'setup_prometheus',
    'record_analysis',
    'record_analysis_duration',
    'increment_active_analyses',
    'decrement_active_analyses',
    'record_api_request',
]
