from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from datetime import datetime, timedelta
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from database.db import DatabaseConnection
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def send_email(receiver_email: str, subject: str, body: str):
    sender_email = "your-email@gmail.com"
    sender_password = "your-email-password"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        logger.info("Email sent to %s", receiver_email)
    except smtplib.SMTPException as e:
        logger.error("An error occurred while sending the email: %s", e)
        raise HTTPException(status_code=500, detail="An error occurred while sending the email")
    except Exception as e:
        logger.error("General  error occurred while sending email: %s", e)
        raise HTTPException(status_code=500, detail="Failed to send email due to an unexpected error")    
  

@router.post("/request_password_reset")
async def request_password_reset(email: EmailStr):
    dbUser = DatabaseConnection("Users")
    try:
        user_document = dbUser.get_document_by_attribute("email", email)
        if not user_document:
            raise HTTPException(status_code=404, detail="Email not registered")
        
        otp = generate_otp()
        otp_expiration = datetime.utcnow() + timedelta(minutes=10)  # OTP valid for 10 minutes

        user_document["otp"] = otp
        user_document["otp_expiration"] = otp_expiration
        logger.info("Updating user document with new OTP and expiration time: %s", user_document)
        dbUser.replace_document_by_id(user_document["_id"], user_document)

        # Send OTP via email
        logger.info("Sending OTP to user's email")
        send_email(
            receiver_email=email,
            subject="Your OTP Code",
            body=f"Your OTP code is {otp}. It is valid for 10 minutes."
        )

        return {"message": "OTP sent to your email"}
    except HTTPException as e:
        logger.error("HTTP error in request_password_reset: %s", e)
        raise e
    except Exception as e:
        logger.error("General error in request_password_reset: %s", e)
        raise HTTPException(status_code=500, detail="internal server error")
    finally:
        dbUser.close()

@router.post("/reset_password")
async def reset_password(email: EmailStr, otp: str, new_password: str):
    dbUser = DatabaseConnection("Users")
    try:
        user_document = dbUser.get_document_by_attribute("email", email)
        if not user_document:
            raise HTTPException(status_code=404, detail="Email not registered")

        if user_document["otp"] != otp or user_document["otp_expiration"] < datetime.utcnow():
            raise HTTPException(status_code=400, detail="Invalid or expired OTP")

        hashed_password = pwd_context.hash(new_password)
        user_document["hashed_password"] = hashed_password
        user_document["otp"] = None
        user_document["otp_expiration"] = None
        dbUser.replace_document_by_id(user_document["_id"], user_document)

        return {"message": "Password reset successful"}
    finally:
        dbUser.close()
