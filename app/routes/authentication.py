
from typing import Optional
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from motor.motor_asyncio import AsyncIOMotorClient
from services import db
from services.db import DatabaseConnection
from models.user_model import  User,Employee
from .security import create_access_token, get_current_user, create_refresh_token


router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/refresh-token")
async def refresh_token(current_user:User = Depends(get_current_user)):
    access_token = create_access_token(
        data={"sub": current_user.email}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login_token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    db=DatabaseConnection("Users")
    user = await authenticate_user(form_data.username,form_data.password)
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
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer","role":"admin" if user.admin else "user"}


@router.get("/add_employee")
async def create_document(userID,name,email,department,type,supervisor):
    db = DatabaseConnection("Employees")
    results_instance=Employee(
        user_id= userID,
        name=name,
        position="Senior Softweare Engineer",
        email=email,
        supervisor=supervisor,
        department=department,
        type=type
        )
    print(results_instance)
    existing =db.find_id_by_attribute("user_id",userID)
    if existing:
        db.delete_document_by_id(existing)
    db.add_document(results_instance.model_dump())





@router.post("/sign_up1")
async def create_document(
    name:str =Body(),
    email: str = Body(...),
    password: str = Body(...)):
    
    
    dbEmployee = DatabaseConnection("Employees")
    dbUser = None
    
    try:
        hashed_password = pwd_context.hash(password)
        document= dbEmployee.get_document_by_attribute("email",email)
        if(document):
            dbUser = DatabaseConnection("Users")
            document.pop("_id", None)
            instanceEmployee= Employee(**document)
            instanceUser=User(
                user_id= instanceEmployee.user_id,
                name=name,
                hashed_password=hashed_password,
                email=email,
                position=instanceEmployee.position,
                attempts= 0,
                supervisor= instanceEmployee.supervisor,
                requested= False,
                observed= 0,
                allowed_assess= False,
                self_answers= None,
                supervisor_answers= None,
                potential=None,
                department= instanceEmployee.department,
                admin=(instanceEmployee.type.lower()=="admin"),
                
            )
            print(instanceUser)
            existing =dbUser.find_id_by_attribute("email",instanceUser.email)
            if existing:
                return {"status": "error", "message": "User already exists"}
                ##return massage to front end request saying user already exist cont signup
                
     
            ##sender email to this email address to confirm this sign in(atherizetion)    
            ## if confirm button click then
            dbUser.add_document(instanceUser.model_dump())
            return {"status": "success", "message": "Signup successful"}
        else:
            
            return {"status": "error", "message": "Email not registered with company"}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}
            
    finally:    
        dbEmployee.close()
        if dbUser:
            dbUser.close()
        
    
    


async def authenticate_user(email: str, password: str) -> Optional[User]:
    """Authenticate a user by email and password."""
    dbUser1 = DatabaseConnection("Users")
    try:
        user_document = dbUser1.get_document_by_attribute("email", email)
        if not user_document:
            return None
        user = User(**user_document)
        if not pwd_context.verify(password, user.hashed_password):
            return None
        return user
    finally:
        dbUser1.close()