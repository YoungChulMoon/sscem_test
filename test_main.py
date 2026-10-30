from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_root():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json() == {"message": "Hello, FastAPI!"}


def test_todo_crud():
    res = client.post("/todos", json={"title": "장보기"})
    assert res.status_code == 201
    todo_id = res.json()["id"]

    res = client.get(f"/todos/{todo_id}")
    assert res.json()["title"] == "장보기"

    res = client.patch(f"/todos/{todo_id}", json={"done": True})
    assert res.json()["done"] is True

    res = client.get("/todos", params={"done": True})
    assert any(t["id"] == todo_id for t in res.json())

    assert client.delete(f"/todos/{todo_id}").status_code == 204
    assert client.get(f"/todos/{todo_id}").status_code == 404


def test_validation_error():
    res = client.post("/todos", json={"title": ""})
    assert res.status_code == 422
