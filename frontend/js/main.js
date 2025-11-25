// ====== CONFIG: set your Railway URL here ======
const API_BASE = 'https://ayamil-ai.up.railway.app'; // <-- Railway URL

// ====== tiny DOM helpers ======
const $ = (sel) => document.querySelector(sel);
const el = (tag, cls = '') => { const d = document.createElement(tag); if (cls) d.className = cls; return d; };

// ====== HTTP helper with error handling ======
async function request(path, body = null, method = 'POST', token = null) {
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = 'Bearer ' + token;

  const res = await fetch(API_BASE + path, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined
  });

  let json = null;
  try { json = await res.json(); } catch (e) { /* ignore */ }

  if (!res.ok) {
    const message = json?.detail || json?.error || JSON.stringify(json) || res.statusText;
    throw new Error(message);
  }

  return json;
}

// ====== Auth helpers ======
function saveSession(token, user) {
  localStorage.setItem('token', token);
  localStorage.setItem('user', JSON.stringify(user));
}
function clearSession() {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
}
function getToken() { return localStorage.getItem('token'); }
function getUser() { try { return JSON.parse(localStorage.getItem('user')); } catch(e){ return null; } }

// ====== Signup handler ======
const signupForm = $('#signup-form');
if (signupForm) {
  signupForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    $('#signup-error')?.style.display = 'none';
    const data = Object.fromEntries(new FormData(signupForm));
    try {
      const res = await request('/signup', data, 'POST');
      saveSession(res.token, res.user);
      location.href = 'chat.html';
    } catch (err) {
      const msg = err.message || 'Signup failed';
      const elErr = $('#signup-error');
      if (elErr) { elErr.innerText = msg; elErr.style.display = 'block'; }
      else alert(msg);
    }
  });
}

// ====== Login handler ======
const loginForm = $('#login-form');
if (loginForm) {
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    $('#login-error')?.style.display = 'none';
    const data = Object.fromEntries(new FormData(loginForm));
    try {
      const res = await request('/login', data, 'POST');
      saveSession(res.token, res.user);
      location.href = 'chat.html';
    } catch (err) {
      const msg = err.message || 'Login failed';
      const elErr = $('#login-error');
      if (elErr) { elErr.innerText = msg; elErr.style.display = 'block'; }
      else alert(msg);
    }
  });
}

// ====== Chat page logic ======
if (location.pathname.endsWith('chat.html')) {
  const token = getToken();
  const user = getUser();
  if (!token || !user) {
    clearSession();
    location.href = 'login.html';
  }

  const userNameEl = $('#user-name');
  const logoutBtn = $('#logout');
  const trainBtn = $('#train-btn');
  const businessTextEl = $('#business-text');
  const loadBusinessBtn = $('#load-business');
  const trainStatusEl = $('#train-status');
  const messagesEl = $('#messages');
  const chatForm = $('#chat-form');
  const messageInput = $('#message-input');
  const chatError = $('#chat-error');

  userNameEl.innerText = user.name || user.email || '';

  logoutBtn.addEventListener('click', () => { clearSession(); location.href = 'index.html'; });

  function pushMessage(text, who = 'assistant') {
    const m = el('div', 'message ' + (who === 'user' ? 'user' : 'assistant'));
    m.innerText = text;
    messagesEl.appendChild(m);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  // Load saved business description
  loadBusinessBtn.addEventListener('click', async () => {
    trainStatusEl.style.display = 'none';
    try {
      const saved = localStorage.getItem('business_text_' + user.id);
      if (saved) {
        businessTextEl.value = saved;
        trainStatusEl.innerText = 'Loaded from local cache';
        trainStatusEl.style.display = 'block';
      } else {
        trainStatusEl.innerText = 'No local saved business text found';
        trainStatusEl.style.display = 'block';
      }
    } catch {
      trainStatusEl.innerText = 'Could not load business text';
      trainStatusEl.style.display = 'block';
    }
  });

  // Train/save business text
  trainBtn.addEventListener('click', async () => {
    trainStatusEl.style.display = 'none';
    const text = businessTextEl.value.trim();
    if (!text) { alert('Write something about your business'); return; }
    try {
      await request('/train-business', { user_id: user.id, business_text: text }, 'POST', token);
      localStorage.setItem('business_text_' + user.id, text);
      trainStatusEl.innerText = 'Business saved & training simulated';
      trainStatusEl.style.display = 'block';
    } catch (err) {
      trainStatusEl.innerText = err.message || 'Failed to save';
      trainStatusEl.style.display = 'block';
    }
  });

  // Chat submission
  chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    chatError.style.display = 'none';
    const text = messageInput.value.trim();
    if (!text) return;
    pushMessage(text, 'user');
    messageInput.value = '';

    try {
      const res = await request('/chat', { user_id: user.id, message: text }, 'POST', token);
      pushMessage(res.reply || 'No reply', 'assistant');
    } catch (err) {
      chatError.innerText = err.message || 'Chat failed';
      chatError.style.display = 'block';
      pushMessage('Sorry, I could not get a reply right now. Try again.', 'assistant');
    }
  });

  // Load last conversation from localStorage
  (function loadCachedConversation() {
    const conv = JSON.parse(localStorage.getItem('conv_' + user.id) || '[]');
    conv.forEach(m => pushMessage(m.text, m.sender));
  })();

  // Save conversation periodically
  const saveConversation = () => {
    const conv = Array.from(messagesEl.children).map(n => ({
      text: n.innerText,
      sender: n.classList.contains('user') ? 'user' : 'assistant'
    }));
    localStorage.setItem('conv_' + user.id, JSON.stringify(conv));
  };
  setInterval(saveConversation, 5000);
  window.addEventListener('beforeunload', saveConversation);
}
