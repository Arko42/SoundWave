import os
import uuid
from werkzeug.utils import secure_filename


ALLOWED_AUDIO = {'mp3', 'wav', 'ogg', 'flac', 'm4a'}
ALLOWED_IMAGE = {'png', 'jpg', 'jpeg', 'webp', 'gif'}


def allowed_audio(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_AUDIO


def allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE


def save_file(file, folder):
    """Save uploaded file with unique name. Returns filename or None."""
    try:
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        file.save(os.path.join(folder, filename))
        return filename
    except Exception as e:
        print(f"Error saving file: {e}")
        return None


def extract_metadata(filepath):
    """Extract metadata from audio file using mutagen."""
    metadata = {
        'title': os.path.basename(filepath).rsplit('.', 1)[0],
        'artist': 'Unknown Artist',
        'album': 'Unknown Album',
        'duration': 0,
        'year': None,
        'bitrate': 0,
        'genre_id': None,
    }

    try:
        from mutagen import File
        from mutagen.mp3 import MP3
        from mutagen.id3 import ID3NoHeaderError

        audio = File(filepath)
        if audio is None:
            return metadata

        # Duration
        if hasattr(audio, 'info') and audio.info:
            metadata['duration'] = int(audio.info.length)
            if hasattr(audio.info, 'bitrate'):
                metadata['bitrate'] = audio.info.bitrate

        # Tags - MP3
        if hasattr(audio, 'tags') and audio.tags:
            tags = audio.tags

            def get_tag(keys):
                for k in keys:
                    val = tags.get(k)
                    if val:
                        return str(val[0]) if hasattr(val, '__iter__') and not isinstance(val, str) else str(val)
                return None

            title = get_tag(['TIT2', '\xa9nam', 'title', 'TITLE'])
            artist = get_tag(['TPE1', '\xa9ART', 'artist', 'ARTIST'])
            album = get_tag(['TALB', '\xa9alb', 'album', 'ALBUM'])
            year = get_tag(['TDRC', '\xa9day', 'date', 'DATE', 'year'])

            if title:
                metadata['title'] = title
            if artist:
                metadata['artist'] = artist
            if album:
                metadata['album'] = album
            if year:
                try:
                    metadata['year'] = int(str(year)[:4])
                except Exception:
                    pass

    except Exception as e:
        print(f"Metadata extraction error: {e}")

    return metadata


def format_duration(seconds):
    """Format seconds to MM:SS string."""
    mins = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{mins}:{secs:02d}"
