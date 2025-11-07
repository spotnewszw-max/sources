from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers import feeds, articles

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(feeds.router, prefix="/feeds", tags=["feeds"])
app.include_router(articles.router, prefix="/articles", tags=["articles"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the News Aggregator API"}