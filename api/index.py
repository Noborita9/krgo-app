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
    async with engine.begin() as conn:
        # Warning: create_all is good for dev, in production use Alembic migrations
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Cleanup logic (if any) here
    await engine.dispose()

app = FastAPI(
    title="Receipt Splitter API",
    description="API for parsing receipts and managing shared payments via sessions.",
    version="1.0.0",
    lifespan=lifespan,
)

# Set up CORS for the future Vue frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(sessions.router)

# Mount static files for payment confirmations
os.makedirs("uploads/payments", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Receipt Splitter API! Visit /docs for the interactive API documentation."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
