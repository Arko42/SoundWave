from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models.song import Song, Genre, PlayHistory
from app.models.playlist import Playlist
from app.models.user import User
from app import db
from sqlalchemy import func
import os

api_bp = Blueprint('api', __name__)


@api_bp.route('/songs')
def songs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    genre_id = request.args.get('genre_id')
    search = request.args.get('q', '')

    query = Song.query.filter_by(is_public=True)
    if genre_id:
        query = query.filter_by(genre_id=genre_id)
    if search:
        query = query.filter(
            db.or_(Song.title.ilike(f'%{search}%'), Song.artist.ilike(f'%{search}%'))
        )

    paginated = query.order_by(Song.created_at.desc()).paginate(page=page, per_page=per_page)
    return jsonify({
        'songs': [s.to_dict() for s in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'page': paginated.page
    })


@api_bp.route('/songs/<int:song_id>')
def song(song_id):
    s = Song.query.get_or_404(song_id)
    data = s.to_dict()
    if current_user.is_authenticated:
        data['is_favorite'] = current_user.is_favorite(song_id)
    return jsonify(data)


@api_bp.route('/trending')
def trending():
    songs = Song.query.filter_by(is_public=True).order_by(Song.play_count.desc()).limit(20).all()
    return jsonify([s.to_dict() for s in songs])


@api_bp.route('/genres')
def genres():
    genres = Genre.query.all()
    return jsonify([g.to_dict() for g in genres])


@api_bp.route('/search')
def search():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({'songs': [], 'playlists': []})

    songs = Song.query.filter(
        db.or_(
            Song.title.ilike(f'%{q}%'),
            Song.artist.ilike(f'%{q}%'),
            Song.album.ilike(f'%{q}%')
        ),
        Song.is_public == True
    ).limit(10).all()

    playlists = Playlist.query.filter(
        Playlist.name.ilike(f'%{q}%'),
        Playlist.is_public == True
    ).limit(5).all()

    return jsonify({
        'songs': [s.to_dict() for s in songs],
        'playlists': [p.to_dict() for p in playlists]
    })


@api_bp.route('/user/stats')
@login_required
def user_stats():
    total_plays = PlayHistory.query.filter_by(user_id=current_user.id).count()
    favorites_count = current_user.favorites.count()
    playlists_count = current_user.playlists.count()

    # Top genres
    top_genres = db.session.query(
        Genre.name, func.count(PlayHistory.id).label('plays')
    ).join(Song, Song.genre_id == Genre.id)\
     .join(PlayHistory, PlayHistory.song_id == Song.id)\
     .filter(PlayHistory.user_id == current_user.id)\
     .group_by(Genre.name)\
     .order_by(db.desc('plays'))\
     .limit(5).all()

    return jsonify({
        'total_plays': total_plays,
        'favorites': favorites_count,
        'playlists': playlists_count,
        'top_genres': [{'name': g[0], 'plays': g[1]} for g in top_genres]
    })


@api_bp.route('/user/playlists')
@login_required
def user_playlists():
    playlists = current_user.playlists.order_by(Playlist.updated_at.desc()).all()
    return jsonify([p.to_dict() for p in playlists])


@api_bp.route('/ai/recommend', methods=['POST'])
@login_required
def ai_recommend():
    """AI-powered song recommendations using Anthropic Claude."""
    from flask import current_app
    import anthropic

    mood = request.json.get('mood', 'happy')
    genre_pref = request.json.get('genre', 'any')

    # Get available songs
    songs = Song.query.filter_by(is_public=True).all()
    song_list = [f"{s.title} by {s.artist} ({s.genre_ref.name if s.genre_ref else 'Unknown'})" for s in songs[:50]]

    api_key = current_app.config.get('ANTHROPIC_API_KEY', '')
    if not api_key:
        # Return smart fallback recommendations
        recommended = Song.query.filter_by(is_public=True).order_by(Song.play_count.desc()).limit(5).all()
        return jsonify({
            'recommendations': [s.to_dict() for s in recommended],
            'message': f"Top tracks for a {mood} mood",
            'ai': False
        })

    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": f"""Given these available songs: {', '.join(song_list[:20])}\n
                Recommend 5 songs for a {mood} mood (genre preference: {genre_pref}).
                Return ONLY a JSON array of song titles like: ["title1", "title2"]"""
            }]
        )

        import json, re
        text = response.content[0].text
        match = re.search(r'\[.*?\]', text, re.DOTALL)
        if match:
            titles = json.loads(match.group())
            recommended = []
            for title in titles:
                song = Song.query.filter(Song.title.ilike(f'%{title}%')).first()
                if song:
                    recommended.append(song.to_dict())

            return jsonify({
                'recommendations': recommended,
                'message': f"AI curated {mood} playlist",
                'ai': True
            })
    except Exception as e:
        pass

    # Fallback
    recommended = Song.query.filter_by(is_public=True).order_by(Song.play_count.desc()).limit(5).all()
    return jsonify({
        'recommendations': [s.to_dict() for s in recommended],
        'message': f"Recommended for {mood} mood",
        'ai': False
    })


@api_bp.route('/ai/chat', methods=['POST'])
@login_required
def ai_chat():
    """AI chatbot assistant for music suggestions."""
    from flask import current_app

    message = request.json.get('message', '').strip()
    if not message:
        return jsonify({'response': 'Please ask me something about music!'}), 400

    api_key = current_app.config.get('ANTHROPIC_API_KEY', '')

    if not api_key:
        # Smart fallback responses
        responses = {
            'recommend': 'Try our trending section for popular tracks! You can also filter by genre in the Discover page.',
            'playlist': 'Create a playlist from your Library section and add songs you love!',
            'upload': 'Go to Library → Upload to add your own music collection.',
            'default': f'I heard "{message}" - explore our Discover page to find great music! 🎵'
        }
        key = next((k for k in responses if k in message.lower()), 'default')
        return jsonify({'response': responses[key]})

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        songs_sample = Song.query.filter_by(is_public=True).order_by(Song.play_count.desc()).limit(20).all()
        song_context = ', '.join([f"{s.title} by {s.artist}" for s in songs_sample])

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            system=f"""You are SoundWave's AI music assistant. Be friendly, concise, and helpful.
            Available songs on platform: {song_context}
            Help users find music, suggest songs, and navigate the platform.""",
            messages=[{"role": "user", "content": message}]
        )
        return jsonify({'response': response.content[0].text})
    except Exception as e:
        return jsonify({'response': 'Our AI is taking a break. Try browsing the Discover page! 🎵'})
