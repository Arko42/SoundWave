from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models.user import User
from app.models.song import Song, Genre, PlayHistory
from app.models.playlist import Playlist
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    stats = {
        'total_users': User.query.count(),
        'total_songs': Song.query.count(),
        'total_playlists': Playlist.query.count(),
        'total_plays': PlayHistory.query.count(),
    }

    # Top songs
    top_songs = Song.query.order_by(Song.play_count.desc()).limit(10).all()

    # Recent users
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()

    # Genre distribution
    genre_stats = db.session.query(
        Genre.name, func.count(Song.id).label('count')
    ).join(Song, Song.genre_id == Genre.id)\
     .group_by(Genre.name).all()

    # Daily plays (last 7 days)
    from datetime import datetime, timedelta
    from sqlalchemy import cast, Date
    daily_plays = []
    for i in range(7):
        day = datetime.utcnow().date() - timedelta(days=i)
        count = PlayHistory.query.filter(
            func.date(PlayHistory.played_at) == day
        ).count()
        daily_plays.append({'date': str(day), 'plays': count})
    daily_plays.reverse()

    return render_template('admin/dashboard.html',
                           stats=stats,
                           top_songs=top_songs,
                           recent_users=recent_users,
                           genre_stats=genre_stats,
                           daily_plays=daily_plays)


@admin_bp.route('/songs')
@login_required
@admin_required
def songs():
    page = request.args.get('page', 1, type=int)
    songs = Song.query.order_by(Song.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('admin/songs.html', songs=songs)


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)


@admin_bp.route('/users/<int:user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': 'Cannot deactivate yourself'})
    user.is_active = not user.is_active
    db.session.commit()
    return jsonify({'success': True, 'active': user.is_active})


@admin_bp.route('/songs/<int:song_id>/delete', methods=['DELETE'])
@login_required
@admin_required
def delete_song(song_id):
    song = Song.query.get_or_404(song_id)
    import os
    from flask import current_app
    try:
        path = os.path.join(current_app.config['SONGS_FOLDER'], song.file_path)
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass
    db.session.delete(song)
    db.session.commit()
    return jsonify({'success': True})
