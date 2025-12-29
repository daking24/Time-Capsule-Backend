from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from database import get_db
from models.user import User
from utils.security import get_password_hash, verify_password, create_access_token
import random
import string
from services.email import send_email, send_verification_email

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# In-memory store for magic codes (For MVP purposes. Use Redis or DB for production)
magic_codes = {}

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class EmailRequest(BaseModel):
    email: EmailStr

class CodeVerify(BaseModel):
    email: EmailStr
    code: str

@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Login immediately
    access_token = create_access_token(data={"sub": new_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Authenticate
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate Token
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/request-code")
async def request_magic_code(request: EmailRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Generate 6-digit code
    code = ''.join(random.choices(string.digits, k=6))
    magic_codes[request.email] = code
    
    # Check if user exists, if not, create them (auto-registration for SSO flow)
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        # Create user with random password since they are using Code Auth
        temp_pass = get_password_hash(''.join(random.choices(string.ascii_letters, k=8)))
        user = User(email=request.email, hashed_password=temp_pass)
        db.add(user)
        db.commit()

    # Send Email
    background_tasks.add_task(send_verification_email, request.email, code)

    print(f"------------\nMAGIC CODE for {request.email}: {code}\n------------") 
    return {"message": "Code sent to email"}

@router.post("/verify-code", response_model=Token)
def verify_magic_code(verify: CodeVerify, db: Session = Depends(get_db)):
    if verify.email not in magic_codes or magic_codes[verify.email] != verify.code:
        raise HTTPException(status_code=400, detail="Invalid or expired code")
    
    # Code valid, clear it
    del magic_codes[verify.email]
    
    user = db.query(User).filter(User.email == verify.email).first()
    if not user:
         raise HTTPException(status_code=400, detail="User not found")

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
