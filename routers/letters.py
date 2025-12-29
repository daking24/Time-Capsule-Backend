from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.letter import Letter
from models.user import User
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from fastapi.security import OAuth2PasswordBearer
from utils.security import SECRET_KEY, ALGORITHM
from jose import jwt

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

def get_current_user_email(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return email
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

class LetterCreate(BaseModel):
    # Email is inferred from token now
    content_text: Optional[str] = None
    media_url: Optional[str] = None
    media_type: str = "text"
    delivery_date: datetime

class LetterRead(BaseModel):
    id: int
    content_text: Optional[str]
    media_url: Optional[str]
    media_type: str
    delivery_date: datetime
    is_sent: bool
    created_at: datetime
    
    class Config:
        orm_mode = True

@router.post("/letters")
def create_letter(letter: LetterCreate, db: Session = Depends(get_db), email: str = Depends(get_current_user_email)):
    # Ensure delivery_date is naive UTC for simple comparison
    delivery_date = letter.delivery_date.replace(tzinfo=None)
    
    db_letter = Letter(
        email=email, # Use authenticated email
        content_text=letter.content_text,
        media_url=letter.media_url,
        media_type=letter.media_type,
        delivery_date=delivery_date
    )
    db.add(db_letter)
    db.commit()
    db.refresh(db_letter)
    return db_letter

@router.get("/letters", response_model=List[LetterRead])
def get_letters(db: Session = Depends(get_db), email: str = Depends(get_current_user_email)):
    return db.query(Letter).filter(Letter.email == email).order_by(Letter.created_at.desc()).all()

