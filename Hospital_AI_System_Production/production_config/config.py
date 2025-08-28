"""
Production Configuration for Hospital AI System
Centralized configuration management
"""

import os
from typing import Dict, Any
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    """Database configuration settings."""
    
    # PostgreSQL Database
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "hospital_ai_db"
    POSTGRES_USER: str = "hospital_user"
    POSTGRES_PASSWORD: str = ""
    
    # Redis Cache
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Connection Pool
    MAX_CONNECTIONS: int = 20
    MIN_CONNECTIONS: int = 5
    
    class Config:
        env_file = ".env"


class MLModelConfig(BaseSettings):
    """ML Model configuration settings."""
    
    # Model Path
    MODEL_PATH: str = r"C:\Users\saksh\OneDrive\Desktop\No-show_Hospital\Medical-Appointment-No-shows-prediction\model_save\no_show_model.pkl"
    
    # Model Parameters
    FEATURE_COUNT: int = 98
    PREDICTION_THRESHOLD: float = 0.5
    
    # Risk Assessment Thresholds
    LOW_RISK_THRESHOLD: float = 0.3
    MEDIUM_RISK_THRESHOLD: float = 0.6
    HIGH_RISK_THRESHOLD: float = 0.8
    
    class Config:
        env_file = ".env"


class HospitalConfig(BaseSettings):
    """Hospital system configuration."""
    
    # Working Hours
    WORKING_HOURS_START: int = 9  # 9 AM
    WORKING_HOURS_END: int = 18   # 6 PM
    SLOT_DURATION_MINUTES: int = 30
    
    # Slots per day
    SLOTS_PER_DAY: int = 18  # 9 AM to 6 PM, 30 min each
    
    # Buffer Times (minutes)
    LOW_RISK_BUFFER: int = 0
    MEDIUM_RISK_BUFFER: int = 15
    HIGH_RISK_BUFFER: int = 30
    
    # Waitlist Settings
    MAX_WAITLIST_SIZE: int = 1000
    WAITLIST_PRIORITY_WEIGHTS: Dict[str, float] = {
        "medical_urgency": 0.4,
        "waitlist_time": 0.3,
        "risk_level": 0.2,
        "doctor_preference": 0.1
    }
    
    class Config:
        env_file = ".env"


class APIConfig(BaseSettings):
    """API configuration settings."""
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # API Version
    API_VERSION: str = "v1"
    API_PREFIX: str = f"/api/{API_VERSION}"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # CORS Settings
    ALLOWED_ORIGINS: list = ["*"]
    ALLOWED_METHODS: list = ["GET", "POST", "PUT", "DELETE"]
    
    class Config:
        env_file = ".env"


class NotificationConfig(BaseSettings):
    """Notification system configuration."""
    
    # SMS Configuration
    SMS_ENABLED: bool = True
    SMS_PROVIDER: str = "twilio"  # or other providers
    
    # Email Configuration
    EMAIL_ENABLED: bool = True
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    
    # Push Notifications
    PUSH_NOTIFICATIONS_ENABLED: bool = True
    
    # Reminder Settings
    REMINDER_24H_BEFORE: bool = True
    REMINDER_48H_BEFORE: bool = True
    REMINDER_1WEEK_BEFORE: bool = False
    
    class Config:
        env_file = ".env"


class LoggingConfig(BaseSettings):
    """Logging configuration."""
    
    # Log Level
    LOG_LEVEL: str = "INFO"
    
    # Log Format
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Log Files
    LOG_FILE: str = "logs/hospital_ai.log"
    ERROR_LOG_FILE: str = "logs/error.log"
    
    # Log Rotation
    MAX_LOG_SIZE: int = 100 * 1024 * 1024  # 100 MB
    BACKUP_COUNT: int = 5
    
    class Config:
        env_file = ".env"


class SecurityConfig(BaseSettings):
    """Security configuration."""
    
    # JWT Settings
    JWT_SECRET_KEY: str = "your-secret-key-here"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Password Settings
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_SPECIAL_CHAR: bool = True
    
    # Session Settings
    SESSION_TIMEOUT_MINUTES: int = 60
    
    class Config:
        env_file = ".env"


# Main Configuration Class
class Config:
    """Main configuration class combining all settings."""
    
    def __init__(self):
        self.database = DatabaseConfig()
        self.ml_model = MLModelConfig()
        self.hospital = HospitalConfig()
        self.api = APIConfig()
        self.notifications = NotificationConfig()
        self.logging = LoggingConfig()
        self.security = SecurityConfig()
    
    def get_database_url(self) -> str:
        """Get database connection URL."""
        return f"postgresql://{self.database.POSTGRES_USER}:{self.database.POSTGRES_PASSWORD}@{self.database.POSTGRES_HOST}:{self.database.POSTGRES_PORT}/{self.database.POSTGRES_DB}"
    
    def get_redis_url(self) -> str:
        """Get Redis connection URL."""
        return f"redis://{self.database.REDIS_HOST}:{self.database.REDIS_PORT}/{self.database.REDIS_DB}"


# Global configuration instance
config = Config()
