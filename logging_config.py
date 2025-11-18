#!/usr/bin/env python3
"""
Logging configuration for Brand Deconstruction Station
Structured JSON logging with rotation
"""

import logging
import json
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
import traceback


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""

    def format(self, record):
        """Format log record as JSON"""
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'process': record.process,
            'thread': record.thread,
        }

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }

        # Add custom fields if present
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'ip_address'):
            log_data['ip_address'] = record.ip_address
        if hasattr(record, 'url'):
            log_data['url'] = record.url

        return json.dumps(log_data)


def setup_logging(app=None):
    """
    Configure structured logging with rotation for the application.

    Args:
        app: Flask application instance (optional)

    Returns:
        Logger instance
    """
    # Create logs directory
    os.makedirs('logs', exist_ok=True)

    # Get log level from environment
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()

    # JSON formatter for file logs
    json_formatter = JSONFormatter()

    # Human-readable formatter for console
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Application log (JSON, rotating)
    app_handler = RotatingFileHandler(
        'logs/app.json.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    app_handler.setFormatter(json_formatter)
    app_handler.setLevel(logging.INFO)

    # Error log (JSON, rotating)
    error_handler = RotatingFileHandler(
        'logs/errors.json.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    error_handler.setFormatter(json_formatter)
    error_handler.setLevel(logging.ERROR)

    # Access log (JSON, rotating)
    access_handler = RotatingFileHandler(
        'logs/access.json.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    access_handler.setFormatter(json_formatter)
    access_handler.setLevel(logging.INFO)

    # Console handler (human-readable)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(getattr(logging, log_level))

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers = []  # Clear existing handlers
    root_logger.addHandler(app_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)

    # Configure Flask app logger if provided
    if app:
        app.logger.handlers = []
        app.logger.addHandler(app_handler)
        app.logger.addHandler(error_handler)
        app.logger.addHandler(console_handler)
        app.logger.setLevel(getattr(logging, log_level))

        # Configure access logger
        access_logger = logging.getLogger('access')
        access_logger.handlers = []
        access_logger.addHandler(access_handler)
        access_logger.setLevel(logging.INFO)
        access_logger.propagate = False

        return app.logger
    else:
        return root_logger


def log_request(logger, request_obj, response_status=None, response_time=None):
    """
    Log HTTP request with structured data.

    Args:
        logger: Logger instance
        request_obj: Flask request object
        response_status: HTTP response status code
        response_time: Request processing time in seconds
    """
    log_data = {
        'method': request_obj.method,
        'path': request_obj.path,
        'remote_addr': request_obj.remote_addr,
        'user_agent': request_obj.user_agent.string if request_obj.user_agent else None,
    }

    if response_status:
        log_data['status'] = response_status

    if response_time:
        log_data['response_time'] = f"{response_time:.3f}s"

    # Log as structured data
    extra_data = logging.LoggerAdapter(logger, log_data)
    extra_data.info(f"{request_obj.method} {request_obj.path}")


def log_analysis(logger, analysis_id, url, analysis_type, status):
    """
    Log brand analysis event with structured data.

    Args:
        logger: Logger instance
        analysis_id: Unique analysis identifier
        url: Target URL being analyzed
        analysis_type: Type of analysis (quick/deep/mega)
        status: Analysis status (started/completed/failed)
    """
    logger.info(
        f"Analysis {status}: {analysis_id}",
        extra={
            'analysis_id': analysis_id,
            'url': url,
            'analysis_type': analysis_type,
            'status': status
        }
    )


# Export functions
__all__ = [
    'setup_logging',
    'log_request',
    'log_analysis',
    'JSONFormatter',
]
