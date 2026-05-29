from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.song import Song, Genre, Favorite
from app.models.user import User
from app.utils.helpers import allowed_audio, allowed_image, save_file, extract_metadata
import os

library_bp = Blueprint('library', __name__)


@library_bp.route('/')
@login_required
def index():
    songs = Song.query.filter_by(uploaded_by=current_user.id).order_by(Song.created_at.desc()).all()
    genres = Genre.query.all()
    return render_template('library.html', songs=songs, genres=genres)


@library_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    genres = Genre.query.all()

    if request.method == 'POST':
        if 'audio' not in request.files:
            return jsonify({'success': False, 'message': 'No audio file provided'}), 400

        audio_file = request.files['audio']
        if not audio_file.filename:
            return jsonify({'success': False, 'message': 'No file selected'}), 400

        if not allowed_audio(audio_file.filename):
            return jsonify({'success': False, 'message': 'Invalid audio format. Use MP3, WAV, OGG, FLAC, or M4A'}), 400

        # Save audio file
        songs_folder = current_app.config['SONGS_FOLDER']
        audio_filename = save_file(audio_file, songs_folder)
        if not audio_filename:
            return jsonify({'success': False, 'message': 'Error saving audio file'}), 500

        # Extract metadata
        audio_path = os.path.join(songs_folder, audio_filename)
        metadata = extract_metadata(audio_path)

        # Save cover if provided
        cover_filename = 'default_cover.jpg'
        if 'cover' in request.files:
            cover_file = request.files['cover']
            if cover_file.filename and allowed_image(cover_file.filename):
                covers_folder = current_app.config['COVERS_FOLDER']
                saved_cover = save_file(cover_file, covers_folder)
                if saved_cover:
                    cover_filename = saved_cover

        # Create song record
        genre_id = request.form.get('genre_id') or metadata.get('genre_id')
        song = Song(
            title=request.form.get('title') or metadata.get('title', audio_file.filename),
            artist=request.form.get('artist') or metadata.get('artist', 'Unknown Artist'),
            album=request.form.get('album') or metadata.get('album', 'Unknown Album'),
            genre_id=genre_id if genre_id else None,
            duration=metadata.get('duration', 0),
            file_path=audio_filename,
            cover_path=cover_filename,
            lyrics=request.form.get('lyrics', ''),
            year=metadata.get('year'),
            bitrate=metadata.get('bitrate', 0),
            file_size=os.path.getsize(audio_path),
            uploaded_by=current_user.id,
        )
        db.session.add(song)
        db.session.commit()

        return jsonify({'success': True, 'song': song.to_dict()})

    return render_template('upload.html', genres=genres)


@library_bp.route('/favorites')
@login_required
def favorites():
    fav_songs = [f.song for f in current_user.favorites.order_by(Favorite.created_at.desc()).all() if f.song]
    return render_template('favorites.html', songs=fav_songs)


@library_bp.route('/toggle-favorite/<int:song_id>', methods=['POST'])
@login_required
def toggle_favorite(song_id):
    song = Song.query.get_or_404(song_id)
    existing = Favorite.query.filter_by(user_id=current_user.id, song_id=song_id).first()

    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'success': True, 'favorited': False})
    else:
        fav = Favorite(user_id=current_user.id, song_id=song_id)
        db.session.add(fav)
        db.session.commit()
        return jsonify({'success': True, 'favorited': True})


@library_bp.route('/delete/<int:song_id>', methods=['DELETE'])
@login_required
def delete_song(song_id):
    song = Song.query.get_or_404(song_id)
    if song.uploaded_by != current_user.id and not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    # Delete files
    try:
        songs_folder = current_app.config['SONGS_FOLDER']
        audio_path = os.path.join(songs_folder, song.file_path)
        if os.path.exists(audio_path):
            os.remove(audio_path)
    except Exception:
        pass

    db.session.delete(song)
    db.session.commit()
    return jsonify({'success': True})
