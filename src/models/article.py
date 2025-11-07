from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from datetime import datetime
from src.database.base import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)
    content = Column(Text)
    url = Column(String(512), unique=True, index=True)
    source = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Add PostgreSQL full-text search vector
    search_vector = Column(
        func.to_tsvector('english', func.coalesce(title, '') + ' ' + func.coalesce(content, '')),
        index=True,
        postgresql_using='gin'
    )