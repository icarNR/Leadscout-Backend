from fastapi import Depends, FastAPI,APIRouter, HTTPException,WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Optional
from app.routes.security import get_current_user1
from app.services.db import DatabaseConnection
from crorSetting import setup_cors
from app.models.user_model import User, Results, Notification
from datetime import datetime
from fastapi import Body
from app.services.auth import get_current_user

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(WebSocket)  
            
            
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
            
manager= ConnectionManager()            
            
@router.websocket("/ws/notifications")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)            

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
        await manager.broadcast(f"New Notification from supervisor {reciever_id}")
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
        await manager.broadcast(f"New Notification from employee {superviseeID}")
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
            await manager.broadcast(f"New Notification from admin")
        finally:
            db.close()
            
@router.get("/notifications", response_model=List[Notification])
async def get_notifications(current_user: dict = Depends(get_current_user(required_roles=["user", "admin"]))):
    db = DatabaseConnection("Notifications")
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID not found in current user")

        documents = db.get_doc_by_attribute("reciever_id", user_id)
        if documents:
            for document in documents:
                document.pop("_id", None)
            return [Notification(**document) for document in documents]
        else:
            raise HTTPException(status_code=404, detail="No notifications found for user_id: {user_id}")
    finally:
        db.close()            
        



