"""
Configuration settings for the Expense Management App.
"""

import logging
import os
from dotenv import load_dotenv

load_dotenv()

class Config:

    """Base configuration class."""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

    # Upload settings
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', os.path.join('uploads', 'receipts'))
    MAX_CONTENT_LENGTH = os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)  # 16 MB
    logging.info("Upload folder set to: %s", UPLOAD_FOLDER)
    
    # OCR Settings
    OCR_LANGUAGES = ['es', 'en']  # Spanish and English support

    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}