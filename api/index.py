import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.database import engine, Base
from api.routers import sessions

# Create database tables automatically for simplicity
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.begin() as conn:
            # This is helpful for the first run on Vercel
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"Database initialization failed: {e}")
    yield
    await engine.dispose()

app = FastAPI(
    title="Receipt Splitter API",
    description="API for parsing receipts and managing shared payments via sessions.",
    version="1.0.0",
    lifespan=lifespan,
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with /api prefix to match Vercel routing
app.include_router(sessions.router, prefix="/api")

@app.get("/api/health")
def health_check():
    return {
        "status": "ok", 
        "message": "Receipt Splitter API is running!",
        "versions": {
            "sqlalchemy": sqlalchemy.__version__,
            "asyncpg": asyncpg.__version__
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
