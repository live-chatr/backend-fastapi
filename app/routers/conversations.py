from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.models import User
from app.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/chats",
    tags=["chats"]
)

@router.get('/')
def chats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    print(f'User id is {current_user.id}')
    return []