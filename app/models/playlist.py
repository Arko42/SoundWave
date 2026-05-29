from app import db
from datetime import datetime


class Playlist(db.Model):
    __tablename__ = 'playlists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), default='')
    cover_path = db.Column(db.String(500), default='default_playlist.jpg')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Many-to-many with songs via PlaylistSong
    playlist_songs = db.relationship(
        'PlaylistSong',
        backref='playlist',
        lazy='dynamic',
        cascade='all, delete-orphan',
        order_by='PlaylistSong.position'
    )

    @property
    def songs(self):
        from app.models.song import Song
        return [ps.song for ps in self.playlist_songs.order_by(PlaylistSong.position).all() if ps.song]

    @property
    def song_count(self):
        return self.playlist_songs.count()

    @property
    def total_duration(self):
        total = sum(ps.song.duration for ps in self.playlist_songs.all() if ps.song)
        mins = total // 60
        return f"{mins} min"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'cover_path': self.cover_path,
            'user_id': self.user_id,
            'owner': self.owner.username if self.owner else 'Unknown',
            'is_public': self.is_public,
            'song_count': self.song_count,
            'total_duration': self.total_duration,
            'created_at': self.created_at.isoformat(),
        }

    def __repr__(self):
        return f'<Playlist {self.name}>'


class PlaylistSong(db.Model):
    __tablename__ = 'playlist_songs'

    id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlists.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
    position = db.Column(db.Integer, default=0)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    song = db.relationship('Song', backref='playlist_entries')

    __table_args__ = (db.UniqueConstraint('playlist_id', 'song_id'),)
