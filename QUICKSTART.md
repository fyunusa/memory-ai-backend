# 🚀 Memory Service - Quick Start

## What We Built

A backend API for "OAuth for Personal Memory" - allowing users to store memories from social media (Facebook, LinkedIn, Twitter) and grant AI applications access to their personal context.

## Project Structure

```
memory-service/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py          # User model
│   │   ├── memory.py        # Memory model
│   │   ├── social_account.py # Social account connections
│   │   └── permission.py    # Permission management
│   ├── schemas/             # Pydantic schemas
│   ├── routers/             # API endpoints
│   │   ├── auth.py          # Authentication
│   │   ├── memory.py        # Memory CRUD
│   │   ├── oauth.py         # OAuth flows
│   │   └── social.py        # Social media sync
│   ├── services/            # Business logic (to be implemented)
│   └── utils/               # Utilities
│       ├── security.py      # JWT & password hashing
│       └── dependencies.py  # FastAPI dependencies
├── docker-compose.yml       # PostgreSQL, Redis, Qdrant
├── requirements.txt         # Python dependencies
└── setup.sh                 # Setup script
```

## Quick Setup (5 minutes)

### Option 1: Automated Setup

```bash
cd memory-service
./setup.sh
```

### Option 2: Manual Setup

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup environment
cp .env.example .env
# Edit .env with your credentials

# 4. Start databases
docker-compose up -d

# 5. Run server
uvicorn app.main:app --reload
```

## Test the API

### 1. Register a User

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "SecurePassword123"
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123"
  }'
```

Save the `access_token` from the response.

### 3. Store a Memory

```bash
curl -X POST "http://localhost:8000/memory/store" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "content": "I love MacBooks because they are reliable",
    "source": "manual",
    "category": "preferences",
    "metadata": {"topic": "technology"}
  }'
```

### 4. Query Memories

```bash
curl -X POST "http://localhost:8000/memory/query" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "query": "laptop preferences",
    "limit": 10
  }'
```

## API Documentation

Once running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Current Status

### ✅ Implemented:
- User registration and authentication (JWT)
- Basic memory storage and retrieval
- Database models for users, memories, social accounts, permissions
- API structure for OAuth flows
- Docker setup for PostgreSQL, Redis, Qdrant

### 🚧 To Be Implemented:
- Vector embeddings with OpenAI/Qdrant
- Semantic search for memories
- Facebook OAuth integration
- Twitter OAuth integration
- LinkedIn OAuth integration
- Social media data sync
- Permission management for AI apps
- Rate limiting
- API key management for AI apps

## Next Steps

### Phase 1: Vector Search (Week 1)
1. Implement embedding service with OpenAI
2. Store embeddings in Qdrant
3. Implement semantic search in `/memory/query`

### Phase 2: OAuth Integration (Week 2)
1. Facebook OAuth flow
2. Twitter OAuth flow
3. LinkedIn OAuth flow
4. Data extraction from each platform

### Phase 3: Permission System (Week 3)
1. AI app registration
2. OAuth-style permission grants
3. Access token generation for AI apps
4. Usage tracking and audit logs

### Phase 4: Production Ready (Week 4)
1. Rate limiting
2. Caching with Redis
3. Background tasks with Celery
4. Production deployment (Railway/Render)

## Development Commands

```bash
# Run server with auto-reload
uvicorn app.main:app --reload

# Run tests (once implemented)
pytest

# Format code
black app/
isort app/

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Environment Variables

Key variables to configure in `.env`:

```
DATABASE_URL=postgresql://user:password@localhost:5432/memory_service
OPENAI_API_KEY=your-key-here
FACEBOOK_APP_ID=your-facebook-app-id
TWITTER_API_KEY=your-twitter-api-key
LINKEDIN_CLIENT_ID=your-linkedin-client-id
```

## Database Schema

### Users Table
- `id`, `email`, `username`, `hashed_password`
- `is_active`, `is_verified`
- Timestamps

### Memories Table
- `id`, `user_id`, `content`, `source`
- `category`, `metadata`
- `vector_id` (for Qdrant)
- Timestamps

### Social Accounts Table
- `id`, `user_id`, `platform`
- `platform_user_id`, `access_token`
- OAuth tokens and profile data

### Permissions Table
- `id`, `user_id`, `app_name`, `app_id`
- `scopes` (granted permissions)
- `expires_at`, usage tracking

## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  FastAPI    │ ◄── JWT Auth
│   Router    │
└──────┬──────┘
       │
       ├──► PostgreSQL (Structured data)
       │
       ├──► Qdrant (Vector search)
       │
       ├──► Redis (Cache + Queue)
       │
       └──► Social Media APIs
            (Facebook, Twitter, LinkedIn)
```

## Troubleshooting

**Database connection error:**
```bash
docker-compose up -d
# Wait 5 seconds for PostgreSQL to start
```

**Import errors:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**OAuth not working:**
- Check `.env` has correct credentials
- Ensure redirect URIs match in OAuth app settings

## Support

For questions or issues, check the README.md or create an issue on GitHub.

---

**Next Session:** We'll implement vector embeddings and semantic search! 🚀
