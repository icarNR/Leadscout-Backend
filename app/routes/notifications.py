from fastapi import Depends, FastAPI,APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.routes.security import get_current_user
from app.services.db import DatabaseConnection
from crorSetting import setup_cors
from app.models.user_model import User, Results, Notification
from datetime import datetime
from fastapi import Body

router = APIRouter()

@router.post("/add_supervisor_notification")
async def create_document(
    userID: str = Body(...),
    ntype: str = Body(...) 
    ):
    print(userID)
    print(ntype)
    db = DatabaseConnection("Users")
    document= db.get_document_by_attribute("user_id",userID)
    if(document):
            document.pop("_id", None)
            instance= User(**document)
            name=instance.name
            reciever_id=instance.supervisor
    db.close()

    db = DatabaseConnection("Notifications")
    try:
        instance=Notification(
            sender_id = userID,
            sender_name= name,
            reciever_id= reciever_id ,
            datetime= datetime.now(), 
            ntype= ntype,
            viewed= False 
            )
        print(instance)
        db.add_document(instance.model_dump()) 
    finally:
        db.close()
        

@router.post("/add_employee_notification")
async def create_document(
    userID: str = Body(...),
    superviseeID: str = Body(...),
    ntype: str = Body(...) 
    ):

    db = DatabaseConnection("Users")
    document= db.get_document_by_attribute("user_id",userID)
    if(document):
            document.pop("_id", None)
            instance= User(**document)
            name=instance.name
    db.close()
    
    db = DatabaseConnection("Notifications")
    try:
        instance=Notification(
            sender_id = userID,
            sender_name= name,
            reciever_id= superviseeID,
            datetime= datetime.now(), 
            ntype= ntype,
            viewed= False 
            )
        print(instance)
        db.add_document(instance.model_dump()) 
    finally:
        db.close()

        
@router.post("/add_admin_notification")
async def create_document(
    userID: str = Body(...),
    ntype: str = Body(...) 
    ):

    db = DatabaseConnection("Users")
    document= db.get_document_by_attribute("user_id",userID)
    if(document):
            document.pop("_id", None)
            instance= User(**document)
            name=instance.name
    db.close()

    if(instance.self_answers and instance.supervisor_answers):
        db = DatabaseConnection("Notifications")
        try:
            instance=Notification(
                sender_id = userID,
                sender_name= name,
                reciever_id= "admin",
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
        documents = db.get_doc_by_attribute("reciever_id",current_user.user_id)
        if documents:
            for document in documents:
                document.pop("_id", None)
            return [Notification(**document) for document in documents]
        else:
            raise HTTPException(status_code=404, detail="No notifications found") 
               
    finally:
        db.close()

