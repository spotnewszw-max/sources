from fastapi import Depends
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..core.config import get_settings

def get_database_session(db: Session = Depends(get_db)):
    return db

def get_settings_instance():
    return get_settings()