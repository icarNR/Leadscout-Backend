from fastapi import FastAPI,APIRouter,Depends
from pydantic import BaseModel
from datetime import datetime
from app.services.db import DatabaseConnection
from app.models.user_model import User, Results, Notification
from typing import Optional, Dict, List
from app.services.auth import get_current_user  

router = APIRouter()
# Call the function to set up CORS


# class User(BaseModel):
#     id: str
#     attempts: int = 0
#     requested: bool = False

# class Supervisor(BaseModel):
#     id: str
#     notifications: list = []

class AttemptResponse(BaseModel):
    attempts: Optional[int] = 0
    requested: Optional[bool] = False
    allowed: Optional[bool] = False

# Get the number of attempts and  requested flag for a user
@router.get("/api/users/{user_id}/attempts")
async def get_attempts(user_id: str, current_user: dict = Depends(get_current_user)):
    db=DatabaseConnection("Users")
    document=db.get_document_by_attribute("user_id",user_id)
    if document:
        # Extract the attributes from the document
        attempts = document.get("attempts", 0)
        requested = document.get("requested", False)
        allowed = document.get("allowed_assess", False)
        return AttemptResponse(attempts=attempts, requested=requested, allowed=allowed)

    # else:
    #     raise HTTPException(status_code=404, detail="User not found-attempts endpoint")

# Get the number of attempts and  requested flag for a user
# @router.get("/api/users/{user_id}/attempts")
# async def get_attempts(user_id: str):
#     db=DatabaseConnection("Users")
#     document=db.get_document_by_attribute("user_id",user_id)
#     if document:
#         # Extract the attributes from the document
#         userInstance= User(**document)
#         return userInstance
#     else:
#         raise HTTPException(status_code=404, detail="User not found-attempts endpoint")


# Set the `requested` flag to `true` for a user & send notifications
@router.post("/api/users/{user_id}/request")
async def set_request(user_id: str):
    db=DatabaseConnection("Users")
    try:
        document_id=db.find_id_by_attribute("user_id",user_id)
        print(f"--------------------------------------------------------------------{document_id}")
        print(user_id)
        if document_id:
            db.update_attribute_by_id(document_id,"requested",True)
            supervisor = db.get_attribute_value_by_id(document_id,"supervisor")
            # if supervisor:
            #     instance = Notification( 
            #         user_id= user_id,
            #         supervisor= supervisor,
            #         date= datetime.now(),
            #         ntype= "self_request" 
            #         )
            #     db.add_document(instance.model_dump())
            return {"success": True}
        else:
            return {"success": False}
    finally:   
        db.close()

# @router.get("/get_supervisors/")
# async def get_supervisors():
#     db=DatabaseConnection("users")
#     document_id=db.find_id_by_attribute("user_id",user_id)
#     db.close()
#     return supervisors

@router.get("/get_users/{userId}/")
async def get_users(userId: str):
    db = DatabaseConnection("Users")
    users = db.get_documents_by_attribute("supervisor", userId,["user_id","name","observed"])
    print(users)
    return users 