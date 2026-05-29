from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import config
import os

db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO()
limiter = Limiter(key_func=get_remote_address)

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*", async_mode='eventlet')
    limiter.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # Ensure upload directories exist
    for folder in [
        app.config['UPLOAD_FOLDER'],
        app.config['SONGS_FOLDER'],
        app.config['COVERS_FOLDER'],
        app.config['AVATARS_FOLDER'],
    ]:
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

    # Create tables and seed data
    with app.app_context():
        db.create_all()
        seed_database()

    return app


def seed_database():
    """Create default admin user and sample data if not exists."""
    from app.models.user import User
    from app.models.song import Song, Genre
    from werkzeug.security import generate_password_hash

    # Create admin user
    if not User.query.filter_by(email='admin@soundwave.com').first():
        admin = User(
            username='admin',
            email='admin@soundwave.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True,
            bio='SoundWave Platform Administrator'
        )
        db.session.add(admin)

    # Create demo user
    if not User.query.filter_by(email='demo@soundwave.com').first():
        demo = User(
            username='demouser',
            email='demo@soundwave.com',
            password_hash=generate_password_hash('demo123'),
            bio='Music enthusiast 🎵'
        )
        db.session.add(demo)

    # Create genres
    genres = ['Pop', 'Rock', 'Hip-Hop', 'Electronic', 'Jazz', 'Classical', 'R&B', 'Country', 'Metal', 'Indie']
    for g in genres:
        if not Genre.query.filter_by(name=g).first():
            db.session.add(Genre(name=g))

    db.session.commit()
