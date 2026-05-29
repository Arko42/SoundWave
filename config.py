import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'soundwave-secret-key-2024-ultra-secure')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'soundwave.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload settings
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'uploads')
    SONGS_FOLDER = os.path.join(UPLOAD_FOLDER, 'songs')
    COVERS_FOLDER = os.path.join(UPLOAD_FOLDER, 'covers')
    AVATARS_FOLDER = os.path.join(UPLOAD_FOLDER, 'avatars')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max upload
    ALLOWED_AUDIO = {'mp3', 'wav', 'ogg', 'flac', 'm4a'}
    ALLOWED_IMAGE = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    
    # SocketIO
    SOCKETIO_ASYNC_MODE = 'eventlet'
    
    # AI config (Anthropic Claude)
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
    
    # Rate limiting
    RATELIMIT_DEFAULT = "200 per day;50 per hour"
    
    # App settings
    SONGS_PER_PAGE = 20
    APP_NAME = "SoundWave"

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
