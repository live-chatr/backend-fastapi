from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.get("/")
def get_users(db: Session = Depends(get_db)):
    return [] 
