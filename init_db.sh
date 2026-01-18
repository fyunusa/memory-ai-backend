#!/bin/bash

# Wait for database to be ready
echo "Waiting for database..."
sleep 5

# Run database migrations
echo "Creating database tables..."
python -c "
from app.database import engine, Base
from app.models.user import User
from app.models.memory import Memory
from app.models.social_account import SocialAccount
from app.models.permission import Permission

print('Creating all tables...')
Base.metadata.create_all(bind=engine)
print('✅ Database tables created successfully!')
"

echo "Database setup complete!"
