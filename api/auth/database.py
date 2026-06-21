from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from api.core.config import settings
from api.auth.models import Base

_raw_url = settings.DATABASE_URL
if _raw_url.startswith("sqlite:///"):
    DATABASE_URL = _raw_url.replace("sqlite:///", "sqlite+aiosqlite:///")
elif _raw_url.startswith("postgres://"):
    # Render/Heroku-style URLs use "postgres://" — SQLAlchemy needs "postgresql+asyncpg://"
    DATABASE_URL = _raw_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif _raw_url.startswith("postgresql://"):
    DATABASE_URL = _raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)
else:
    DATABASE_URL = _raw_url

engine = create_async_engine(DATABASE_URL, echo=settings.DEBUG)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Self-healing migration: older deployments created TIMESTAMP WITHOUT TIME ZONE
        # columns, but the app inserts timezone-aware datetimes. Safe to re-run.
        if DATABASE_URL.startswith("postgresql+asyncpg://"):
            from sqlalchemy import text
            alters = [
                "ALTER TABLE users ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE USING created_at AT TIME ZONE 'UTC'",
                "ALTER TABLE users ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE USING updated_at AT TIME ZONE 'UTC'",
                "ALTER TABLE api_keys ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE USING created_at AT TIME ZONE 'UTC'",
                "ALTER TABLE api_keys ALTER COLUMN last_used TYPE TIMESTAMP WITH TIME ZONE USING last_used AT TIME ZONE 'UTC'",
                "ALTER TABLE api_keys ALTER COLUMN expires_at TYPE TIMESTAMP WITH TIME ZONE USING expires_at AT TIME ZONE 'UTC'",
                "ALTER TABLE scan_logs ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE USING created_at AT TIME ZONE 'UTC'",
            ]
            for stmt in alters:
                try:
                    await conn.execute(text(stmt))
                except Exception:
                    pass

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
