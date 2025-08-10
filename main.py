from fastapi import FastAPI
from pydantic import BaseModel
from config import create_tables
from routers import users, auth

app = FastAPI()


# アプリケーション起動時にテーブルを作成
@app.on_event("startup")
async def startup_event():
    create_tables()


class AddRequest(BaseModel):
    a: float
    b: float


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


@app.post("/add")
def add_numbers(request: AddRequest):
    """2つの数値を加算して結果を返す"""
    result = request.a + request.b
    return {
        "a": request.a,
        "b": request.b,
        "result": result,
        "message": f"{request.a} + {request.b} = {result}",
    }


# ルーターの登録
app.include_router(users.router)
app.include_router(auth.router)
