"""
Logging Configuration
Structured logging with JSON format for production
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict

import structlog
from structlog.types import EventDict, Processor

from app.core.config import settings


def add_app_context(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """
    Add application context to log entries
    """
    event_dict["app"] = settings.APP_NAME
    event_dict["version"] = settings.APP_VERSION
    event_dict["environment"] = settings.ENVIRONMENT
    return event_dict


def censor_sensitive_data(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """
    Censor sensitive data in logs (PII, passwords, tokens)
    """
    sensitive_keys = {
        "password", "token", "secret", "api_key", "authorization",
        "credit_card", "ssn", "email", "phone"
    }
    
    def censor_dict(d: Dict) -> Dict:
        """Recursively censor sensitive keys in dictionaries"""
        censored = {}
        for key, value in d.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                censored[key] = "***REDACTED***"
            elif isinstance(value, dict):
                censored[key] = censor_dict(value)
            elif isinstance(value, list):
                censored[key] = [
                    censor_dict(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                censored[key] = value
        return censored
    
    return censor_dict(event_dict)


def setup_logging() -> structlog.BoundLogger:
    """
    Set up structured logging configuration
    
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_file_path = Path(settings.LOG_FILE)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper()),
    )
    
    # Add file handler if not in development
    if not settings.is_development:
        from logging.handlers import RotatingFileHandler
        
        file_handler = RotatingFileHandler(
            settings.LOG_FILE,
            maxBytes=settings.LOG_MAX_BYTES,
            backupCount=settings.LOG_BACKUP_COUNT,
        )
        file_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
        logging.root.addHandler(file_handler)
    
    # Configure structlog processors
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        add_app_context,
    ]
    
    # Add PII censoring in production
    if settings.is_production or settings.ENCRYPT_PII:
        processors.append(censor_sensitive_data)
    
    # Format output based on environment
    if settings.LOG_FORMAT == "json" or settings.is_production:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.extend([
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer(colors=True),
        ])
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Initialize Sentry if configured
    if settings.SENTRY_DSN:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.SENTRY_ENVIRONMENT,
            traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
            ],
            send_default_pii=False,  # GDPR compliance
        )
    
    return structlog.get_logger()


# Create global logger instance
logger = setup_logging()
