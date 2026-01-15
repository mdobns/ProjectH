/**
 * Admin Dashboard JavaScript
 * Handles authentication, WebSocket, and UI interactions
 */

const API_URL = 'http://localhost:8000';
let accessToken = null;
let adminWs = null;
let currentSessionId = null;
let adminInfo = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    attachEventListeners();
});

function attachEventListeners() {
    // Login/Register
    document.getElementById('login-form')?.addEventListener('submit', handleLogin);
    document.getElementById('register-form')?.addEventListener('submit', handleRegister);
    document.getElementById('show-register')?.addEventListener('click', (e) => {
        e.preventDefault();
        showSection('register-section');
    });
    document.getElementById('show-login')?.addEventListener('click', (e) => {
        e.preventDefault();
        showSection('login-section');
    });
    document.getElementById('logout-btn')?.addEventListener('click', handleLogout);

    // Navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const section = item.dataset.section;
            switchSection(section);
        });
    });

    // Chat
    document.getElementById('admin-send-btn')?.addEventListener('click', sendAdminMessage);
    document.getElementById('admin-chat-input')?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendAdminMessage();
    });
    document.getElementById('close-chat-btn')?.addEventListener('click', closeCurrentChat);
}

function checkAuth() {
    accessToken = localStorage.getItem('admin_token');
    if (accessToken) {
        connectAdminWebSocket();
        loadAdminInfo();
    } else {
        showSection('login-section');
    }
}

async function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch(`${API_URL}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        if (!response.ok) throw new Error('Login failed');

        const data = await response.json();
        accessToken = data.access_token;
        localStorage.setItem('admin_token', accessToken);

        connectAdminWebSocket();
        loadAdminInfo();

    } catch (error) {
        alert('Login failed: ' + error.message);
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const username = document.getElementById('reg-username').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    const fullName = document.getElementById('reg-fullname').value;

    try {
        const response = await fetch(`${API_URL}/api/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username,
                email,
                password,
                full_name: fullName || null
            })
        });

        if (!response.ok) throw new Error('Registration failed');

        const data = await response.json();
        accessToken = data.access_token;
        localStorage.setItem('admin_token', accessToken);

        connectAdminWebSocket();
        loadAdminInfo();

    } catch (error) {
        alert('Registration failed: ' + error.message);
    }
}

function handleLogout() {
    localStorage.removeItem('admin_token');
    accessToken = null;
    if (adminWs) adminWs.close();
    showSection('login-section');
}

async function loadAdminInfo() {
    try {
        const response = await fetch(`${API_URL}/api/admin/me`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });

        if (!response.ok) throw new Error('Failed to load admin info');

        adminInfo = await response.json();
        document.getElementById('admin-name').textContent = adminInfo.full_name || adminInfo.username;

        switchSection('queue');

    } catch (error) {
        console.error('Error loading admin info:', error);
        handleLogout();
    }
}

function connectAdminWebSocket() {
    const wsUrl = API_URL.replace('http', 'ws');
    adminWs = new WebSocket(`${wsUrl}/ws/admin?token=${accessToken}`);

    adminWs.onopen = () => {
        console.log('Admin WebSocket connected');
    };

    adminWs.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleAdminMessage(data);
    };

    adminWs.onerror = (error) => {
        console.error('WebSocket error:', error);
    };

    adminWs.onclose = () => {
        console.log('WebSocket closed');
        setTimeout(() => {
            if (accessToken) connectAdminWebSocket();
        }, 3000);
    };
}

function handleAdminMessage(data) {
    console.log('Admin message:', data);

    if (data.type === 'connected') {
        loadQueue();
        loadActiveChats();
    } else if (data.type === 'new_session_queued') {
        loadQueue();
        updateQueueCount(data.queue_size);
    } else if (data.type === 'session_claimed') {
        loadSessionChat(data.session_id);
        showChatWindow(data.session_id, data.client_info);
    } else if (data.type === 'message') {
        if (data.session_id === currentSessionId) {
            addChatMessage(data.content, 'client');
        }
    } else if (data.type === 'queue_update') {
        updateQueueCount(data.queue_size);
    } else if (data.type === 'session_claimed_by_other') {
        loadQueue();
        updateQueueCount(data.queue_size);
    }
}

async function loadQueue() {
    try {
        const response = await fetch(`${API_URL}/api/admin/queue`, {
            headers: { 'Authorization': `Bearer ${accessToken}` }
        });

        const sessions = await response.json();
        renderQueueList(sessions);
        updateQueueCount(sessions.length);

    } catch (error) {
        console.error('Error loading queue:', error);
    }
}

async function loadActiveChats() {
    try {
        const response = await fetch(`${API_URL}/api/admin/active`, {
            headers: { 'Authorization': `Bearer ${accessToken}` }
        });

        const sessions = await response.json();
        renderActiveList(sessions);
        updateActiveCount(sessions.length);

    } catch (error) {
        console.error('Error loading active chats:', error);
    }
}

function renderQueueList(sessions) {
    const container = document.getElementById('queue-list');

    if (sessions.length === 0) {
        container.innerHTML = '<p class="empty-message">No sessions in queue</p>';
        return;
    }

    container.innerHTML = sessions.map(session => `
        <div class="session-card">
            <h3>${session.client_info.name}</h3>
            <p>📧 ${session.client_info.email}</p>
            <p>📱 ${session.client_info.phone}</p>
            <div class="session-meta">
                <span style="color: #6b7280; font-size: 0.85rem;">
                    ${new Date(session.created_at).toLocaleTimeString()}
                </span>
                <button onclick="claimSession('${session.session_id}')">Claim Chat</button>
            </div>
        </div>
    `).join('');
}

function renderActiveList(sessions) {
    const container = document.getElementById('active-list');

    if (sessions.length === 0) {
        container.innerHTML = '<p class="empty-message">No active chats</p>';
        return;
    }

    container.innerHTML = sessions.map(session => `
        <div class="session-card ${session.session_id === currentSessionId ? 'selected' : ''}" 
             onclick="selectActiveChat('${session.session_id}', ${JSON.stringify(session.client_info).replace(/"/g, '&quot;')})">
            <h3>${session.client_info.name}</h3>
            <p>📧 ${session.client_info.email}</p>
        </div>
    `).join('');
}

function claimSession(sessionId) {
    if (adminWs && adminWs.readyState === WebSocket.OPEN) {
        adminWs.send(JSON.stringify({
            type: 'claim_session',
            session_id: sessionId
        }));
    }
}

function selectActiveChat(sessionId, clientInfo) {
    loadSessionChat(sessionId);
    showChatWindow(sessionId, clientInfo);
}

async function loadSessionChat(sessionId) {
    try {
        const response = await fetch(`${API_URL}/api/sessions/${sessionId}/messages`, {
            headers: { 'Authorization': `Bearer ${accessToken}` }
        });

        const messages = await response.json();
        currentSessionId = sessionId;

        const container = document.getElementById('chat-messages');
        container.innerHTML = '';

        messages.forEach(msg => {
            addChatMessage(msg.content, msg.sender_type.toLowerCase(), false);
        });

    } catch (error) {
        console.error('Error loading chat:', error);
    }
}

function showChatWindow(sessionId, clientInfo) {
    document.getElementById('no-chat-selected').classList.add('hidden');
    document.getElementById('chat-container').classList.remove('hidden');

    document.getElementById('chat-client-name').textContent = clientInfo.name;
    document.getElementById('chat-client-info').textContent = `${clientInfo.email} • ${clientInfo.phone}`;

    currentSessionId = sessionId;

    // Switch to active section
    switchSection('active');
}

function addChatMessage(text, sender, scroll = true) {
    const container = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}`;
    messageDiv.innerHTML = `<div class="chat-message-content">${text}</div>`;
    container.appendChild(messageDiv);

    if (scroll) {
        container.scrollTop = container.scrollHeight;
    }
}

function sendAdminMessage() {
    const input = document.getElementById('admin-chat-input');
    const message = input.value.trim();

    if (!message || !adminWs || adminWs.readyState !== WebSocket.OPEN || !currentSessionId) return;

    adminWs.send(JSON.stringify({
        type: 'message',
        session_id: currentSessionId,
        content: message
    }));

    addChatMessage(message, 'admin');
    input.value = '';
}

function closeCurrentChat() {
    if (!currentSessionId || !adminWs || adminWs.readyState !== WebSocket.OPEN) return;

    if (confirm('Are you sure you want to close this chat?')) {
        adminWs.send(JSON.stringify({
            type: 'close_session',
            session_id: currentSessionId
        }));

        document.getElementById('chat-container').classList.add('hidden');
        document.getElementById('no-chat-selected').classList.remove('hidden');
        currentSessionId = null;

        loadActiveChats();
    }
}

function switchSection(section) {
    // Update nav
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.toggle('active', item.dataset.section === section);
    });

    // Update sections
    document.querySelectorAll('.section').forEach(sec => {
        sec.classList.remove('active');
    });
    document.getElementById(`${section}-section`).classList.add('active');

    // Load data for section
    if (section === 'queue') {
        loadQueue();
    } else if (section === 'active') {
        loadActiveChats();
    }
}

function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(sec => {
        sec.classList.remove('active');
    });
    document.getElementById(sectionId).classList.add('active');
}

function updateQueueCount(count) {
    document.getElementById('queue-count').textContent = count;
}

function updateActiveCount(count) {
    document.getElementById('active-count').textContent = count;
}
