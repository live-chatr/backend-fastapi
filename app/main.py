from fastapi import FastAPI
from app.routers import users

app = FastAPI()

@app.get("/")
def home():
    return {"message": "FastAPI is running!"}

app.include_router(users.router)