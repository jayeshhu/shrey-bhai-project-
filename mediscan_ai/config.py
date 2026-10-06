"""
MediScan AI - Configuration Module
Demonstrates: dictionaries, environment variables, classes, encapsulation
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory — absolute path to project root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    """Base configuration class - demonstrates OOP encapsulation"""

    # Flask secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fallback-dev-key-change-in-production'

    # Database configuration — use absolute path for SQLite
    _db_path = os.path.join(BASE_DIR, 'instance', 'mediscan.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{_db_path}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File upload configuration
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 10 * 1024 * 1024))  # 10 MB
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

    # AI API Configuration
    AI_PROVIDER = os.environ.get('AI_PROVIDER', 'gemini').lower()
    AI_API_KEY = os.environ.get('AI_API_KEY', '')

    # OpenAI
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')

    # Gemini
    GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-1.5-flash')

    # Groq
    GROQ_MODEL = os.environ.get('GROQ_MODEL', 'llama-3.1-8b-instant')

    # Charts directory
    CHARTS_FOLDER = os.path.join('static', 'generated_charts')

    @classmethod
    def is_ai_configured(cls) -> bool:
        """Check if AI API is properly configured"""
        return bool(cls.AI_API_KEY and cls.AI_API_KEY != 'your_api_key_here')

    @classmethod
    def get_ai_info(cls) -> dict:
        """Return AI configuration info as a dictionary"""
        return {
            'provider': cls.AI_PROVIDER,
            'configured': cls.is_ai_configured(),
            'model': cls._get_model_name(),
        }

    @classmethod
    def _get_model_name(cls) -> str:
        """Get model name based on provider"""
        models = {
            'openai': cls.OPENAI_MODEL,
            'gemini': cls.GEMINI_MODEL,
            'groq': cls.GROQ_MODEL,
        }
        return models.get(cls.AI_PROVIDER, 'unknown')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


# Configuration dictionary - demonstrates dictionaries
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}


def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config_map.get(env, config_map['default'])
