from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from api.core.config import settings
from api.auth.models import Base

DATABASE_URL = settings.DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")

engine = create_async_engine(DATABASE_URL, echo=settings.DEBUG)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
