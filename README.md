# 🎵 SoundWave — Premium AI-Powered Music Platform

A full-featured, production-grade music streaming platform built with Flask. Inspired by Spotify and Apple Music with a premium dark-glassmorphism UI.

---

## ✨ Features

### 🎵 Music Player
- Play / Pause / Next / Previous
- Shuffle & Repeat modes (none / all / one)
- Volume control & mute
- Seek progress bar with timestamps
- Playback speed control (0.5× → 2×)
- Animated audio visualizer
- Fullscreen player mode
- Queue management panel
- Lyrics panel
- Sleep timer
- Keyboard shortcuts (Space, Arrow keys, N/P/M/S/F)
- Recently played history
- Crossfade-ready architecture

### 🎨 Premium UI
- Dark/Light mode toggle
- Glassmorphism design language
- Animated gradient backgrounds that change with each song
- GSAP-powered entrance animations
- Responsive mobile-first layout
- Toast notification system
- Skeleton loading states
- Smooth panel transitions
- Cover art spinning animation while playing

### 👤 User System
- Register / Login / Logout
- Secure bcrypt password hashing
- User profiles with avatar upload
- Bio and theme preferences
- Listening statistics dashboard

### 📚 Music Library
- Upload MP3, WAV, OGG, FLAC, M4A (up to 50MB)
- Auto metadata extraction (title, artist, album, duration)
- Album cover upload
- Genre categorization
- Lyrics support
- Favorites / Like system
- Recently played history
- Song deletion

### 🎼 Playlists
- Create unlimited playlists
- Add / remove songs
- Public / private playlists
- Drag-and-drop reorder (API-ready)

### 🤖 AI Features (requires Anthropic API key)
- AI music recommendations by mood
- AI chatbot music assistant
- Mood-based playlist suggestions (Happy / Chill / Hype / Sad)
- Smart fallback recommendations without API key

### 👑 Admin Panel
- Platform analytics dashboard
- Interactive Chart.js charts (daily plays, genre distribution)
- Manage all songs (play, delete)
- Manage all users (activate/deactivate)
- Top songs leaderboard
- Recent user signups

### ⚡ Technical
- Flask Blueprints architecture
- SQLite database (zero-config)
- Flask-Login session management
- Flask-SocketIO real-time ready
- REST API endpoints
- Rate limiting
- Audio streaming with range request support
- PWA manifest (installable)

---

## 🚀 Quick Start

### 1. Clone and setup
```bash
cd music_platform
pip install -r requirements.txt
```

### 2. Run the app
```bash
python run.py
```

### 3. Open in browser
```
http://localhost:5000
```

### 4. Demo credentials
| Role  | Email                    | Password  |
|-------|--------------------------|-----------|
| Admin | admin@soundwave.com      | admin123  |
| User  | demo@soundwave.com       | demo123   |

---

## 🤖 Enable AI Features (Optional)

To enable the AI chatbot and smart recommendations, get an Anthropic API key:

1. Visit https://console.anthropic.com
2. Create an API key
3. Set the environment variable:

```bash
# Linux/Mac
export ANTHROPIC_API_KEY=your-key-here

# Windows
set ANTHROPIC_API_KEY=your-key-here
```

Or create a `.env` file:
```
ANTHROPIC_API_KEY=your-key-here
```

The app works fully without an API key — it uses smart fallback recommendations.

---

## 📁 Project Structure

```
music_platform/
├── app/
│   ├── models/
│   │   ├── user.py          # User, auth
│   │   ├── song.py          # Song, Genre, Favorite, PlayHistory
│   │   └── playlist.py      # Playlist, PlaylistSong
│   ├── routes/
│   │   ├── main.py          # Home, Discover, Search, Artist, Album
│   │   ├── auth.py          # Login, Register, Profile
│   │   ├── player.py        # Audio streaming, cover/avatar serving
│   │   ├── library.py       # Upload, Favorites, Delete
│   │   ├── playlist.py      # CRUD playlists
│   │   ├── admin.py         # Admin dashboard
│   │   └── api.py           # REST API + AI endpoints
│   ├── static/
│   │   ├── css/main.css     # Complete premium CSS
│   │   ├── js/player.js     # Full audio player engine
│   │   ├── js/app.js        # UI utilities, AI chat, themes
│   │   └── images/          # Default cover/avatar
│   ├── templates/
│   │   ├── base.html        # Main layout with player
│   │   ├── index.html       # Home page
│   │   ├── discover.html    # Browse music
│   │   ├── search.html      # Search
│   │   ├── library.html     # User library
│   │   ├── upload.html      # Upload music
│   │   ├── favorites.html   # Liked songs
│   │   ├── playlists.html   # Playlist list
│   │   ├── playlist_view.html
│   │   ├── artist.html      # Artist page
│   │   ├── album.html       # Album page
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   ├── register.html
│   │   │   └── profile.html
│   │   └── admin/
│   │       ├── dashboard.html
│   │       ├── songs.html
│   │       └── users.html
│   ├── uploads/             # User uploaded files
│   │   ├── songs/
│   │   ├── covers/
│   │   └── avatars/
│   └── utils/
│       └── helpers.py       # File upload, metadata extraction
├── instance/
│   └── soundwave.db         # SQLite database
├── config.py                # Configuration
├── run.py                   # Entry point
└── requirements.txt
```

---

## 🎹 Keyboard Shortcuts

| Key       | Action            |
|-----------|-------------------|
| `Space`   | Play / Pause      |
| `→`       | Seek +10 seconds  |
| `←`       | Seek -10 seconds  |
| `↑`       | Volume up         |
| `↓`       | Volume down       |
| `N`       | Next song         |
| `P`       | Previous song     |
| `M`       | Mute toggle       |
| `S`       | Shuffle toggle    |
| `F`       | Fullscreen player |

---

## 🔌 REST API

| Method | Endpoint              | Description            |
|--------|-----------------------|------------------------|
| GET    | `/api/songs`          | List songs (paginated) |
| GET    | `/api/songs/<id>`     | Get song details       |
| GET    | `/api/trending`       | Trending songs         |
| GET    | `/api/genres`         | All genres             |
| GET    | `/api/search?q=`      | Search songs/playlists |
| GET    | `/api/user/stats`     | User listening stats   |
| GET    | `/api/user/playlists` | User's playlists       |
| POST   | `/api/ai/recommend`   | AI recommendations     |
| POST   | `/api/ai/chat`        | AI assistant chat      |
| GET    | `/player/stream/<id>` | Stream audio           |
| GET    | `/player/cover/<fn>`  | Serve cover image      |

---

## 🛠️ Tech Stack

| Layer     | Technology                                |
|-----------|-------------------------------------------|
| Backend   | Flask 3.0, Python 3.10+                   |
| Database  | SQLite via Flask-SQLAlchemy               |
| Auth      | Flask-Login                               |
| Realtime  | Flask-SocketIO + Eventlet                 |
| Frontend  | HTML5, Tailwind CSS (CDN), Vanilla JS     |
| Charts    | Chart.js 4                                |
| Animations| GSAP 3                                    |
| Fonts     | Space Grotesk + Syne (Google Fonts)       |
| Icons     | Font Awesome 6                            |
| AI        | Anthropic Claude API (optional)           |
| Metadata  | Mutagen                                   |
| Images    | Pillow                                    |

---

## 📄 License

MIT — Use freely for personal and commercial projects.
