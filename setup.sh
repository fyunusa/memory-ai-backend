#!/bin/bash

echo "🚀 Setting up Memory Service..."

# Create .env from example
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please update .env with your actual credentials"
fi

# Create virtual environment
echo "🐍 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✨ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Start Docker services
echo "🐳 Starting Docker services (PostgreSQL, Redis, Qdrant)..."
docker-compose up -d

# Wait for databases to be ready
echo "⏳ Waiting for databases to be ready..."
sleep 5

# Initialize database
echo "🗄️  Initializing database..."
alembic upgrade head || echo "⚠️  Alembic migrations not set up yet. Run manually: alembic upgrade head"

echo ""
echo "✅ Setup complete!"
echo ""
echo "📚 Next steps:"
echo "1. Update .env file with your API credentials"
echo "2. Run: source venv/bin/activate"
echo "3. Run: uvicorn app.main:app --reload"
echo "4. Visit: http://localhost:8000/docs"
echo ""
echo "🎉 Happy coding!"
