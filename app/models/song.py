from app import db
from datetime import datetime


class Genre(db.Model):
    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    songs = db.relationship('Song', backref='genre_ref', lazy='dynamic')

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'count': self.songs.count()}


class Song(db.Model):
    __tablename__ = 'songs'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(200), nullable=False, default='Unknown Artist')
    album = db.Column(db.String(200), default='Unknown Album')
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'), nullable=True)
    duration = db.Column(db.Integer, default=0)  # seconds
    file_path = db.Column(db.String(500), nullable=False)
    cover_path = db.Column(db.String(500), default='default_cover.jpg')
    lyrics = db.Column(db.Text, default='')
    play_count = db.Column(db.Integer, default=0)
    year = db.Column(db.Integer, nullable=True)
    bitrate = db.Column(db.Integer, default=0)
    file_size = db.Column(db.Integer, default=0)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    favorites = db.relationship('Favorite', backref='song', lazy='dynamic', cascade='all, delete-orphan')
    history_entries = db.relationship('PlayHistory', backref='song', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def duration_formatted(self):
        mins = self.duration // 60
        secs = self.duration % 60
        return f"{mins}:{secs:02d}"

    @property
    def file_size_mb(self):
        return round(self.file_size / (1024 * 1024), 2)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'artist': self.artist,
            'album': self.album,
            'genre': self.genre_ref.name if self.genre_ref else 'Unknown',
            'genre_id': self.genre_id,
            'duration': self.duration,
            'duration_formatted': self.duration_formatted,
            'file_path': self.file_path,
            'cover_path': self.cover_path,
            'play_count': self.play_count,
            'year': self.year,
            'lyrics': self.lyrics,
            'created_at': self.created_at.isoformat(),
        }

    def __repr__(self):
        return f'<Song {self.title} by {self.artist}>'


class Favorite(db.Model):
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'song_id'),)


class PlayHistory(db.Model):
    __tablename__ = 'play_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
    played_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'song': self.song.to_dict() if self.song else None,
            'played_at': self.played_at.isoformat()
        }
