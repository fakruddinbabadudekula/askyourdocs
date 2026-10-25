from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncEngine,
)
from sqlalchemy.orm import DeclarativeBase


def create_db_engine(db_url: str)->AsyncEngine:
    """Create an async database engine."""
    return create_async_engine(url=db_url)


def create_session_factory(engine) -> async_sessionmaker[AsyncSession]:
    """Create an async session factory."""
    return async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )


class Base(DeclarativeBase):
    pass


async def init_db(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)