from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    avatar = db.Column(db.String(256), default='default_avatar.png')
    bio = db.Column(db.String(500), default='')
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    theme = db.Column(db.String(10), default='dark')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    playlists = db.relationship('Playlist', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    history = db.relationship('PlayHistory', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    uploaded_songs = db.relationship('Song', backref='uploader', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_favorite(self, song_id):
        return self.favorites.filter_by(song_id=song_id).first() is not None

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'avatar': self.avatar,
            'bio': self.bio,
            'is_admin': self.is_admin,
            'theme': self.theme,
            'created_at': self.created_at.isoformat(),
            'playlist_count': self.playlists.count(),
            'favorite_count': self.favorites.count(),
        }

    def __repr__(self):
        return f'<User {self.username}>'
