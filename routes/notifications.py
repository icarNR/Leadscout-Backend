from fastapi import FastAPI,APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from database.db import DatabaseConnection
from crorSetting import setup_cors
from models.user_model import User, Results, Notification
from datetime import datetime

router = APIRouter()

@router.post("/add_notification/{userID}/{type}")
async def create_document(userID,ntype):
    db = DatabaseConnection("Users")
    try:
        document= db.get_document_by_Attribute("user_id",userID)
        if(document):
            document.pop("_id", None)
            instance= User(**document)
            name=instance.name
            reciever_id=instance.supervisor
            print(instance)
    finally:
        db.close()
    
    # db = DatabaseConnection("Notifications")
    # try:
    #     instance=Notification(
    #         sender_id = userID,
    #         sender_name= name,
    #         reciever_id= reciever_id ,
    #         datetime= datetime.now(),
    #         ntype= ntype,
    #         viewed= False 
    #         )
    #     print(instance)
    #     # db.add_document(results_instance.model_dump()) 
    # finally:
    #     db.close()

    
