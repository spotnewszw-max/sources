from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers import articles

app = FastAPI(
    title="Sources Media API",
    description="News aggregation and content management API",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(articles.router, prefix="/api/articles", tags=["articles"])