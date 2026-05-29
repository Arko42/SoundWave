from flask import Blueprint, send_file, abort, request, jsonify, current_app
from flask_login import current_user
from app.models.song import Song, PlayHistory
from app import db
import os

player_bp = Blueprint('player', __name__)


@player_bp.route('/stream/<int:song_id>')
def stream(song_id):
    """Stream audio file with range support."""
    song = Song.query.get_or_404(song_id)

    songs_folder = current_app.config['SONGS_FOLDER']
    file_path = os.path.join(songs_folder, song.file_path)

    if not os.path.exists(file_path):
        abort(404)

    # Update play count
    song.play_count += 1
    db.session.commit()

    # Record play history if user is logged in
    if current_user.is_authenticated:
        history = PlayHistory(user_id=current_user.id, song_id=song_id)
        db.session.add(history)
        db.session.commit()

    return send_file(file_path, mimetype='audio/mpeg', conditional=True)


@player_bp.route('/cover/<string:filename>')
def cover(filename):
    """Serve album cover images."""
    covers_folder = current_app.config['COVERS_FOLDER']
    file_path = os.path.join(covers_folder, filename)

    if os.path.exists(file_path):
        return send_file(file_path)

    # Return default cover
    default = os.path.join(current_app.static_folder, 'images', 'default_cover.jpg')
    if os.path.exists(default):
        return send_file(default)
    abort(404)


@player_bp.route('/avatar/<string:filename>')
def avatar(filename):
    """Serve user avatar images."""
    avatars_folder = current_app.config['AVATARS_FOLDER']
    file_path = os.path.join(avatars_folder, filename)

    if os.path.exists(file_path):
        return send_file(file_path)

    default = os.path.join(current_app.static_folder, 'images', 'default_avatar.png')
    if os.path.exists(default):
        return send_file(default)
    abort(404)
