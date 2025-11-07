from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Article(BaseModel):
    id: Optional[int] = None
    title: str
    content: str
    author: str
    published_at: datetime
    url: str

class ArticleCreate(BaseModel):
    title: str
    content: str
    author: str
    published_at: datetime
    url: str

class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    url: Optional[str] = None