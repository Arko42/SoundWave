from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import config
import os

# Extensions
db = SQLAlchemy()
login_manager = LoginManager()

# Removed eventlet async_mode
socketio = SocketIO(cors_allowed_origins="*")

limiter = Limiter(key_func=get_remote_address)


def create_app(config_name='default'):
    app = Flask(__name__)

    # Load config
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)
    limiter.init_app(app)

    # Login settings
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # Ensure upload directories exist
    folders = [
        app.config.get('UPLOAD_FOLDER', 'uploads'),
        app.config.get('SONGS_FOLDER', 'uploads/songs'),
        app.config.get('COVERS_FOLDER', 'uploads/covers'),
        app.config.get('AVATARS_FOLDER', 'uploads/avatars'),
    ]

    for folder in folders:
        os.makedirs(folder, exist_ok=True)

    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.player import player_bp
    from app.routes.library import library_bp
    from app.routes.playlist import playlist_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(player_bp, url_prefix='/player')
    app.register_blueprint(library_bp, url_prefix='/library')
    app.register_blueprint(playlist_bp, url_prefix='/playlist')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Create database tables
    with app.app_context():
        db.create_all()
        seed_database()

    return app


def seed_database():
    """Create default users and genres."""
    from app.models.user import User
    from app.models.song import Genre
    from werkzeug.security import generate_password_hash

    # Admin user
    if not User.query.filter_by(email='admin@soundwave.com').first():
        admin = User(
            username='admin',
            email='admin@soundwave.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True,
            bio='SoundWave Platform Administrator'
        )
        db.session.add(admin)

    # Demo user
    if not User.query.filter_by(email='demo@soundwave.com').first():
        demo = User(
            username='demouser',
            email='demo@soundwave.com',
            password_hash=generate_password_hash('demo123'),
            bio='Music enthusiast 🎵'
        )
        db.session.add(demo)

    # Music genres
    genres = [
        'Pop',
        'Rock',
        'Hip-Hop',
        'Electronic',
        'Jazz',
        'Classical',
        'R&B',
        'Country',
        'Metal',
        'Indie'
    ]

    for genre_name in genres:
        if not Genre.query.filter_by(name=genre_name).first():
            db.session.add(Genre(name=genre_name))

    db.session.commit()
