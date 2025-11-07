from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from src.core.config import Config

# SQLite specific configuration
DATABASE_URL = Config.DATABASE_URL
if "sqlite" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=Config.DEBUG
    )
else:
    engine = create_engine(
        DATABASE_URL,
        echo=Config.DEBUG
    )

SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()