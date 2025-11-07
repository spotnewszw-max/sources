from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy import or_, and_, desc, asc, func, text
from sqlalchemy.orm import Session
from src.database.base import SessionLocal
from src.models.article import Article
from src.schemas.article import (
    ArticleCreate, ArticleUpdate, ArticleInDB, 
    PaginatedResponse, SortOrder
)
from src.utils.cache import cache_response
from typing import List, Optional
from datetime import datetime, timedelta
import math

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ArticleInDB, status_code=status.HTTP_201_CREATED)
async def create_article(article: ArticleCreate, db: Session = Depends(get_db)):
    db_article = Article(**article.model_dump())
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

@router.get("/", response_model=PaginatedResponse[ArticleInDB])
@cache_response(expire_seconds=60)
async def list_articles(
    search: Optional[str] = Query(None, description="Search in title and content"),
    source: Optional[str] = Query(None, description="Filter by source"),
    from_date: Optional[datetime] = Query(None, description="Filter from date"),
    to_date: Optional[datetime] = Query(None, description="Filter to date"),
    sort_by: str = Query("created_at", description="Sort by field"),
    sort_order: SortOrder = Query(SortOrder.desc, description="Sort order"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db)
):
    # Base query
    query = db.query(Article)

    # Apply full-text search if search term provided
    if search:
        search_query = func.plainto_tsquery('english', search)
        query = query.filter(Article.search_vector.match(search_query))

    # Apply filters
    if source:
        query = query.filter(Article.source == source)

    if from_date:
        query = query.filter(Article.created_at >= from_date)
    if to_date:
        query = query.filter(Article.created_at <= to_date)

    # Get total count
    total = query.count()

    # Apply sorting
    sort_column = getattr(Article, sort_by, Article.created_at)
    query = query.order_by(
        asc(sort_column) if sort_order == SortOrder.asc 
        else desc(sort_column)
    )

    # Apply pagination
    offset = (page - 1) * size
    articles = query.offset(offset).limit(size).all()

    # Calculate total pages
    pages = math.ceil(total / size)

    return PaginatedResponse(
        items=articles,
        total=total,
        page=page,
        size=size,
        pages=pages
    )

@router.get("/sources", response_model=List[str])
async def list_sources(db: Session = Depends(get_db)):
    """Get list of unique article sources"""
    sources = db.query(Article.source).distinct().all()
    return [source[0] for source in sources if source[0]]

@router.get("/{article_id}", response_model=ArticleInDB)
async def get_article(article_id: int, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

@router.put("/{article_id}", response_model=ArticleInDB)
async def update_article(article_id: int, article: ArticleUpdate, db: Session = Depends(get_db)):
    db_article = db.query(Article).filter(Article.id == article_id).first()
    if not db_article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    update_data = article.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_article, field, value)
    
    db.commit()
    db.refresh(db_article)
    return db_article

@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(article_id: int, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    db.delete(article)
    db.commit()
    return None

@router.get("/stats", response_model=dict)
@cache_response(expire_seconds=300)
async def get_article_stats(
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    """Get detailed article statistics"""
    
    # Base query
    base_query = db.query(Article)
    if from_date:
        base_query = base_query.filter(Article.created_at >= from_date)
    if to_date:
        base_query = base_query.filter(Article.created_at <= to_date)

    # Get stats
    stats = {
        "total_articles": base_query.count(),
        "sources_count": db.query(func.count(Article.source.distinct())).scalar(),
        "latest_article": db.query(Article.created_at)
            .order_by(desc(Article.created_at))
            .first()[0],
        "articles_by_source": db.query(
            Article.source,
            func.count(Article.id)
        ).group_by(Article.source).all(),
        "articles_by_day": db.query(
            func.date_trunc('day', Article.created_at),
            func.count(Article.id)
        ).group_by(text('1')).order_by(text('1')).all(),
        "avg_articles_per_day": db.query(
            func.avg(func.count(Article.id))
        ).group_by(func.date_trunc('day', Article.created_at)).scalar()
    }
    return stats