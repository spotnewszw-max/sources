from fastapi import APIRouter, HTTPException
from typing import List
from src.schemas.article import Article

router = APIRouter()

# Sample in-memory storage for feeds
feeds = []

@router.post("/feeds/", response_model=Article)
async def create_feed(feed: Article):
    feeds.append(feed)
    return feed

@router.get("/feeds/", response_model=List[Article])
async def get_feeds():
    return feeds

@router.get("/feeds/{feed_id}", response_model=Article)
async def get_feed(feed_id: int):
    if feed_id < 0 or feed_id >= len(feeds):
        raise HTTPException(status_code=404, detail="Feed not found")
    return feeds[feed_id]

@router.delete("/feeds/{feed_id}", response_model=Article)
async def delete_feed(feed_id: int):
    if feed_id < 0 or feed_id >= len(feeds):
        raise HTTPException(status_code=404, detail="Feed not found")
    return feeds.pop(feed_id)