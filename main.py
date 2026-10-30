"""FastAPI 샘플: 간단한 할 일(Todo) CRUD API

실행:
    pip install -r requirements.txt
    uvicorn main:app --reload

문서:
    http://127.0.0.1:8000/docs   (Swagger UI)
    http://127.0.0.1:8000/redoc  (ReDoc)
"""

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field

app = FastAPI(title="Todo Sample API", version="1.0.0")


class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, examples=["장보기"])
    description: str | None = Field(None, max_length=500)
    done: bool = False


class TodoUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    done: bool | None = None


class Todo(TodoCreate):
    id: int


# 메모리 저장소 (서버 재시작 시 초기화됨)
todos: dict[int, Todo] = {}
next_id = 1


@app.get("/")
def root():
    return {"message": "Hello, FastAPI!"}


@app.get("/todos", response_model=list[Todo])
def list_todos(
    done: bool | None = Query(None, description="완료 여부로 필터링"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    items = [t for t in todos.values() if done is None or t.done == done]
    return items[skip : skip + limit]


@app.get("/todos/{todo_id}", response_model=Todo)
def get_todo(todo_id: int):
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todos[todo_id]


@app.post("/todos", response_model=Todo, status_code=status.HTTP_201_CREATED)
def create_todo(payload: TodoCreate):
    global next_id
    todo = Todo(id=next_id, **payload.model_dump())
    todos[next_id] = todo
    next_id += 1
    return todo


@app.patch("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, payload: TodoUpdate):
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Todo not found")
    updated = todos[todo_id].model_copy(update=payload.model_dump(exclude_unset=True))
    todos[todo_id] = updated
    return updated


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int):
    if todos.pop(todo_id, None) is None:
        raise HTTPException(status_code=404, detail="Todo not found")
