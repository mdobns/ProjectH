# FastAPI Chatbot Backend

A production-ready FastAPI backend for a chatbot assistant with AI-to-human handoff capabilities.

## Features

- ✅ **Dual-Mode Chat**: AI agent handles initial conversations, seamlessly transfers to human agents
- ✅ **Real-time Communication**: WebSocket-based live chat for both clients and admins
- ✅ **Google Gemini AI**: Free AI model integration with conversation context
- ✅ **JWT Authentication**: Secure admin access with bcrypt password hashing
- ✅ **Client Information**: Collects name, email, and phone before starting conversations
- ✅ **Queue System**: FIFO queue management for sessions awaiting human agents
- ✅ **Database Support**: SQLite (default) with PostgreSQL ready to uncomment
- ✅ **Session Management**: Track conversation state (AI/HUMAN/CLOSED)
- ✅ **Message History**: Full conversation logging and retrieval

## Project Structure

```
ProjectH/
├── main.py                  # FastAPI application entry point
├── config.py                # Configuration settings
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (create from .env.example)
├── models/                  # Database models
├── schemas/                 # Pydantic schemas
├── auth/                    # JWT authentication
├── websocket/               # WebSocket handlers
├── ai/                      # Gemini AI integration
├── services/                # Business logic
├── routes/                  # REST API endpoints
└── utils/                   # Utility functions
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update:

```bash
# Required: Add your Gemini API key
GEMINI_API_KEY=your-actual-api-key-here

# Required: Change secret key for production
SECRET_KEY=your-secure-random-32-char-secret-key
```

**Get a Gemini API key**: https://aistudio.google.com/app/apikey

### 3. Run the Server

```bash
uvicorn main:app --reload
```

Server will start at `http://localhost:8000`

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Usage Flow

### Client Flow

1. **Create Session** (POST `/api/sessions`)
   ```json
   {
     "client_info": {
       "name": "John Doe",
       "email": "john@example.com",
       "phone": "+1234567890"
     }
   }
   ```
   Returns `session_id`

2. **Connect to WebSocket** (`/ws/client/{session_id}`)
   - Send/receive messages in JSON format
   - AI responds automatically
   - Request human agent by saying "I want to speak to a human"

3. **Message Format**:
   ```json
   {
     "content": "Hello, I need help!"
   }
   ```

### Admin Flow

1. **Register/Login** (POST `/api/auth/register` or `/api/auth/login`)
   ```json
   {
     "username": "admin",
     "password": "securepassword",
     "email": "admin@example.com"
   }
   ```
   Returns JWT `access_token`

2. **Connect to Admin WebSocket** (`/ws/admin?token={access_token}`)
   - Receives queue updates
   - Claims sessions
   - Sends/receives messages

3. **Claim Session**:
   ```json
   {
     "type": "claim_session",
     "session_id": "session-id-here"
   }
   ```

4. **Send Message**:
   ```json
   {
     "type": "message",
     "session_id": "session-id-here",
     "content": "How can I help you?"
   }
   ```

## Database

### SQLite (Default)
Database file: `chatbot.db` (created automatically)

### PostgreSQL (Optional)
Uncomment PostgreSQL lines in:
- `requirements.txt`: Uncomment `psycopg2-binary`
- `models/database.py`: Uncomment PostgreSQL engine configuration
- `.env`: Update `DATABASE_URL`

## REST API Endpoints

### Public Endpoints
- `POST /api/sessions` - Create chat session
- `GET /api/sessions/{session_id}` - Get session details
- `GET /api/sessions/{session_id}/messages` - Get message history

### Authentication
- `POST /api/auth/register` - Register admin
- `POST /api/auth/login` - Login admin
- `POST /api/auth/refresh` - Refresh token

### Admin Endpoints (JWT Protected)
- `GET /api/admin/queue` - Get pending sessions
- `GET /api/admin/active` - Get active sessions
- `GET /api/admin/all-sessions` - Get all sessions
- `POST /api/admin/sessions/{session_id}/claim` - Claim session
- `POST /api/admin/sessions/{session_id}/close` - Close session
- `GET /api/admin/me` - Get current admin info

## WebSocket Endpoints

### Client WebSocket
- **Endpoint**: `/ws/client/{session_id}`
- **No authentication required**
- Auto-connects to AI agent
- Can request human agent

### Admin WebSocket
- **Endpoint**: `/ws/admin?token={jwt_access_token}`
- **JWT authentication required**
- Manages multiple sessions
- Real-time queue updates

## Technologies Used

- **FastAPI** - Modern web framework
- **Uvicorn** - ASGI server
- **SQLAlchemy** - ORM
- **Google Gemini** - AI model
- **JWT** - Authentication
- **WebSockets** - Real-time communication
- **Pydantic** - Data validation

## Development

Run with auto-reload:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Production Deployment

1. Set `DEBUG=False` in `.env`
2. Use strong `SECRET_KEY`
3. Configure PostgreSQL
4. Use production ASGI server (e.g., Gunicorn with Uvicorn workers)
5. Set up reverse proxy (Nginx/Caddy)
6. Enable HTTPS

## License

MIT
