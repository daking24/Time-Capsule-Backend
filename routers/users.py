from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from pydantic import BaseModel
from utils.security import get_current_user_email

router = APIRouter()

class UserProfileUpdate(BaseModel):
    display_name: str | None = None
    profile_image_url: str | None = None

class UserProfile(BaseModel):
    email: str
    display_name: str | None
    profile_image_url: str | None

@router.get("/me", response_model=UserProfile)
def get_me(db: Session = Depends(get_db), email: str = Depends(get_current_user_email)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/me", response_model=UserProfile)
def update_profile(profile: UserProfileUpdate, db: Session = Depends(get_db), email: str = Depends(get_current_user_email)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if profile.display_name is not None:
        user.display_name = profile.display_name
    if profile.profile_image_url is not None:
        user.profile_image_url = profile.profile_image_url
    
    db.commit()
    db.refresh(user)
    return user
