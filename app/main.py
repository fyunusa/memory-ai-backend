from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth, memory, social, oauth, upload
from app.database import engine, Base, SessionLocal
from app.models.user import User
from app.models.memory import Memory
from app.models.social_account import SocialAccount
from app.models.permission import Permission
from passlib.context import CryptContext

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="OAuth for Personal Memory - Backend API"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables and test user on startup
@app.on_event("startup")
async def startup_event():
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        # Create test user if not exists
        db = SessionLocal()
        try:
            existing_user = db.query(User).filter(User.id == 1).first()
            if not existing_user:
                pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
                test_user = User(
                    id=1,
                    email='test@example.com',
                    username='testuser',
                    hashed_password=pwd_context.hash('password123')
                )
                db.add(test_user)
                db.commit()
                print("✅ Test user created (id=1)")
            else:
                print("✅ Test user already exists")
        finally:
            db.close()
    except Exception as e:
        print(f"❌ Startup error: {e}")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(memory.router, prefix="/memory", tags=["Memory"])
app.include_router(social.router, prefix="/social", tags=["Social Media"])
app.include_router(oauth.router, prefix="/oauth", tags=["OAuth"])
app.include_router(upload.router, prefix="/upload", tags=["File Uploads"])


@app.get("/")
async def root():
    return {
        "message": "Memory Service API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
