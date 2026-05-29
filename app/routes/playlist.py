from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.playlist import Playlist, PlaylistSong
from app.models.song import Song

playlist_bp = Blueprint('playlist', __name__)


@playlist_bp.route('/')
@login_required
def index():
    playlists = current_user.playlists.order_by(Playlist.updated_at.desc()).all()
    return render_template('playlists.html', playlists=playlists)


@playlist_bp.route('/create', methods=['POST'])
@login_required
def create():
    data = request.get_json() or request.form
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'success': False, 'message': 'Playlist name required'}), 400

    playlist = Playlist(
        name=name,
        description=data.get('description', ''),
        user_id=current_user.id,
        is_public=bool(data.get('is_public', True))
    )
    db.session.add(playlist)
    db.session.commit()
    return jsonify({'success': True, 'playlist': playlist.to_dict()})


@playlist_bp.route('/<int:playlist_id>')
def view(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    if not playlist.is_public and (not current_user.is_authenticated or current_user.id != playlist.user_id):
        flash('This playlist is private', 'error')
        return redirect(url_for('main.index'))
    songs = playlist.songs
    return render_template('playlist_view.html', playlist=playlist, songs=songs)


@playlist_bp.route('/<int:playlist_id>/add-song', methods=['POST'])
@login_required
def add_song(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    if playlist.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    song_id = request.json.get('song_id')
    if not Song.query.get(song_id):
        return jsonify({'success': False, 'message': 'Song not found'}), 404

    existing = PlaylistSong.query.filter_by(playlist_id=playlist_id, song_id=song_id).first()
    if existing:
        return jsonify({'success': False, 'message': 'Song already in playlist'})

    max_pos = db.session.query(db.func.max(PlaylistSong.position))\
        .filter_by(playlist_id=playlist_id).scalar() or 0

    ps = PlaylistSong(playlist_id=playlist_id, song_id=song_id, position=max_pos + 1)
    db.session.add(ps)
    db.session.commit()
    return jsonify({'success': True})


@playlist_bp.route('/<int:playlist_id>/remove-song', methods=['POST'])
@login_required
def remove_song(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    if playlist.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    song_id = request.json.get('song_id')
    ps = PlaylistSong.query.filter_by(playlist_id=playlist_id, song_id=song_id).first()
    if ps:
        db.session.delete(ps)
        db.session.commit()
    return jsonify({'success': True})


@playlist_bp.route('/<int:playlist_id>/reorder', methods=['POST'])
@login_required
def reorder(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    if playlist.user_id != current_user.id:
        return jsonify({'success': False}), 403

    order = request.json.get('order', [])  # list of song_ids
    for i, song_id in enumerate(order):
        ps = PlaylistSong.query.filter_by(playlist_id=playlist_id, song_id=song_id).first()
        if ps:
            ps.position = i
    db.session.commit()
    return jsonify({'success': True})


@playlist_bp.route('/<int:playlist_id>/delete', methods=['DELETE'])
@login_required
def delete(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    if playlist.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    db.session.delete(playlist)
    db.session.commit()
    return jsonify({'success': True})
