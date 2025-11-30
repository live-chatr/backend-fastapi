from fastapi import FastAPI
from app.routers import users, auth
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings


app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def home():
    return {"message": "FastAPI is running!"}

app.include_router(auth.router)
app.include_router(users.router)