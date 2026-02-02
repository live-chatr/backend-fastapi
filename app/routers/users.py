from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.get("/")
def get_users(db: AsyncSession = Depends(get_db)):
    return [] 
