from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings


# Creating connection engin to the db
motore_database = create_async_engine(settings.DATABASE_URL)


# Creating a single session per user
SessionLocal = async_sessionmaker(
    motore_database,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)
# Removing autocommit gives you full control over saving operations
# Autoflush prepares information for autocommit, keeping it active makes no sense


async def get_db():
    async with SessionLocal() as db:
        yield db

        # Regardless of whether the function is finished or not(crash), the db closes