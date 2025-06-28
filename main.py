from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


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
