
from typing import Optional
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from datetime import datetime
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
from app.services.db import DatabaseConnection
from app.models.user_model import OTPRequest, OTPVerifyRequest, SetPasswordRequest, User, Employee
from .security import create_access_token, create_refresh_token, get_current_user1

load_dotenv()

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory OTP cache
otp_cache = {}

def generate_otp() -> str:
    return str(random.randint(100000, 999999))

def send_email_via_smtp(to_email, subject, body):
    from_email = os.getenv("SMTP_EMAIL")
    from_password = os.getenv("SMTP_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = os.getenv("SMTP_PORT")

    message = MIMEMultipart()
    message["From"] = from_email
    message["To"] = to_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "html"))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(from_email, from_password)
        server.sendmail(from_email, to_email, message.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


@router.post("/refresh-token")
async def refresh_token(current_user: User = Depends(get_current_user1)):
    access_token = create_access_token(
        data={"sub": current_user.email, "role": current_user.role, "user_id": current_user.user_id}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login_token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "user_id": user.user_id}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email, "role": user.role, "user_id": user.user_id}
    )
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get("/add_employee")
async def create_document(userID, name, email, department, role, supervisor):
    db = DatabaseConnection("Employees")
    results_instance = Employee(
        user_id=userID,
        name=name,
        position="Senior Software Engineer",
        email=email,
        supervisor=supervisor,
        department=department,
        role=role,
    )
    print(results_instance)
    existing = db.find_id_by_attribute("user_id", userID)
    if existing:
        db.delete_document_by_id(existing)
    db.add_document(results_instance.model_dump())

    return {"status": "success", "message": "Employee added successfully"}

@router.post("/sign_up1")
async def sign_up(request: OTPRequest):
    dbEmployee = DatabaseConnection("Employees")
    try:
        document = dbEmployee.get_document_by_attribute("email", request.email)
        if document:
            otp = generate_otp()
            otp_cache[request.email] = {
                "otp": otp,
                "name": request.name,
                "created_at": datetime.utcnow()
            }
            subject = "Your OTP Code"
            body = f"Your OTP code is {otp}"
            if send_email_via_smtp(request.email, subject, body):
                return {"status": "success", "message": "OTP sent successfully"}
            else:
                raise HTTPException(status_code=500, detail="Failed to send OTP")
        else:
            return {"status": "error", "message": "Email not registered with company"}
    except Exception as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        dbEmployee.close()

@router.post("/verify-otp")
async def verify_otp(request: OTPVerifyRequest):
    if request.email in otp_cache and otp_cache[request.email]["otp"] == request.otp and (datetime.utcnow() - otp_cache[request.email]["created_at"]).seconds < 600:  # OTP valid for 10 minutes
        return {"status": "success", "message": "OTP verified successfully"}
    else:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

@router.post("/set-password-and-sign-up")
async def set_password(request: SetPasswordRequest):
    dbUser = DatabaseConnection("Users")
    dbEmployee = DatabaseConnection("Employees")
    try:
        if request.email not in otp_cache:
            raise HTTPException(status_code=400, detail="OTP verification required")
        
        document = dbEmployee.get_document_by_attribute("email", request.email)
        if document:
            hashed_password = pwd_context.hash(request.password)
            document.pop("_id", None)
            instanceEmployee = Employee(**document)
            instanceUser = User(
                user_id=instanceEmployee.user_id,
                name=otp_cache[request.email]["name"],
                hashed_password=hashed_password,
                email=request.email,
                position=instanceEmployee.position,
                attempts=0,
                supervisor=instanceEmployee.supervisor,
                requested=False,
                observed=False,
                allowed_assess=False,
                self_answers=None,
                supervisor_answers=None,
                potential=None,
                department=instanceEmployee.department,
                role=instanceEmployee.role,
            )
            print(instanceUser)
            existing = dbUser.find_id_by_attribute("email", instanceUser.email)
            if existing:
                return {"status": "error", "message": "User already exists"}
            
            dbUser.add_document(instanceUser.model_dump())
            del otp_cache[request.email]  # Remove OTP after successful password setup
            return {"status": "success", "message": "Registration successfully"}
        else:
            return {"status": "error", "message": "Email not registered with company"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        dbUser.close()
        dbEmployee.close()
        

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


@router.post("/request_password_reset")
async def request_password_reset(request: OTPRequest):
    dbEmployee = DatabaseConnection("Employees")
    try:
        document = dbEmployee.get_document_by_attribute("email", request.email)
        if document:
            otp = generate_otp()
            otp_cache[request.email] = {
                "otp": otp,
                "created_at": datetime.utcnow()
            }
            subject = "Your OTP Code for Password Reset"
            body = f"Your OTP code is {otp}"
            if send_email_via_smtp(request.email, subject, body):
                return {"status": "success", "message": "OTP sent successfully"}
            else:
                raise HTTPException(status_code=500, detail="Failed to send OTP")
        else:
            return {"status": "error", "message": "Email not registered"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        dbEmployee.close()
        
@router.post("/reset_password")
async def reset_password(request: SetPasswordRequest):
    dbUser = DatabaseConnection("Users")
    try:
        if request.email not in otp_cache:
            raise HTTPException(status_code=400, detail="OTP verification required")
        
        document = dbUser.get_document_by_attribute("email", request.email)
        if document:
            hashed_password = pwd_context.hash(request.password)
            dbUser.update_attribute_by_id(document["_id"],"hashed_password", hashed_password)
            del otp_cache[request.email]  # Remove OTP after successful password reset
            return {"status": "success", "message": "Password reset successfully"}
        else:
            return {"status": "error", "message": "Email not registered"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        dbUser.close()        