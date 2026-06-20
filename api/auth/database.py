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

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
