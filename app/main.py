from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth, memory, social, oauth, upload

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
