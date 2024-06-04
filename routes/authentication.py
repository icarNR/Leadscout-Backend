
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from pydantic import BaseModel, EmailStr
from motor.motor_asyncio import AsyncIOMotorClient
from database import db
from database.db import DatabaseConnection
from models.user_model import  User,SignupRequest
from .security import create_access_token, get_current_user, create_refresh_token


from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

@router.post("/refresh-token")
async def refresh_token(current_user: User = Depends(get_current_user)):
    access_token = create_access_token(
        data={"sub": current_user.email}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    db=DatabaseConnection("Users")
    user = await db.authenticate_user(form_data.username,form_data.password)
    if not user :
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.email}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email}
    )
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/sign_up")
async def get_signup(signup_request:SignupRequest):
    db=DatabaseConnection("Users")
    return await db.create_user(
        signup_request.user_id,
        signup_request.name,
        signup_request.email,
        signup_request.password)
    # return "Success"

@router.post("/checkMail")
async def checkMail(email: EmailStr):
    user = await db.users.find_one({"email": email})
    if user:
        return {"exists": True}
    else:
        return {"exists": False}

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user