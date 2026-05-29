/**
 * SoundWave Music Player Engine
 * Full-featured audio player with queue, shuffle, repeat, visualizer
 */

// ===== STATE =====
let currentSong = null;
let queue = [];
let originalQueue = [];
let currentIndex = -1;
let isPlaying = false;
let isShuffle = false;
let repeatMode = 'none'; // 'none', 'all', 'one'
let isMuted = false;
let prevVolume = 80;
let sleepTimer = null;
let addToPlaylistSongId = null;

const audio = document.getElementById('audioElement');

// ===== PLAY A SONG =====
function playSong(songData, songList) {
  if (!songData) return;

  currentSong = songData;

  if (songList && songList.length > 0) {
    originalQueue = [...songList];
    queue = isShuffle ? shuffleArray([...songList]) : [...songList];
    currentIndex = queue.findIndex(s => s.id === songData.id);
    if (currentIndex === -1) { queue.unshift(songData); currentIndex = 0; }
  } else if (queue.length === 0) {
    queue = [songData];
    originalQueue = [songData];
    currentIndex = 0;
  } else {
    currentIndex = queue.findIndex(s => s.id === songData.id);
    if (currentIndex === -1) currentIndex = 0;
  }

  loadAndPlay(songData);
  updatePlayerUI(songData);
  updateQueueUI();
  updateAmbientColor(songData.cover_path);
  saveLastPlayed(songData.id);
}

function loadAndPlay(song) {
  const streamUrl = `/player/stream/${song.id}`;
  if (audio.src !== streamUrl) {
    audio.src = streamUrl;
  }
  audio.play().then(() => {
    setPlayingState(true);
  }).catch(err => {
    console.error('Play error:', err);
    showToast('Could not play this track', 'error');
  });
}

// ===== PLAYER CONTROLS =====
function togglePlayPause() {
  if (!currentSong) return;
  if (isPlaying) {
    audio.pause();
    setPlayingState(false);
  } else {
    audio.play();
    setPlayingState(true);
  }
}

function nextSong() {
  if (queue.length === 0) return;
  if (repeatMode === 'one') { audio.currentTime = 0; audio.play(); return; }
  currentIndex = (currentIndex + 1) % queue.length;
  if (currentIndex === 0 && repeatMode === 'none') { audio.pause(); setPlayingState(false); return; }
  playSong(queue[currentIndex]);
}

function prevSong() {
  if (audio.currentTime > 3) { audio.currentTime = 0; return; }
  if (queue.length === 0) return;
  currentIndex = (currentIndex - 1 + queue.length) % queue.length;
  playSong(queue[currentIndex]);
}

function toggleShuffle() {
  isShuffle = !isShuffle;
  document.getElementById('shuffleBtn').classList.toggle('active', isShuffle);
  if (isShuffle) {
    queue = shuffleArray([...originalQueue]);
    currentIndex = queue.findIndex(s => s.id === currentSong?.id);
  } else {
    queue = [...originalQueue];
    currentIndex = queue.findIndex(s => s.id === currentSong?.id);
  }
  updateQueueUI();
  showToast(isShuffle ? 'Shuffle on' : 'Shuffle off', 'info');
}

function toggleRepeat() {
  const modes = ['none', 'all', 'one'];
  const icons = ['fa-redo', 'fa-redo', 'fa-redo'];
  repeatMode = modes[(modes.indexOf(repeatMode) + 1) % modes.length];
  const btn = document.getElementById('repeatBtn');
  btn.classList.toggle('active', repeatMode !== 'none');
  const labels = { none: 'Repeat off', all: 'Repeat all', one: 'Repeat one' };
  showToast(labels[repeatMode], 'info');
}

function toggleMute() {
  isMuted = !isMuted;
  audio.muted = isMuted;
  const icon = document.getElementById('volumeIcon');
  icon.className = isMuted ? 'fas fa-volume-mute' : 'fas fa-volume-up';
  document.getElementById('muteBtn').classList.toggle('active', isMuted);
}

function changeSpeed(speed) {
  audio.playbackRate = parseFloat(speed);
}

// ===== PROGRESS & TIME =====
audio.addEventListener('timeupdate', () => {
  if (!audio.duration) return;
  const pct = (audio.currentTime / audio.duration) * 100;

  // Update progress bars
  document.getElementById('progressFill').style.width = pct + '%';
  document.getElementById('progressThumb').style.left = pct + '%';
  document.getElementById('fsProgressFill').style.width = pct + '%';

  // Update time displays
  const cur = formatTime(audio.currentTime);
  const tot = formatTime(audio.duration);
  document.getElementById('currentTime').textContent = cur;
  document.getElementById('totalTime').textContent = tot;
  document.getElementById('fsCurrentTime').textContent = cur;
  document.getElementById('fsTotalTime').textContent = tot;
});

audio.addEventListener('ended', () => {
  if (repeatMode === 'one') { audio.currentTime = 0; audio.play(); return; }
  if (currentIndex < queue.length - 1 || repeatMode === 'all') {
    nextSong();
  } else {
    setPlayingState(false);
  }
});

audio.addEventListener('loadedmetadata', () => {
  document.getElementById('totalTime').textContent = formatTime(audio.duration);
  document.getElementById('fsTotalTime').textContent = formatTime(audio.duration);
});

// Seek on progress click
document.getElementById('progressBarFull').addEventListener('click', (e) => {
  const rect = e.currentTarget.getBoundingClientRect();
  const pct = (e.clientX - rect.left) / rect.width;
  audio.currentTime = pct * audio.duration;
});

document.getElementById('fsProgressBar').addEventListener('click', (e) => {
  const rect = e.currentTarget.getBoundingClientRect();
  const pct = (e.clientX - rect.left) / rect.width;
  audio.currentTime = pct * audio.duration;
});

// Volume control
document.getElementById('volumeSlider').addEventListener('input', (e) => {
  const vol = e.target.value / 100;
  audio.volume = vol;
  const icon = document.getElementById('volumeIcon');
  if (vol === 0) icon.className = 'fas fa-volume-mute';
  else if (vol < 0.5) icon.className = 'fas fa-volume-down';
  else icon.className = 'fas fa-volume-up';
  isMuted = vol === 0;
});

// ===== UI UPDATES =====
function setPlayingState(playing) {
  isPlaying = playing;
  const playIcon = document.getElementById('playIcon');
  const fsPlayIcon = document.getElementById('fsPlayIcon');
  const vis = document.getElementById('visualizer');

  if (playing) {
    playIcon.className = 'fas fa-pause';
    fsPlayIcon.className = 'fas fa-pause';
    vis.classList.add('playing');
    document.getElementById('nowPlayingCover').classList.add('spinning');
  } else {
    playIcon.className = 'fas fa-play';
    fsPlayIcon.className = 'fas fa-play';
    vis.classList.remove('playing');
    document.getElementById('nowPlayingCover').classList.remove('spinning');
  }

  // Highlight current card in page
  document.querySelectorAll('.song-card').forEach(c => {
    const matches = c.dataset.songId == currentSong?.id;
    c.classList.toggle('playing', matches && playing);
  });
  document.querySelectorAll('.trending-item').forEach(c => {
    c.classList.toggle('playing', c.dataset.songId == currentSong?.id && playing);
  });
}

function updatePlayerUI(song) {
  document.getElementById('playerSongTitle').textContent = song.title;
  document.getElementById('playerSongArtist').textContent = song.artist;
  document.getElementById('fsSongTitle').textContent = song.title;
  document.getElementById('fsSongArtist').textContent = song.artist;

  const coverUrl = song.cover_path === 'default_cover.jpg'
    ? '/static/images/default_cover.jpg'
    : `/player/cover/${song.cover_path}`;

  document.getElementById('playerCoverImg').src = coverUrl;
  document.getElementById('fsCoverImg').src = coverUrl;

  // Update favorite button
  const favBtn = document.getElementById('playerFavBtn');
  if (song.is_favorite) favBtn.classList.add('favorited');
  else favBtn.classList.remove('favorited');

  // Update page title
  document.title = `${song.title} — ${song.artist} | SoundWave`;

  // Update lyrics
  updateLyrics(song.lyrics || '');
}

function updateAmbientColor(coverPath) {
  // Change ambient gradient based on song (simple hue rotation)
  const hues = [260, 300, 200, 30, 150, 0, 180];
  const hue = hues[Math.floor(Math.random() * hues.length)];
  document.getElementById('ambientBg').style.background =
    `radial-gradient(ellipse 60% 60% at 20% 20%, hsla(${hue}, 70%, 40%, 0.1) 0%, transparent 70%),
     radial-gradient(ellipse 50% 50% at 80% 80%, hsla(${(hue + 120) % 360}, 60%, 40%, 0.07) 0%, transparent 70%)`;
}

function updateQueueUI() {
  const list = document.getElementById('queueList');
  if (!list) return;
  list.innerHTML = queue.map((song, i) => `
    <div class="queue-item ${i === currentIndex ? 'current' : ''}" onclick="playSongFromQueue(${i})">
      <img src="${song.cover_path === 'default_cover.jpg' ? '/static/images/default_cover.jpg' : '/player/cover/' + song.cover_path}"
           alt="${song.title}" onerror="this.src='/static/images/default_cover.jpg'">
      <div class="queue-item-info">
        <div class="queue-item-title">${escapeHtml(song.title)}</div>
        <div class="queue-item-artist">${escapeHtml(song.artist)}</div>
      </div>
      <span class="queue-item-dur">${song.duration_formatted || formatTime(song.duration)}</span>
    </div>
  `).join('');
}

function playSongFromQueue(index) {
  currentIndex = index;
  playSong(queue[index]);
}

function updateLyrics(lyrics) {
  const el = document.getElementById('lyricsContent');
  if (lyrics && lyrics.trim()) {
    el.innerHTML = `<div class="lyrics-text">${escapeHtml(lyrics)}</div>`;
  } else {
    el.innerHTML = '<p class="lyrics-placeholder">No lyrics available for this track</p>';
  }
}

// ===== PANEL TOGGLES =====
function toggleQueue() {
  const panel = document.getElementById('queuePanel');
  const lyricsPanel = document.getElementById('lyricsPanel');
  lyricsPanel.classList.remove('open');
  panel.classList.toggle('open');
}

function toggleLyrics() {
  const panel = document.getElementById('lyricsPanel');
  const queuePanel = document.getElementById('queuePanel');
  queuePanel.classList.remove('open');
  panel.classList.toggle('open');
}

function toggleFullscreen() {
  const fs = document.getElementById('fullscreenPlayer');
  fs.classList.toggle('open');
}

// ===== FAVORITE =====
async function toggleFavorite(songId) {
  if (!songId) return;
  try {
    const res = await fetch(`/library/toggle-favorite/${songId}`, { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      const btn = document.getElementById('playerFavBtn');
      btn.classList.toggle('favorited', data.favorited);
      if (currentSong && currentSong.id === songId) {
        currentSong.is_favorite = data.favorited;
      }
      // Update page song card hearts
      document.querySelectorAll(`[data-fav-btn="${songId}"]`).forEach(b => {
        b.classList.toggle('active', data.favorited);
      });
      showToast(data.favorited ? 'Added to favorites' : 'Removed from favorites', 'success');
    }
  } catch (e) {
    showToast('Please sign in to use favorites', 'error');
  }
}

// ===== ADD TO PLAYLIST MODAL =====
async function toggleAddToPlaylist(songId) {
  addToPlaylistSongId = songId || currentSong?.id;
  if (!addToPlaylistSongId) return;

  const modal = document.getElementById('playlistModal');
  modal.classList.add('open');

  // Load user playlists
  const res = await fetch('/api/user/playlists');
  if (res.ok) {
    const playlists = await res.json();
    const list = document.getElementById('playlistModalList');
    list.innerHTML = playlists.map(pl => `
      <div class="playlist-modal-item" onclick="addSongToPlaylist(${pl.id})">
        <i class="fas fa-music"></i>
        <span>${escapeHtml(pl.name)}</span>
        <small style="color:var(--text-muted);margin-left:auto">${pl.song_count} songs</small>
      </div>
    `).join('') || '<p style="color:var(--text-muted);text-align:center;padding:20px">No playlists yet</p>';
  }
}

function closePlaylistModal() {
  document.getElementById('playlistModal').classList.remove('open');
  addToPlaylistSongId = null;
}

async function addSongToPlaylist(playlistId) {
  if (!addToPlaylistSongId) return;
  const res = await fetch(`/playlist/${playlistId}/add-song`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ song_id: addToPlaylistSongId })
  });
  const data = await res.json();
  showToast(data.success ? 'Added to playlist!' : data.message, data.success ? 'success' : 'error');
  closePlaylistModal();
}

async function createPlaylistFromModal() {
  const name = document.getElementById('newPlaylistName').value.trim();
  if (!name) return;

  const res = await fetch('/playlist/create', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name })
  });
  const data = await res.json();
  if (data.success) {
    await addSongToPlaylist(data.playlist.id);
  }
}

// ===== SLEEP TIMER =====
function setSleepTimer(minutes) {
  clearTimeout(sleepTimer);
  const status = document.getElementById('sleepTimerStatus');
  if (minutes === 0) {
    status.textContent = 'Sleep timer off';
    return;
  }
  sleepTimer = setTimeout(() => {
    audio.pause();
    setPlayingState(false);
    showToast('Sleep timer: music paused', 'info');
  }, minutes * 60000);
  status.textContent = `Music will stop in ${minutes} minute${minutes > 1 ? 's' : ''}`;
  showToast(`Sleep timer set for ${minutes} min`, 'success');
}

function closeSleepModal() {
  document.getElementById('sleepModal').classList.remove('open');
}

// ===== KEYBOARD SHORTCUTS =====
document.addEventListener('keydown', (e) => {
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

  switch(e.code) {
    case 'Space': e.preventDefault(); togglePlayPause(); break;
    case 'ArrowRight': audio.currentTime = Math.min(audio.currentTime + 10, audio.duration); break;
    case 'ArrowLeft': audio.currentTime = Math.max(audio.currentTime - 10, 0); break;
    case 'ArrowUp': e.preventDefault(); audio.volume = Math.min(audio.volume + 0.1, 1); document.getElementById('volumeSlider').value = audio.volume * 100; break;
    case 'ArrowDown': e.preventDefault(); audio.volume = Math.max(audio.volume - 0.1, 0); document.getElementById('volumeSlider').value = audio.volume * 100; break;
    case 'KeyN': nextSong(); break;
    case 'KeyP': prevSong(); break;
    case 'KeyM': toggleMute(); break;
    case 'KeyS': toggleShuffle(); break;
    case 'KeyF': toggleFullscreen(); break;
  }
});

// ===== HELPERS =====
function formatTime(seconds) {
  if (!seconds || isNaN(seconds)) return '0:00';
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
}

function shuffleArray(arr) {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function saveLastPlayed(songId) {
  localStorage.setItem('sw_last_song', songId);
}

// ===== GLOBAL SONG PLAY FUNCTION =====
// Used by pages to play songs
window.SW = {
  play: playSong,
  playById: async (songId, songList) => {
    const res = await fetch(`/api/songs/${songId}`);
    const song = await res.json();
    playSong(song, songList || [song]);
  }
};
