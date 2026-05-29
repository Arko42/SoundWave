from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.models.song import Song, Genre, PlayHistory
from app.models.playlist import Playlist
from app.models.user import User
from app import db
from sqlalchemy import func

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    # Trending songs (most played)
    trending = Song.query.filter_by(is_public=True).order_by(Song.play_count.desc()).limit(10).all()
    # Recent songs
    recent_songs = Song.query.filter_by(is_public=True).order_by(Song.created_at.desc()).limit(12).all()
    # Featured playlists
    featured_playlists = Playlist.query.filter_by(is_public=True).order_by(Playlist.created_at.desc()).limit(6).all()
    # Genres
    genres = Genre.query.all()

    # User-specific data
    user_history = []
    user_playlists = []
    if current_user.is_authenticated:
        user_history = PlayHistory.query.filter_by(user_id=current_user.id)\
            .order_by(PlayHistory.played_at.desc()).limit(8).all()
        user_playlists = current_user.playlists.order_by(Playlist.updated_at.desc()).limit(6).all()

    return render_template('index.html',
                           trending=trending,
                           recent_songs=recent_songs,
                           featured_playlists=featured_playlists,
                           genres=genres,
                           user_history=user_history,
                           user_playlists=user_playlists)


@main_bp.route('/discover')
def discover():
    genres = Genre.query.all()
    genre_id = request.args.get('genre')
    page = request.args.get('page', 1, type=int)

    query = Song.query.filter_by(is_public=True)
    if genre_id:
        query = query.filter_by(genre_id=genre_id)

    songs = query.order_by(Song.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('discover.html', songs=songs, genres=genres, selected_genre=genre_id)


@main_bp.route('/search')
def search():
    q = request.args.get('q', '').strip()
    results = []
    artists = []
    playlists = []

    if q:
        results = Song.query.filter(
            db.or_(
                Song.title.ilike(f'%{q}%'),
                Song.artist.ilike(f'%{q}%'),
                Song.album.ilike(f'%{q}%')
            ),
            Song.is_public == True
        ).limit(30).all()

        playlists = Playlist.query.filter(
            Playlist.name.ilike(f'%{q}%'),
            Playlist.is_public == True
        ).limit(6).all()

    return render_template('search.html', q=q, results=results, playlists=playlists)


@main_bp.route('/artist/<string:artist_name>')
def artist(artist_name):
    songs = Song.query.filter_by(artist=artist_name, is_public=True)\
        .order_by(Song.play_count.desc()).all()
    albums = db.session.query(Song.album, func.count(Song.id).label('count'))\
        .filter_by(artist=artist_name)\
        .group_by(Song.album).all()
    return render_template('artist.html', artist_name=artist_name, songs=songs, albums=albums)


@main_bp.route('/album/<string:artist_name>/<string:album_name>')
def album(artist_name, album_name):
    songs = Song.query.filter_by(artist=artist_name, album=album_name, is_public=True)\
        .order_by(Song.id).all()
    return render_template('album.html', artist_name=artist_name, album_name=album_name, songs=songs)
