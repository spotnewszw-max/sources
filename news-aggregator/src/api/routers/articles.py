from fastapi import APIRouter, HTTPException
from typing import List
from src.schemas.article import Article, ArticleCreate
from src.repositories.article_repository import ArticleRepository

router = APIRouter()
article_repo = ArticleRepository()

@router.post("/", response_model=Article)
async def create_article(article: ArticleCreate):
    return await article_repo.create(article)

@router.get("/", response_model=List[Article])
async def read_articles(skip: int = 0, limit: int = 10):
    return await article_repo.get_all(skip=skip, limit=limit)

@router.get("/{article_id}", response_model=Article)
async def read_article(article_id: int):
    article = await article_repo.get(article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

@router.put("/{article_id}", response_model=Article)
async def update_article(article_id: int, article: ArticleCreate):
    updated_article = await article_repo.update(article_id, article)
    if updated_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return updated_article

@router.delete("/{article_id}", response_model=dict)
async def delete_article(article_id: int):
    success = await article_repo.delete(article_id)
    if not success:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"message": "Article deleted successfully"}