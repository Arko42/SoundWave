/**
 * SoundWave App — UI Utilities, Theme, AI Chat, Toast System
 */

// ===== THEME =====
function toggleTheme() {
  const html = document.documentElement;
  const current = html.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', next);
  localStorage.setItem('sw_theme', next);
  document.getElementById('themeIcon').className = next === 'dark' ? 'fas fa-moon' : 'fas fa-sun';

  // Sync to server if logged in
  fetch('/auth/profile', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `theme=${next}&username=${encodeURIComponent(document.querySelector('.user-name')?.textContent || '')}&bio=`
  }).catch(() => {});
}

// Apply saved theme on load
(function() {
  const saved = localStorage.getItem('sw_theme');
  if (saved) document.documentElement.setAttribute('data-theme', saved);
  const icon = document.getElementById('themeIcon');
  if (icon) icon.className = (saved || 'dark') === 'dark' ? 'fas fa-moon' : 'fas fa-sun';
})();

// ===== SIDEBAR TOGGLE =====
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  sidebar.classList.toggle('open');
}

// Close sidebar on outside click (mobile)
document.addEventListener('click', (e) => {
  const sidebar = document.getElementById('sidebar');
  const toggle = document.getElementById('sidebarToggle');
  if (window.innerWidth <= 768 && sidebar?.classList.contains('open')) {
    if (!sidebar.contains(e.target) && !toggle?.contains(e.target)) {
      sidebar.classList.remove('open');
    }
  }
});

// ===== TOAST SYSTEM =====
function showToast(message, type = 'info', duration = 3000) {
  const container = document.getElementById('toastContainer') || createToastContainer();
  const toast = document.createElement('div');
  const icons = { success: 'fa-check-circle', error: 'fa-exclamation-circle', info: 'fa-info-circle', warning: 'fa-exclamation-triangle' };
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `<i class="fas ${icons[type] || icons.info}"></i>${message}`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(20px)';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

function createToastContainer() {
  const c = document.createElement('div');
  c.id = 'toastContainer';
  c.className = 'toast-container';
  document.body.appendChild(c);
  return c;
}

// Auto-dismiss flash toasts
setTimeout(() => {
  document.querySelectorAll('[data-toast]').forEach(t => {
    t.style.transition = 'all 0.3s ease';
    t.style.opacity = '0';
    setTimeout(() => t.remove(), 300);
  });
}, 3000);

// ===== AI CHAT =====
function toggleAIChat() {
  document.getElementById('aiPanel').classList.toggle('open');
}

async function sendAIMessage() {
  const input = document.getElementById('aiInput');
  const message = input.value.trim();
  if (!message) return;
  input.value = '';
  appendAIMessage(message, 'user');

  // Show typing indicator
  const typing = appendAIMessage('...', 'bot', true);

  try {
    const res = await fetch('/api/ai/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    const data = await res.json();
    typing.remove();
    appendAIMessage(data.response || 'Let me find some great music for you! 🎵', 'bot');
  } catch {
    typing.remove();
    appendAIMessage('Connection issue. Try browsing our Discover page! 🎵', 'bot');
  }
}

function appendAIMessage(text, role, isTyping = false) {
  const container = document.getElementById('aiMessages');
  const div = document.createElement('div');
  div.className = `ai-message ${role}`;
  div.innerHTML = `<div class="ai-bubble">${isTyping ? '<i class="fas fa-ellipsis-h"></i>' : escapeHtml(text)}</div>`;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  return div;
}

function setMood(mood) {
  document.getElementById('aiInput').value = `Recommend songs for a ${mood} mood`;
  sendAIMessage();
}

// escapeHtml helper (also in player.js but safe to redefine)
function escapeHtml(str) {
  if (!str) return '';
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// ===== SONG CARD HELPERS =====
// Build a song data object from DOM attributes
function songFromCard(el) {
  return {
    id: parseInt(el.dataset.songId),
    title: el.dataset.title,
    artist: el.dataset.artist,
    album: el.dataset.album || '',
    cover_path: el.dataset.cover || 'default_cover.jpg',
    duration: parseInt(el.dataset.duration) || 0,
    duration_formatted: el.dataset.durationFmt || '0:00',
    lyrics: el.dataset.lyrics || '',
    is_favorite: el.dataset.favorite === 'true'
  };
}

// Collect all song data from current page
function getPageSongs() {
  return Array.from(document.querySelectorAll('[data-song-id]')).map(songFromCard);
}

// Click handler for song cards / trending items
document.addEventListener('click', (e) => {
  const card = e.target.closest('[data-song-id]');
  if (!card) return;
  // Don't trigger if clicking action buttons inside card
  if (e.target.closest('.song-actions, .now-playing-actions, [data-fav-btn], [data-playlist-btn]')) return;

  const song = songFromCard(card);
  const allSongs = getPageSongs();
  playSong(song, allSongs);
});

// Favorite button handlers in song cards
document.addEventListener('click', (e) => {
  const btn = e.target.closest('[data-fav-btn]');
  if (!btn) return;
  e.stopPropagation();
  const songId = parseInt(btn.dataset.favBtn);
  toggleFavorite(songId).then(() => {
    btn.classList.toggle('active');
  }).catch(() => {
    window.location.href = '/auth/login';
  });
});

// Add to playlist button
document.addEventListener('click', (e) => {
  const btn = e.target.closest('[data-playlist-btn]');
  if (!btn) return;
  e.stopPropagation();
  const songId = parseInt(btn.dataset.playlistBtn);
  toggleAddToPlaylist(songId);
});

// ===== ANIMATIONS =====
// Staggered page entrance animations
document.addEventListener('DOMContentLoaded', () => {
  const items = document.querySelectorAll('.song-card, .grid-card, .trending-item, .stat-card');
  items.forEach((el, i) => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(16px)';
    setTimeout(() => {
      el.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
      el.style.opacity = '1';
      el.style.transform = 'translateY(0)';
    }, 50 + i * 30);
  });
});

// ===== LOAD USER PLAYLISTS FOR MODAL =====
// Override the fetch in player.js for user playlists
const originalFetch = window.fetch;
// Monkey-patch the playlists endpoint for the modal
if (!window.apiPlaylistsPatched) {
  window.apiPlaylistsPatched = true;
}

// ===== DRAG & DROP for Upload =====
document.addEventListener('DOMContentLoaded', () => {
  const zone = document.querySelector('.upload-zone');
  if (!zone) return;

  zone.addEventListener('dragover', (e) => { e.preventDefault(); zone.classList.add('drag-over'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
  zone.addEventListener('drop', (e) => {
    e.preventDefault();
    zone.classList.remove('drag-over');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const fileInput = document.getElementById('audioInput');
      if (fileInput) {
        fileInput.files = files;
        handleAudioSelected(files[0]);
      }
    }
  });
});

// ===== API: User Playlists for Modal =====
// Patch the /api/user/playlists endpoint
(async () => {
  // This runs if needed by the modal
})();

// ===== GSAP ANIMATIONS (if available) =====
if (typeof gsap !== 'undefined') {
  // Animate player on first load
  gsap.from('.music-player', { y: 90, opacity: 0, duration: 0.8, ease: 'power3.out', delay: 0.5 });
  gsap.from('.sidebar-logo', { x: -30, opacity: 0, duration: 0.6, ease: 'power3.out', delay: 0.2 });
  gsap.from('.hero-title', { y: 30, opacity: 0, duration: 0.8, ease: 'power3.out', delay: 0.3 });
}

// ===== COVER IMAGE SPINNING ANIMATION =====
const style = document.createElement('style');
style.textContent = `
  .now-playing-cover.spinning img {
    animation: coverSpin 8s linear infinite;
  }
  @keyframes coverSpin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  .now-playing-cover img { border-radius: 10px; transition: border-radius 0.3s; }
  .now-playing-cover.spinning img { border-radius: 50%; }
`;
document.head.appendChild(style);

console.log('🎵 SoundWave App Initialized');
