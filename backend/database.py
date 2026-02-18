from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
import os
import ssl
from dotenv import load_dotenv

load_dotenv()

# Neon Database Connection String
DATABASE_URL = os.getenv("DATABASE_URL")

engine = None

if DATABASE_URL:
    # Ensure correct scheme for asyncpg
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

    # asyncpg does not support sslmode/channel_binding params
    # We need to remove them from URL and handle SSL via connect_args
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

    parsed = urlparse(DATABASE_URL)
    params = parse_qs(parsed.query)

    ssl_required = "sslmode" in params
    # Remove asyncpg-incompatible params
    for key in ["sslmode", "channel_binding"]:
        params.pop(key, None)

    # Rebuild URL without incompatible params
    new_query = urlencode(params, doseq=True)
    clean_url = urlunparse(parsed._replace(query=new_query))

    connect_args = {}
    if ssl_required:
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        connect_args["ssl"] = ssl_ctx

    engine = create_async_engine(clean_url, echo=False, future=True, connect_args=connect_args)


async def init_db():
    if engine is None:
        print("⚠️  DATABASE_URL not configured, skipping database init")
        return
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    if engine is None:
        raise RuntimeError("Database not configured. Set DATABASE_URL in .env")
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
