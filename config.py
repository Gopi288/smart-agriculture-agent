"""Configuration module for Smart Agriculture Agent.

Defines configuration parameters for development, testing, and production
environments, including database locations, file upload constraints, model
paths, and external service credentials.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load variables from .env if present
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Config:
    """Base application configuration."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    BASE_DIR = BASE_DIR

    # SQLite persistence
    DATABASE_PATH = Path(os.getenv("DATABASE_PATH", BASE_DIR / "smart_agri.db"))

    # File upload settings
    UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 MB max upload size
    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

    # ML Inference settings
    MODEL_PATH = Path(os.getenv("MODEL_PATH", BASE_DIR / "ml" / "models" / "mobilenetv2_crop_disease.pth"))
    CLASS_INDICES_PATH = Path(
        os.getenv("CLASS_INDICES_PATH", BASE_DIR / "ml" / "models" / "class_indices.json")
    )
    CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.70"))
    UNCERTAINTY_MARGIN = float(os.getenv("UNCERTAINTY_MARGIN", "0.15"))

    # Agricultural Knowledge Base
    KNOWLEDGE_BASE_PATH = BASE_DIR / "data" / "disease_knowledge.json"
    SAMPLE_INPUTS_PATH = BASE_DIR / "data" / "sample_inputs.json"

    # External weather integration
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "").strip()
    WEATHER_API_TIMEOUT = 5  # seconds
    WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"

    # Supported Crops
    SUPPORTED_CROPS = ["Tomato", "Potato", "Corn"]


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing configuration with in-memory or isolated database."""

    DEBUG = False
    TESTING = True
    DATABASE_PATH = BASE_DIR / "test_smart_agri.db"
    CONFIDENCE_THRESHOLD = 0.70


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    TESTING = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}


def get_config():
    """Retrieve active configuration based on FLASK_ENV."""
    env = os.getenv("FLASK_ENV", "development").lower()
    return config_by_name.get(env, DevelopmentConfig)
