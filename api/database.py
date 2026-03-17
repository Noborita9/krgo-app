from typing import AsyncGenerator

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from pydantic import Field
...
class Settings(BaseSettings):
    database_url: str = Field("postgresql+asyncpg://postgres:postgres@localhost:5432/receipt_splitter", validation_alias="KRGO_APP_DATABASE_URL")
    gemini_api_key: str = Field("", validation_alias="GEMINI_API_KEY")

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Handle conversion from postgres:// to postgresql+asyncpg://
db_url = settings.database_url
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# Neon/Supabase often add ?channel_binding or ?sslmode which can break asyncpg
# We strip everything after '?' to ensure a clean connection string
if "?" in db_url:
    db_url = db_url.split("?")[0]

# Re-add sslmode=require if it was there, as it's safe and recommended
# db_url += "?sslmode=require" 

engine = create_async_engine(db_url, echo=True)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
