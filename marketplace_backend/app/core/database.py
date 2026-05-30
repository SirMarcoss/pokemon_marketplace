from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import declarative_base
from app.core.config import settings


# Creating connection engin to the db
motore_database = create_engine(settings.DATABASE_URL)


# Creating the single session per user
SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = motore_database)
# Removing autocommit gives you full control over saving operations
# Autoflush prepares information for autocommit, keeping it active makes no sense


Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db  # Regardless of whether the function is finished or not(crash), the db closes
    finally:
        db.close()