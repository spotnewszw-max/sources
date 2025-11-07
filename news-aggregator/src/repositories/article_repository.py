from sqlalchemy.orm import Session
from src.db.models import Article  # Assuming Article is the model for articles

class ArticleRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_article(self, article_data):
        new_article = Article(**article_data)
        self.db.add(new_article)
        self.db.commit()
        self.db.refresh(new_article)
        return new_article

    def get_article(self, article_id: int):
        return self.db.query(Article).filter(Article.id == article_id).first()

    def update_article(self, article_id: int, article_data):
        article = self.get_article(article_id)
        if article:
            for key, value in article_data.items():
                setattr(article, key, value)
            self.db.commit()
            self.db.refresh(article)
        return article

    def delete_article(self, article_id: int):
        article = self.get_article(article_id)
        if article:
            self.db.delete(article)
            self.db.commit()
        return article