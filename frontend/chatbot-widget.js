/**
 * Embeddable Chatbot Widget
 * Easy integration for any website
 */

(function () {
    'use strict';

    const ChatbotWidget = {
        config: {
            apiUrl: 'http://localhost:8000',
            position: 'bottom-right',
            primaryColor: '#6366f1',
            greeting: 'Hi! How can I help you today?',
            companyName: 'Support',
        },

        sessionId: null,
        ws: null,
        isOpen: false,
        isMinimized: true,

        init: function (options) {
            this.config = { ...this.config, ...options };
            this.createWidget();
            this.attachEventListeners();
        },

        createWidget: function () {
            const widget = document.getElementById('chatbot-widget');
            if (!widget) return;

            widget.innerHTML = `
                <style>
                    .chatbot-container {
                        position: fixed;
                        ${this.config.position.includes('bottom') ? 'bottom: 20px;' : 'top: 20px;'}
                        ${this.config.position.includes('right') ? 'right: 20px;' : 'left: 20px;'}
                        z-index: 9999;
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    }
                    
                    .chatbot-button {
                        width: 60px;
                        height: 60px;
                        border-radius: 50%;
                        background: ${this.config.primaryColor};
                        color: white;
                        border: none;
                        cursor: pointer;
                        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 24px;
                        transition: transform 0.3s ease, box-shadow 0.3s ease;
                    }
                    
                    .chatbot-button:hover {
                        transform: scale(1.1);
                        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
                    }
                    
                    .chatbot-window {
                        position: absolute;
                        ${this.config.position.includes('bottom') ? 'bottom: 80px;' : 'top: 80px;'}
                        ${this.config.position.includes('right') ? 'right: 0;' : 'left: 0;'}
                        width: 380px;
                        max-width: calc(100vw - 40px);
                        height: 600px;
                        max-height: calc(100vh - 120px);
                        background: white;
                        border-radius: 16px;
                        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
                        display: flex;
                        flex-direction: column;
                        overflow: hidden;
                        transform-origin: ${this.config.position.includes('right') ? 'bottom right' : 'bottom left'};
                    }
                    
                    .chatbot-window.hidden {
                        display: none;
                    }
                    
                    .chatbot-header {
                        background: ${this.config.primaryColor};
                        color: white;
                        padding: 20px;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    }
                    
                    .chatbot-header h3 {
                        margin: 0;
                        font-size: 18px;
                        font-weight: 600;
                    }
                    
                    .chatbot-header p {
                        margin: 5px 0 0 0;
                        font-size: 12px;
                        opacity: 0.9;
                    }
                    
                    .chatbot-close {
                        background: none;
                        border: none;
                        color: white;
                        font-size: 24px;
                        cursor: pointer;
                        padding: 0;
                        width: 30px;
                        height: 30px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        border-radius: 4px;
                        transition: background 0.2s;
                    }
                    
                    .chatbot-close:hover {
                        background: rgba(255, 255, 255, 0.1);
                    }
                    
                    .chatbot-form {
                        padding: 20px;
                        background: #f9fafb;
                    }
                    
                    .chatbot-form input {
                        width: 100%;
                        padding: 12px;
                        margin-bottom: 12px;
                        border: 1px solid #e5e7eb;
                        border-radius: 8px;
                        font-size: 14px;
                        transition: border-color 0.2s;
                    }
                    
                    .chatbot-form input:focus {
                        outline: none;
                        border-color: ${this.config.primaryColor};
                    }
                    
                    .chatbot-form button {
                        width: 100%;
                        padding: 12px;
                        background: ${this.config.primaryColor};
                        color: white;
                        border: none;
                        border-radius: 8px;
                        font-size: 14px;
                        font-weight: 600;
                        cursor: pointer;
                        transition: background 0.2s;
                    }
                    
                    .chatbot-form button:hover {
                        opacity: 0.9;
                    }
                    
                    .chatbot-messages {
                        flex: 1;
                        overflow-y: auto;
                        padding: 20px;
                        background: #f9fafb;
                    }
                    
                    .chatbot-message {
                        margin-bottom: 16px;
                        display: flex;
                        animation: slideIn 0.3s ease;
                    }
                    
                    @keyframes slideIn {
                        from {
                            opacity: 0;
                            transform: translateY(10px);
                        }
                        to {
                            opacity: 1;
                            transform: translateY(0);
                        }
                    }
                    
                    .chatbot-message.user {
                        justify-content: flex-end;
                    }
                    
                    .chatbot-message-content {
                        max-width: 70%;
                        padding: 12px 16px;
                        border-radius: 12px;
                        font-size: 14px;
                        line-height: 1.5;
                    }
                    
                    .chatbot-message.user .chatbot-message-content {
                        background: ${this.config.primaryColor};
                        color: white;
                        border-bottom-right-radius: 4px;
                    }
                    
                    .chatbot-message.bot .chatbot-message-content {
                        background: white;
                        color: #1f2937;
                        border-bottom-left-radius: 4px;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                    }
                    
                    .chatbot-message.admin .chatbot-message-content {
                        background: #10b981;
                        color: white;
                        border-bottom-left-radius: 4px;
                    }
                    
                    .chatbot-input-container {
                        padding: 16px;
                        background: white;
                        border-top: 1px solid #e5e7eb;
                        display: flex;
                        gap: 8px;
                    }
                    
                    .chatbot-input {
                        flex: 1;
                        padding: 12px;
                        border: 1px solid #e5e7eb;
                        border-radius: 24px;
                        font-size: 14px;
                        outline: none;
                    }
                    
                    .chatbot-input:focus {
                        border-color: ${this.config.primaryColor};
                    }
                    
                    .chatbot-send {
                        width: 44px;
                        height: 44px;
                        border-radius: 50%;
                        background: ${this.config.primaryColor};
                        color: white;
                        border: none;
                        cursor: pointer;
                        font-size: 18px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        transition: background 0.2s;
                    }
                    
                    .chatbot-send:hover {
                        opacity: 0.9;
                    }
                    
                    .chatbot-send:disabled {
                        opacity: 0.5;
                        cursor: not-allowed;
                    }
                    
                    .chatbot-status {
                        padding: 12px 20px;
                        background: #fef3c7;
                        color: #92400e;
                        font-size: 13px;
                        text-align: center;
                        border-bottom: 1px solid #fde68a;
                    }
                    
                    .chatbot-typing {
                        padding: 8px 16px;
                        background: white;
                        border-radius: 12px;
                        display: inline-block;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                    }
                    
                    .chatbot-typing span {
                        display: inline-block;
                        width: 8px;
                        height: 8px;
                        border-radius: 50%;
                        background: #9ca3af;
                        margin: 0 2px;
                        animation: typing 1.4s infinite;
                    }
                    
                    .chatbot-typing span:nth-child(2) {
                        animation-delay: 0.2s;
                    }
                    
                    .chatbot-typing span:nth-child(3) {
                        animation-delay: 0.4s;
                    }
                    
                    @keyframes typing {
                        0%, 60%, 100% {
                            transform: translateY(0);
                        }
                        30% {
                            transform: translateY(-10px);
                        }
                    }
                    
                    @media (max-width: 480px) {
                        .chatbot-window {
                            width: calc(100vw - 40px);
                            height: calc(100vh - 120px);
                        }
                    }
                </style>
                
                <div class="chatbot-container">
                    <button class="chatbot-button" id="chatbot-toggle">
                        💬
                    </button>
                    
                    <div class="chatbot-window hidden" id="chatbot-window">
                        <div class="chatbot-header">
                            <div>
                                <h3>${this.config.companyName} Support</h3>
                                <p id="chatbot-status">AI Assistant</p>
                            </div>
                            <button class="chatbot-close" id="chatbot-close">×</button>
                        </div>
                        
                        <div id="chatbot-form-container" class="chatbot-form" style="display: block;">
                            <h4 style="margin: 0 0 15px 0; color: #1f2937;">Start a conversation</h4>
                            <form id="chatbot-start-form">
                                <input type="text" id="client-name" placeholder="Your name" required>
                                <input type="email" id="client-email" placeholder="Your email" required>
                                <input type="tel" id="client-phone" placeholder="Your phone" required>
                                <button type="submit">Start Chat</button>
                            </form>
                        </div>
                        
                        <div id="chatbot-status-container" style="display: none;"></div>
                        
                        <div id="chatbot-messages" class="chatbot-messages" style="display: none;"></div>
                        
                        <div id="chatbot-input-container" class="chatbot-input-container" style="display: none;">
                            <input type="text" id="chatbot-input" class="chatbot-input" placeholder="Type your message...">
                            <button id="chatbot-send" class="chatbot-send">➤</button>
                        </div>
                    </div>
                </div>
            `;
        },

        attachEventListeners: function () {
            const toggle = document.getElementById('chatbot-toggle');
            const close = document.getElementById('chatbot-close');
            const form = document.getElementById('chatbot-start-form');
            const sendBtn = document.getElementById('chatbot-send');
            const input = document.getElementById('chatbot-input');

            toggle?.addEventListener('click', () => this.toggleWidget());
            close?.addEventListener('click', () => this.closeWidget());
            form?.addEventListener('submit', (e) => this.startChat(e));
            sendBtn?.addEventListener('click', () => this.sendMessage());
            input?.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.sendMessage();
            });
        },

        toggleWidget: function () {
            const window = document.getElementById('chatbot-window');
            window.classList.toggle('hidden');
            this.isMinimized = window.classList.contains('hidden');
        },

        closeWidget: function () {
            const window = document.getElementById('chatbot-window');
            window.classList.add('hidden');
            this.isMinimized = true;
        },

        startChat: async function (e) {
            e.preventDefault();

            const name = document.getElementById('client-name').value;
            const email = document.getElementById('client-email').value;
            const phone = document.getElementById('client-phone').value;

            try {
                const response = await fetch(`${this.config.apiUrl}/api/sessions`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        client_info: { name, email, phone }
                    })
                });

                const data = await response.json();
                this.sessionId = data.session_id;

                // Hide form, show chat
                document.getElementById('chatbot-form-container').style.display = 'none';
                document.getElementById('chatbot-messages').style.display = 'block';
                document.getElementById('chatbot-input-container').style.display = 'flex';

                // Connect WebSocket
                this.connectWebSocket();

            } catch (error) {
                console.error('Error starting chat:', error);
                alert('Failed to start chat. Please try again.');
            }
        },

        connectWebSocket: function () {
            const wsUrl = this.config.apiUrl.replace('http', 'ws');
            this.ws = new WebSocket(`${wsUrl}/ws/client/${this.sessionId}`);

            this.ws.onopen = () => {
                console.log('WebSocket connected');
            };

            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };

            this.ws.onclose = () => {
                console.log('WebSocket closed');
            };
        },

        handleMessage: function (data) {
            const statusContainer = document.getElementById('chatbot-status-container');
            const statusText = document.getElementById('chatbot-status');

            if (data.type === 'connected') {
                this.addMessage(data.message, 'bot');
            } else if (data.type === 'message') {
                this.addMessage(data.content, data.sender_type.toLowerCase());
            } else if (data.type === 'handoff_requested') {
                this.addMessage(data.message, 'bot');
                statusContainer.style.display = 'block';
                statusContainer.innerHTML = '<div class="chatbot-status">Connecting you with a human agent...</div>';
                statusText.textContent = 'Waiting for agent...';
            } else if (data.type === 'agent_connected') {
                statusContainer.style.display = 'none';
                this.addMessage(data.message, 'bot');
                statusText.textContent = 'Human Agent';
            } else if (data.type === 'session_closed') {
                this.addMessage(data.message, 'bot');
                statusText.textContent = 'Chat Closed';
                document.getElementById('chatbot-input').disabled = true;
                document.getElementById('chatbot-send').disabled = true;
            }
        },

        addMessage: function (text, sender) {
            const messages = document.getElementById('chatbot-messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `chatbot-message ${sender}`;
            messageDiv.innerHTML = `<div class="chatbot-message-content">${text}</div>`;
            messages.appendChild(messageDiv);
            messages.scrollTop = messages.scrollHeight;
        },

        sendMessage: function () {
            const input = document.getElementById('chatbot-input');
            const message = input.value.trim();

            if (!message || !this.ws || this.ws.readyState !== WebSocket.OPEN) return;

            this.addMessage(message, 'user');
            this.ws.send(JSON.stringify({ content: message }));
            input.value = '';
        }
    };

    // Make it globally available
    window.ChatbotWidget = ChatbotWidget;
})();
