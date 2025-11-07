from enum import Enum
from datetime import datetime
from typing import Optional, List, Generic, TypeVar
from pydantic import BaseModel, HttpUrl

T = TypeVar('T')

class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

class ArticleFilter(BaseModel):
    search: Optional[str] = None
    source: Optional[str] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    sort_by: Optional[str] = "created_at"
    sort_order: Optional[SortOrder] = SortOrder.desc

class ArticleBase(BaseModel):
    title: str
    content: Optional[str] = None
    url: HttpUrl
    source: Optional[str] = None

class ArticleCreate(ArticleBase):
    pass

class ArticleUpdate(ArticleBase):
    title: Optional[str] = None
    url: Optional[HttpUrl] = None

class ArticleInDB(ArticleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True