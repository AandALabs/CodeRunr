import logging

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.engine import URL
from core.config import settings
from db.base import Base  # noqa: F401 — re-export for Alembic env.py

logger = logging.getLogger(__name__)


def create_db_url() -> str:
    """
    Create a DB URL and return as str
    """
    url = URL.create(
        drivername="postgresql+asyncpg",
        username=settings.POSTGRES_USER.get_secret_value(),
        password=settings.POSTGRES_PASSWORD.get_secret_value(),
        host=settings.POSTGRES_HOST.get_secret_value(),
        port=settings.POSTGRES_PORT,
        database=settings.POSTGRES_DB.get_secret_value(),
    )

    logger.info(f"Database URL: {url.render_as_string(hide_password=True)}")

    url_str = url.render_as_string(hide_password=False)
    return url_str


db_url = create_db_url()
engine = create_async_engine(db_url, echo=False)
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            raise
        finally:
            await session.close()
