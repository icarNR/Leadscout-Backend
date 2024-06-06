from fastapi import FastAPI,APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from database.db import DatabaseConnection
from crorSetting import setup_cors
from models.user_model import User, Results, Notification
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
        
