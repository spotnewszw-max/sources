import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_read_feeds():
    response = client.get("/feeds/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_article():
    response = client.post("/articles/", json={"title": "Test Article", "content": "This is a test."})
    assert response.status_code == 201
    assert response.json()["title"] == "Test Article"

def test_update_article():
    response = client.put("/articles/1", json={"title": "Updated Article", "content": "Updated content."})
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Article"

def test_delete_article():
    response = client.delete("/articles/1")
    assert response.status_code == 204

def test_read_article():
    response = client.get("/articles/1")
    assert response.status_code == 200
    assert "title" in response.json()