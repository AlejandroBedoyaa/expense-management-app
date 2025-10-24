import logging
import os
from dotenv import load_dotenv

load_dotenv()
assert os.getenv('TELEGRAM_BOT_TOKEN') not in ['your_telegram_bot_token_here', None], "ERROR: Token no configurado correctamente"

class Config:
    # Logging configuration
    # Configurar logging
    logging.basicConfig(
        # filename=os.getenv('LOG_FILE', 'logs/bot.log'),
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
    )

    # Handler to write bots logs to file
    LOG_BOT_FOLDER = os.getenv('LOG_BOT_FILE', os.path.join('logs', 'bot.log'))
    file_handler = logging.FileHandler(LOG_BOT_FOLDER, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
    logging.getLogger().addHandler(file_handler)
    logging.info("Bot log folder set to: %s", LOG_BOT_FOLDER)

    # External libraries logging configuration
    EXTERNAL_LOG_FILE = os.getenv('LOG_BOT_EXTERNAL_LIBS_FILE', os.path.join('logs', 'external_libs.log'))
    external_handler = logging.FileHandler(EXTERNAL_LOG_FILE, encoding='utf-8')
    external_handler.setLevel(logging.INFO)
    external_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
    logging.getLogger("telegram").addHandler(external_handler)
    logging.getLogger("telegram").propagate = False
    logging.getLogger("httpx").addHandler(external_handler)
    logging.getLogger("httpx").propagate = False
    logging.getLogger("requests").addHandler(external_handler)
    logging.getLogger("requests").propagate = False
    logging.info("External libraries log folder set to: %s", EXTERNAL_LOG_FILE)

    """Base configuration class."""
    SECRET_KEY = os.getenv('SECRET_KEY')
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
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or \
        'sqlite:///' + os.path.join('expenses_dev.db')

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or \
        'sqlite:///' + os.path.join('expenses.db')

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # In-memory database for tests
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}