from fastapi import FastAPI,APIRouter
from pydantic import BaseModel
from datetime import datetime
from database.db import DatabaseConnection
from models.user_model import User, Results, Notification


router = APIRouter()
# Call the function to set up CORS


class User(BaseModel):
    id: str
    attempts: int = 0
    requested: bool = False

class Supervisor(BaseModel):
    id: str
    notifications: list = []


# Get the number of attempts and  requested flag for a user
@router.get("/api/users/{user_id}/attempts")
async def get_attempts(user_id: str):
    db=DatabaseConnection("users")
    documentID=db.find_id_by_attribute("user_id",user_id)
    return {"attempts": db.get_attribute_value_by_id(documentID,"attempts"), "requested": db.get_attribute_value_by_id(documentID,"requested")}

# Set the `requested` flag to `true` for a user & send notifications
@router.post("/api/users/{user_id}/request")
async def set_request(user_id: str):
    db=DatabaseConnection("users")
    document_id=db.find_id_by_attribute("user_id",user_id)

    if document_id:
        db.update_attribute_by_id(document_id,"requested",True)
        supervisor = db.get_attribute_value_by_id(document_id,"supervisor")
    if supervisor:
        instance = Notification(
            user_id= user_id,
            supervisor= supervisor,
            date= datetime.now(),
            ntype= "self_request" 
            )
        db.add_document(instance.model_dump())
        return {"success": True}
    else:
        return {"success": False}


@router.get("/get_supervisors/")
async def get_supervisors():
    db=DatabaseConnection("users")
    document_id=db.find_id_by_attribute("user_id",user_id)
    return supervisors

@router.get("/get_users/{userId}/")
async def get_users(userId: str):
    db = DatabaseConnection("Users")
    users = db.get_documents_by_attribute("supervisor", userId,["user_id","name"])
    print(users)
    return users