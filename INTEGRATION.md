# Chatbot Integration Guide

## 🚀 Quick Start - Add to Your Website

Add our AI-powered chatbot to your website in just 3 simple steps:

### Step 1: Add the Script

Copy and paste this code before the closing `</body>` tag of your website:

```html
<!-- Chatbot Widget -->
<div id="chatbot-widget"></div>
<script src="https://your-domain.com/chatbot-widget.js"></script>
<script>
    ChatbotWidget.init({
        apiUrl: 'https://your-api-domain.com',
        position: 'bottom-right',
        primaryColor: '#6366f1',
        greeting: 'Hi! How can I help you today?',
        companyName: 'Your Company'
    });
</script>
```

### Step 2: Configure

Customize the widget to match your brand:

- **apiUrl**: Your chatbot API endpoint
- **position**: `'bottom-right'`, `'bottom-left'`, `'top-right'`, or `'top-left'`
- **primaryColor**: Your brand color (hex code)
- **greeting**: Custom welcome message
- **companyName**: Your company/brand name

### Step 3: You're Done!

The chatbot will now appear on your website. Visitors can start chatting immediately!

---

## 📋 Configuration Options

### Basic Configuration

```javascript
ChatbotWidget.init({
    // Required
    apiUrl: 'https://api.example.com',
    
    // Optional
    position: 'bottom-right',          // Widget position
    primaryColor: '#6366f1',           // Brand color
    greeting: 'Hello! Need help?',     // Welcome message
    companyName: 'Acme Corp'           // Your company name
});
```

### Advanced Configuration

```javascript
ChatbotWidget.init({
    apiUrl: 'https://api.example.com',
    position: 'bottom-right',
    primaryColor: '#6366f1',
    
    // Appearance
    buttonIcon: '💬',                  // Custom button icon
    buttonSize: 60,                    // Button size in pixels
    windowWidth: 380,                  // Chat window width
    windowHeight: 600,                 // Chat window height
    
    // Behavior
    autoOpen: false,                   // Auto-open on page load
    autoOpenDelay: 3000,               // Delay before auto-open (ms)
    saveToLocalStorage: true,          // Remember user info
    
    // Messages
    greeting: 'Hi there!',
    placeholder: 'Type your message...',
    offlineMessage: 'We are offline',
    
    // Branding
    companyName: 'Your Company',
    companyLogo: 'https://...',        // Optional logo URL
});
```

---

## 🎨 Styling & Customization

### Custom Colors

```javascript
ChatbotWidget.init({
    apiUrl: 'https://api.example.com',
    primaryColor: '#FF5733',           // Main accent color
    headerBackground: '#1F2937',       // Header background
    userBubbleColor: '#FF5733',        // User message color
    botBubbleColor: '#F3F4F6'          // Bot message color
});
```

### Custom CSS

Override default styles by adding your own CSS:

```css
/* Customize button */
.chatbot-button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    width: 70px !important;
    height: 70px !important;
}

/* Customize window */
.chatbot-window {
    border-radius: 20px !important;
    box-shadow: 0 20px 60px rgba(0,0,0,0.3) !important;
}

/* Customize messages */
.chatbot-message.user .chatbot-message-content {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
}
```

---

## 🔧 API Integration

### For Developers

If you want to build a custom frontend, use our REST API and WebSocket endpoints:

#### Create a Chat Session

```javascript
const response = await fetch('https://api.example.com/api/sessions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        client_info: {
            name: 'John Doe',
            email: 'john@example.com',
            phone: '+1234567890'
        }
    })
});

const { session_id } = await response.json();
```

#### Connect to WebSocket

```javascript
const ws = new WebSocket(`wss://api.example.com/ws/client/${session_id}`);

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};

// Send message
ws.send(JSON.stringify({
    content: 'Hello, I need help!'
}));
```

#### Get Message History

```javascript
const response = await fetch(`https://api.example.com/api/sessions/${session_id}/messages`);
const messages = await response.json();
```

---

## 🛠️ Installation Methods

### Method 1: CDN (Recommended)

Fastest way to integrate - no setup required:

```html
<div id="chatbot-widget"></div>
<script src="https://cdn.your-domain.com/chatbot-widget.js"></script>
<script>
    ChatbotWidget.init({
        apiUrl: 'https://api.your-domain.com'
    });
</script>
```

### Method 2: Self-Hosted

Download and host the widget files yourself:

1. Download `chatbot-widget.js`
2. Place it in your website's assets folder
3. Reference it in your HTML:

```html
<div id="chatbot-widget"></div>
<script src="/assets/js/chatbot-widget.js"></script>
<script>
    ChatbotWidget.init({
        apiUrl: 'https://api.your-domain.com'
    });
</script>
```

### Method 3: NPM Package

For React, Vue, or other frameworks:

```bash
npm install @your-company/chatbot-widget
```

```javascript
import ChatbotWidget from '@your-company/chatbot-widget';

ChatbotWidget.init({
    apiUrl: 'https://api.your-domain.com'
});
```

---

## 🌐 Framework Integration

### React

```jsx
import { useEffect } from 'react';

function App() {
    useEffect(() => {
        // Load widget script
        const script = document.createElement('script');
        script.src = '/chatbot-widget.js';
        script.onload = () => {
            window.ChatbotWidget.init({
                apiUrl: 'https://api.your-domain.com',
                primaryColor: '#6366f1'
            });
        };
        document.body.appendChild(script);
    }, []);

    return (
        <div>
            <div id="chatbot-widget"></div>
            {/* Your app content */}
        </div>
    );
}
```

### Vue.js

```vue
<template>
    <div>
        <div id="chatbot-widget"></div>
        <!-- Your app content -->
    </div>
</template>

<script>
export default {
    mounted() {
        const script = document.createElement('script');
        script.src = '/chatbot-widget.js';
        script.onload = () => {
            window.ChatbotWidget.init({
                apiUrl: 'https://api.your-domain.com',
                primaryColor: '#6366f1'
            });
        };
        document.body.appendChild(script);
    }
}
</script>
```

### WordPress

1. Go to **Appearance** → **Theme Editor**
2. Open `footer.php`
3. Add the chatbot code before `</body>`:

```php
<!-- Chatbot Widget -->
<div id="chatbot-widget"></div>
<script src="https://your-domain.com/chatbot-widget.js"></script>
<script>
    ChatbotWidget.init({
        apiUrl: 'https://api.your-domain.com',
        primaryColor: '#6366f1',
        companyName: '<?php bloginfo("name"); ?>'
    });
</script>
```

---

## 📊 Admin Dashboard

Access your admin dashboard to manage conversations:

### URL

```
https://your-domain.com/admin.html
```

### Features

- **Live Queue**: See customers waiting for human assistance
- **Active Chats**: Manage ongoing conversations
- **Real-time Notifications**: Get alerted when new sessions arrive
- **Message History**: View past conversations

### Admin Credentials

Create admin accounts via API or registration page:

```bash
curl -X POST "https://api.your-domain.com/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@company.com",
    "password": "secure_password_here",
    "full_name": "Admin Name"
  }'
```

---

## 🔐 Security Best Practices

### HTTPS Only

Always use HTTPS for your API and widget:

```javascript
ChatbotWidget.init({
    apiUrl: 'https://api.your-domain.com'  // ✅ HTTPS
    // NOT: 'http://...'  // ❌ Insecure
});
```

### CORS Configuration

Configure allowed origins in your backend `.env`:

```bash
# In backend config.py, set:
cors_origins: List[str] = [
    "https://your-website.com",
    "https://www.your-website.com"
]
```

### API Rate Limiting

Protect your API with rate limiting (recommended):

- Client sessions: 10/minute
- Messages: 60/minute
- Admin actions: 100/minute

---

## 🐛 Troubleshooting

### Widget Not Appearing

1. Check browser console for errors
2. Verify `chatbot-widget.js` is loading
3. Ensure `apiUrl` is correct
4. Check CORS settings

### WebSocket Connection Failed

1. Verify API is running
2. Check firewall settings
3. Ensure WebSocket protocol (`ws://` or `wss://`)
4. Test with: `wscat -c wss://api.your-domain.com/ws/client/test`

### Messages Not Sending

1. Check session was created successfully
2. Verify WebSocket is connected
3. Check network tab for errors
4. Ensure Gemini API key is configured

---

## 📞 Support

### Getting Help

- **Documentation**: https://docs.your-domain.com
- **Email**: support@your-company.com
- **Live Chat**: Available on our website

### Pricing Plans

Contact us for custom pricing based on:
- Monthly message volume
- Number of admin seats
- Custom features
- White-label options

---

## ✅ Checklist for Go-Live

- [ ] Widget added to website
- [ ] API endpoint configured
- [ ] Gemini API key set
- [ ] Admin account created
- [ ] Brand colors customized
- [ ] Welcome message personalized
- [ ] HTTPS enabled
- [ ] CORS configured
- [ ] Tested on mobile devices
- [ ] Admin dashboard accessible

---

## 📝 License

This chatbot service is proprietary software. Contact us for licensing terms.

**© 2026 Your Company Name. All rights reserved.**
