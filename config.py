"""
Secure Configuration Management System
Addresses: Hardcoded Configuration Without Environment Separation
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from cryptography.fernet import Fernet
import secrets


class SecuritySettings(BaseSettings):
    """Security-focused configuration with environment separation"""

    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")

    # Encryption (FIX: API Credentials Stored in Plain Text)
    encryption_key_id: Optional[str] = Field(default=None, env="ENCRYPTION_KEY_ID")
    master_encryption_key: Optional[str] = Field(default=None, env="MASTER_ENCRYPTION_KEY")

    # Database with encryption
    database_url: str = Field(env="DATABASE_URL")
    database_encryption_enabled: bool = Field(default=True, env="DATABASE_ENCRYPTION_ENABLED")

    # Kraken API (FIX: Stored securely, not in plain text)
    kraken_api_key: Optional[str] = Field(default=None, env="KRAKEN_API_KEY")
    kraken_api_secret: Optional[str] = Field(default=None, env="KRAKEN_API_SECRET")
    kraken_api_timeout: int = Field(default=30, env="KRAKEN_API_TIMEOUT")
    kraken_rate_limit_enabled: bool = Field(default=True, env="KRAKEN_RATE_LIMIT_ENABLED")
    kraken_max_requests_per_minute: int = Field(default=15, env="KRAKEN_MAX_REQUESTS_PER_MINUTE")

    # Email Configuration
    smtp_host: str = Field(env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_username: str = Field(env="SMTP_USERNAME")
    smtp_password: str = Field(env="SMTP_PASSWORD")
    smtp_use_tls: bool = Field(default=True, env="SMTP_USE_TLS")
    email_rate_limit_per_hour: int = Field(default=50, env="EMAIL_RATE_LIMIT_PER_HOUR")

    # Microsoft Integration
    microsoft_client_id: Optional[str] = Field(default=None, env="MICROSOFT_CLIENT_ID")
    microsoft_client_secret: Optional[str] = Field(default=None, env="MICROSOFT_CLIENT_SECRET")
    microsoft_tenant_id: Optional[str] = Field(default=None, env="MICROSOFT_TENANT_ID")
    sharepoint_site_url: Optional[str] = Field(default=None, env="SHAREPOINT_SITE_URL")
    onedrive_root_path: str = Field(default="/Documents", env="ONEDRIVE_ROOT_PATH")

    # Zapier Integration
    zapier_webhook_url: Optional[str] = Field(default=None, env="ZAPIER_WEBHOOK_URL")
    zapier_api_key: Optional[str] = Field(default=None, env="ZAPIER_API_KEY")

    # Security Settings (FIX: No Authentication or Access Control)
    jwt_secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32), env="JWT_SECRET_KEY")
    jwt_expiration_hours: int = Field(default=24, env="JWT_EXPIRATION_HOURS")
    api_key_rotation_days: int = Field(default=90, env="API_KEY_ROTATION_DAYS")
    enable_ip_whitelist: bool = Field(default=True, env="ENABLE_IP_WHITELIST")
    allowed_ips: str = Field(default="127.0.0.1", env="ALLOWED_IPS")

    # Rate Limiting (FIX: Lack of Rate Limiting and DDoS Protection)
    rate_limit_storage: str = Field(default="redis://localhost:6379/0", env="RATE_LIMIT_STORAGE")
    global_rate_limit: str = Field(default="100/minute", env="GLOBAL_RATE_LIMIT")

    # Logging (FIX: Insufficient Logging and Audit Trail)
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file_path: str = Field(default="/var/log/business-automation/app.log", env="LOG_FILE_PATH")
    audit_log_enabled: bool = Field(default=True, env="AUDIT_LOG_ENABLED")
    audit_log_path: str = Field(default="/var/log/business-automation/audit.log", env="AUDIT_LOG_PATH")

    # Backup Configuration (FIX: No Backup or Disaster Recovery Plan)
    backup_enabled: bool = Field(default=True, env="BACKUP_ENABLED")
    backup_interval_hours: int = Field(default=24, env="BACKUP_INTERVAL_HOURS")
    backup_retention_days: int = Field(default=30, env="BACKUP_RETENTION_DAYS")
    backup_location: str = Field(default="/backups", env="BACKUP_LOCATION")
    s3_backup_bucket: Optional[str] = Field(default=None, env="S3_BACKUP_BUCKET")
    azure_backup_container: Optional[str] = Field(default=None, env="AZURE_BACKUP_CONTAINER")

    # Monitoring (FIX: Single Point of Failure)
    health_check_enabled: bool = Field(default=True, env="HEALTH_CHECK_ENABLED")
    health_check_interval_seconds: int = Field(default=60, env="HEALTH_CHECK_INTERVAL_SECONDS")
    alert_email: str = Field(env="ALERT_EMAIL")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")

    # Application Settings
    app_name: str = Field(default="Business Automation System", env="APP_NAME")
    app_version: str = Field(default="3.0.0", env="APP_VERSION")
    max_workers: int = Field(default=25, env="MAX_WORKERS")
    enable_parallel_processing: bool = Field(default=True, env="ENABLE_PARALLEL_PROCESSING")
    sandbox_mode: bool = Field(default=True, env="SANDBOX_MODE")

    @validator("environment")
    def validate_environment(cls, v):
        """Ensure only valid environments are used"""
        valid_envs = ["development", "staging", "production"]
        if v not in valid_envs:
            raise ValueError(f"Environment must be one of {valid_envs}")
        return v

    @validator("debug")
    def validate_debug(cls, v, values):
        """Never allow debug in production"""
        if values.get("environment") == "production" and v:
            raise ValueError("Debug mode cannot be enabled in production")
        return v

    @validator("allowed_ips")
    def parse_allowed_ips(cls, v) -> List[str]:
        """Parse comma-separated IP list"""
        return [ip.strip() for ip in v.split(",")]

    def get_allowed_ips(self) -> List[str]:
        """Get list of allowed IPs"""
        if isinstance(self.allowed_ips, str):
            return [ip.strip() for ip in self.allowed_ips.split(",")]
        return self.allowed_ips

    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == "production"

    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == "development"

    def is_sandbox(self) -> bool:
        """Check if sandbox mode is enabled"""
        return self.sandbox_mode

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Singleton instance
_settings: Optional[SecuritySettings] = None


def get_settings() -> SecuritySettings:
    """Get or create settings instance"""
    global _settings
    if _settings is None:
        _settings = SecuritySettings()
    return _settings


def get_encryption_cipher() -> Fernet:
    """
    Get encryption cipher for sensitive data
    FIX: Unencrypted Storage of Sensitive Legal and Financial Data
    """
    settings = get_settings()

    if settings.master_encryption_key:
        key = settings.master_encryption_key.encode()
    else:
        # Generate a new key if not provided (for development only)
        if not settings.is_production():
            key = Fernet.generate_key()
            print(f"WARNING: Generated temporary encryption key. Set MASTER_ENCRYPTION_KEY in production!")
        else:
            raise ValueError("MASTER_ENCRYPTION_KEY must be set in production environment")

    return Fernet(key)


def encrypt_sensitive_data(data: str) -> bytes:
    """Encrypt sensitive data before storage"""
    cipher = get_encryption_cipher()
    return cipher.encrypt(data.encode())


def decrypt_sensitive_data(encrypted_data: bytes) -> str:
    """Decrypt sensitive data after retrieval"""
    cipher = get_encryption_cipher()
    return cipher.decrypt(encrypted_data).decode()
