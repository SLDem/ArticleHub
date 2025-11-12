from fastapi import APIRouter, HTTPException, Depends
from app.models.user import User
from app.services.auth_service import hash_password, verify_password, create_access_token
from app.tasks.celery_app import send_welcome_email
from pydantic import BaseModel

router = APIRouter(prefix="/api/auth")

class RegisterSchema(BaseModel):
    email: str
    password: str
    name: str

class LoginSchema(BaseModel):
    email: str
    password: str

@router.post("/register/", status_code=201)
async def register_user(data: RegisterSchema):
    existing = await User.find_one(User.email == data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=data.email, name=data.name, hashed_password=hash_password(data.password))
    await user.insert()
    send_welcome_email.delay(str(user.id), user.email)
    return {"id": str(user.id), "email": user.email, "name": user.name}

@router.post("/login/")
async def login_user(data: LoginSchema):
    user = await User.find_one(User.email == data.email)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token({"user_id": str(user.id)})
    refresh_token = create_access_token({"user_id": str(user.id)}, expires_delta=1440)  # 1 day
    return {"access": access_token, "refresh": refresh_token}

from app.dependencies import get_current_user

@router.get("/profile/")
async def get_profile(user=Depends(get_current_user)):
    return {"id": str(user.id), "email": user.email, "name": user.name}
