"""Module contains sqlalchemy db async connection
contain get_db fucntion which creates a connection instance """


from sqlalchemy.ext.asyncio import AsyncSession,create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings

# an asycn engine to connect the datbase.
a_engine=create_async_engine(
   url= settings.DATABASE_URL
)

class Base(DeclarativeBase):
    pass

async def init_db():
    """Initialize the db. It creates the tables.Must be called before doing anything about the tables."""
    async with a_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    
# an async session maker, returns an contextmanager  
async_session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=a_engine,
    expire_on_commit=False,
)

