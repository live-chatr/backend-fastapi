from fastapi import FastAPI, Depends
from app.routers import users, auth
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.auth.dependencies import get_current_user
from app.models import User
from app.schemas.auth import UserResponse


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
    
@app.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return current_user

app.include_router(auth.router)
app.include_router(users.router)