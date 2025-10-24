"""
Application Configuration
Centralized settings management using Pydantic
"""

from typing import List, Optional, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
    
    # Application
    APP_NAME: str = "Freelancer Feedback Assistant"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = Field(..., min_length=32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    BCRYPT_ROUNDS: int = 12
    
    # Database
    DATABASE_URL: str = Field(..., description="PostgreSQL connection string")
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600
    DB_ECHO: bool = False
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 50
    REDIS_SOCKET_TIMEOUT: int = 5
    REDIS_SOCKET_CONNECT_TIMEOUT: int = 5
    
    # Blackbox AI Configuration
    BLACKBOX_API_KEY: str = Field(default="sk-test-key", description="Blackbox API key")
    OPENAI_BASE_URL: str = "https://api.blackbox.ai/v1"  # Blackbox API endpoint
    OPENAI_MODEL: str = "blackboxai-pro"  # Blackbox AI model
    OPENAI_MAX_TOKENS: int = 1000
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_TIMEOUT: int = 120
    
    # AI Settings
    AI_CACHE_ENABLED: bool = True
    AI_CACHE_TTL: int = 3600
    MAX_FEEDBACK_LENGTH: int = 5000
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: Optional[List[str]] = None
    CELERY_TIMEZONE: str = "UTC"
    CELERY_ENABLE_UTC: bool = True
    CELERY_TASK_TRACK_STARTED: bool = True
    CELERY_TASK_TIME_LIMIT: int = 300
    CELERY_TASK_SOFT_TIME_LIMIT: int = 240
    
    @field_validator("CELERY_ACCEPT_CONTENT", mode="before")
    @classmethod
    def parse_celery_accept_content(cls, v):
        """Parse Celery accept content from string or list"""
        if v is None or v == "":
            return ["json"]
        if isinstance(v, str):
            # Try to parse as JSON first
            try:
                import json
                return json.loads(v)
            except:
                # If not JSON, split by comma
                return [item.strip() for item in v.split(",") if item.strip()]
        return v if v else ["json"]
    
    # Email (SendGrid)
    SENDGRID_API_KEY: Optional[str] = None
    SENDGRID_FROM_EMAIL: str = "noreply@freelancerfeedback.com"
    SENDGRID_FROM_NAME: str = "Freelancer Feedback Assistant"
    EMAIL_ENABLED: bool = True
    EMAIL_TEMPLATES_DIR: str = "app/templates/email"
    
    # Slack
    SLACK_CLIENT_ID: Optional[str] = None
    SLACK_CLIENT_SECRET: Optional[str] = None
    SLACK_SIGNING_SECRET: Optional[str] = None
    SLACK_BOT_TOKEN: Optional[str] = None
    SLACK_ENABLED: bool = False
    SLACK_WEBHOOK_URL: Optional[str] = None
    
    # File Storage
    STORAGE_BACKEND: str = "local"
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_FILE_EXTENSIONS: Union[str, List[str]] = ".pdf,.png,.jpg,.jpeg,.gif,.svg,.psd,.ai,.sketch,.fig"
    
    # S3 (Optional)
    S3_BUCKET_NAME: Optional[str] = None
    S3_REGION: str = "us-east-1"
    S3_ACCESS_KEY_ID: Optional[str] = None
    S3_SECRET_ACCESS_KEY: Optional[str] = None
    S3_ENDPOINT_URL: Optional[str] = None
    S3_PUBLIC_URL: Optional[str] = None
    
    # CORS
    ALLOWED_ORIGINS: Union[str, List[str]] = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000"
    ALLOWED_HOSTS: Optional[List[str]] = None
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: Optional[List[str]] = None
    CORS_ALLOW_HEADERS: Optional[List[str]] = None
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_AUTH_PER_MINUTE: int = 5
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE: str = "logs/app.log"
    LOG_MAX_BYTES: int = 10485760  # 10MB
    LOG_BACKUP_COUNT: int = 5
    
    # Sentry (Optional)
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1
    
    # Monitoring
    METRICS_ENABLED: bool = True
    METRICS_PORT: int = 9090
    HEALTH_CHECK_ENABLED: bool = True
    
    # Feature Flags
    FEATURE_AI_PARSING: bool = True
    FEATURE_SLACK_INTEGRATION: bool = False
    FEATURE_EMAIL_NOTIFICATIONS: bool = True
    FEATURE_FILE_UPLOADS: bool = True
    FEATURE_WEBHOOKS: bool = False
    
    # GDPR & Privacy
    GDPR_ENABLED: bool = True
    DATA_RETENTION_DAYS: int = 365
    ANONYMIZE_DELETED_USERS: bool = True
    COOKIE_CONSENT_REQUIRED: bool = True
    ENCRYPT_PII: bool = True
    AUDIT_LOG_ENABLED: bool = True
    DATA_EXPORT_ENABLED: bool = True
    
    # Testing
    TEST_DATABASE_URL: Optional[str] = None
    TEST_OPENAI_API_KEY: Optional[str] = None
    PYTEST_WORKERS: str = "auto"
    COVERAGE_THRESHOLD: int = 80
    
    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def parse_allowed_hosts(cls, v):
        """Parse allowed hosts from string or list"""
        if v is None or v == "":
            return ["*"]
        if isinstance(v, str):
            return [host.strip() for host in v.split(",") if host.strip()]
        return v if v else ["*"]
    
    @field_validator("CORS_ALLOW_METHODS", mode="before")
    @classmethod
    def parse_cors_methods(cls, v):
        """Parse CORS methods from string or list"""
        if v is None or v == "":
            return ["*"]
        if isinstance(v, str):
            return [method.strip() for method in v.split(",") if method.strip()]
        return v if v else ["*"]
    
    @field_validator("CORS_ALLOW_HEADERS", mode="before")
    @classmethod
    def parse_cors_headers(cls, v):
        """Parse CORS headers from string or list"""
        if v is None or v == "":
            return ["*"]
        if isinstance(v, str):
            return [header.strip() for header in v.split(",") if header.strip()]
        return v if v else ["*"]
    
    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            if not v or v.strip() == "":
                return ["http://localhost:3000", "http://localhost:5173"]
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v if v else ["http://localhost:3000", "http://localhost:5173"]
    
    @field_validator("ALLOWED_FILE_EXTENSIONS", mode="before")
    @classmethod
    def parse_file_extensions(cls, v):
        """Parse file extensions from string or list"""
        if isinstance(v, str):
            if not v or v.strip() == "":
                return [".pdf", ".png", ".jpg", ".jpeg", ".gif", ".svg"]
            return [ext.strip() for ext in v.split(",") if ext.strip()]
        return v if v else [".pdf", ".png", ".jpg", ".jpeg", ".gif", ".svg"]
    
    @property
    def max_upload_size_bytes(self) -> int:
        """Convert max upload size from MB to bytes"""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.ENVIRONMENT.lower() == "development"
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment"""
        return self.ENVIRONMENT.lower() == "testing"
    
    def get_database_url(self) -> str:
        """Get appropriate database URL based on environment"""
        if self.is_testing and self.TEST_DATABASE_URL:
            return self.TEST_DATABASE_URL
        return self.DATABASE_URL


# Create global settings instance
settings = Settings()


# Validate critical settings on startup
def validate_settings():
    """
    Validate critical settings on application startup
    Raises ValueError if any critical setting is missing or invalid
    """
    errors = []
    
    # Check required settings
    if not settings.SECRET_KEY or len(settings.SECRET_KEY) < 32:
        errors.append("SECRET_KEY must be at least 32 characters long")
    
    if not settings.DATABASE_URL:
        errors.append("DATABASE_URL is required")
    
    if not settings.BLACKBOX_API_KEY:
        errors.append("BLACKBOX_API_KEY is required for AI features")
    
    if settings.EMAIL_ENABLED and not settings.SENDGRID_API_KEY:
        errors.append("SENDGRID_API_KEY is required when EMAIL_ENABLED is True")
    
    if settings.SLACK_ENABLED and not all([
        settings.SLACK_CLIENT_ID,
        settings.SLACK_CLIENT_SECRET,
        settings.SLACK_SIGNING_SECRET,
    ]):
        errors.append("Slack credentials are required when SLACK_ENABLED is True")
    
    # Production-specific checks
    if settings.is_production:
        if settings.DEBUG:
            errors.append("DEBUG must be False in production")
        
        if "localhost" in settings.ALLOWED_ORIGINS:
            errors.append("localhost should not be in ALLOWED_ORIGINS in production")
        
        if not settings.SENTRY_DSN:
            errors.append("SENTRY_DSN is recommended for production error tracking")
    
    if errors:
        raise ValueError(
            "Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
        )


# Validate settings on import (can be disabled for testing)
# Validation is skipped during import to allow for flexible testing
# Call validate_settings() explicitly in production startup
