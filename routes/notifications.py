from fastapi import FastAPI,APIRouter, HTTPException,Depends
from pydantic import BaseModel
from typing import List, Optional
from database.db import DatabaseConnection
from crorSetting import setup_cors
from models.user_model import User, Results, Notification
from datetime import datetime

from routes.security import get_current_user

router = APIRouter()

@router.post("/add_notification/{userID}/{type}")
async def create_document(userID,ntype):
    db = DatabaseConnection("Users")
    try:
        document= db.get_document_by_attribute("user_id",userID)
        if(document):
            document.pop("_id", None)
            instance= User(**document)
            name=instance.name
            receiver_id=instance.supervisor
            print(instance)
    finally:
        db.close()
    
    db = DatabaseConnection("Notifications")
    try:
        instance=Notification(
            sender_id = userID,
            sender_name= name,
            receiver_id= receiver_id,
            datetime= datetime.now(),
            ntype= ntype,
            viewed= False 
            )
        print(instance)
        db.add_document(instance.model_dump()) 
    finally:
        db.close()
@router.get("/notifications",response_model=List[Notification])
async def get_notifications(current_user: User = Depends(get_current_user)):
    db = DatabaseConnection("Notifications")
    try:
        documents = db.get_doc_by_attribute("receiver_id",current_user.user_id)
        if documents:
            for document in documents:
                document.pop("_id", None)
            return [Notification(**document) for document in documents]
        else:
            raise HTTPException(status_code=404, detail="No notifications found")       
    finally:
        db.close()


