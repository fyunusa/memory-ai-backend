# Memory Service Backend

OAuth for Personal Memory - Backend API

## Features

- 🔐 User authentication with JWT
- 🌐 Social media integrations (Facebook, LinkedIn, Twitter)
- 💾 Memory storage with vector search
- 🔍 Semantic memory retrieval
- 🎯 Granular permission management
- 📊 Usage analytics and audit logs

## Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL
- **Vector DB:** Qdrant
- **Cache:** Redis
- **Task Queue:** Celery
- **Embeddings:** OpenAI / Sentence Transformers

## Project Structure

```
memory-service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app
│   ├── config.py               # Configuration
│   ├── database.py             # Database connection
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── memory.py
│   │   ├── social_account.py
│   │   └── permission.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── memory.py
│   │   └── auth.py
│   ├── routers/                # API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── memory.py
│   │   ├── social.py
│   │   └── oauth.py
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── memory_service.py
│   │   ├── embedding_service.py
│   │   ├── facebook_service.py
│   │   ├── twitter_service.py
│   │   └── linkedin_service.py
│   └── utils/                  # Utilities
│       ├── __init__.py
│       ├── security.py
│       └── dependencies.py
├── alembic/                    # Database migrations
├── tests/
├── requirements.txt
└── .env.example
```

## Setup

1. **Clone and setup:**
```bash
cd memory-service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Environment variables:**
```bash
cp .env.example .env
# Edit .env with your credentials
```

3. **Database setup:**
```bash
# Start PostgreSQL and Redis
docker-compose up -d

# Run migrations
alembic upgrade head
```

4. **Run the server:**
```bash
uvicorn app.main:app --reload
```

API will be available at: http://localhost:8000
Docs at: http://localhost:8000/docs

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `POST /auth/refresh` - Refresh access token

### OAuth Social Media
- `GET /auth/facebook` - Initiate Facebook OAuth
- `GET /auth/facebook/callback` - Facebook OAuth callback
- `GET /auth/twitter` - Initiate Twitter OAuth
- `GET /auth/twitter/callback` - Twitter OAuth callback
- `GET /auth/linkedin` - Initiate LinkedIn OAuth
- `GET /auth/linkedin/callback` - LinkedIn OAuth callback

### Memory Management
- `POST /memory/store` - Store new memory
- `GET /memory/query` - Query memories with semantic search
- `GET /memory/list` - List all memories
- `DELETE /memory/{id}` - Delete memory
- `POST /memory/sync/{platform}` - Sync memories from social platform

### Permissions
- `GET /permissions` - List granted permissions
- `POST /permissions/grant` - Grant permission to AI app
- `DELETE /permissions/{id}` - Revoke permission

## Development

```bash
# Run tests
pytest

# Format code
black app/
isort app/

# Type checking
mypy app/
```

## License

MIT
