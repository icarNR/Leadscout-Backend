from ast import Str
from pydantic import BaseModel,EmailStr
from typing import Optional, Dict, List
from datetime import datetime

class Results(BaseModel):
    user_id: str
    openness: float
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float

class Employee(BaseModel):
    name: str
    user_id: str
    email: str
    supervisor: str
    position: str
    department: str

class User(BaseModel):
    user_id: str
    name: Optional[str] = None
    hashed_password: str 
    email: str
    position: Optional[str] = None
    attempts: Optional[int] = 0
    supervisor: Optional[str] = None
    requested: bool = False
    observed: bool = False
    allowed_assess: bool = False
    self_answers: Optional[List[int]] = []
    supervisor_answers: Optional[List[int]] = []
    potential: Optional[float] = None
    department: Optional[str] = None
    admin: bool = False
    
    
    class Config:
        json_schema_extra = {
            "example": {
                "employee_id": "123",
                "email": "test@test.com",
                "hashed_password": "hashedpassword",
                "name": "John Doe",
                "position": "Developer",
                "attempts": 3,
                "supervisor": "Jane Smith",
                "requested": True,
                "observed": False,
                "allowed_assess": True,
                "self_answers": [],
                "supervisor_answers": [],
                "potential": True,
                "department": "IT",
                "admin": False
            }
        }
    
    
# class SignupRequest(BaseModel):
#     user_id: str
#     name:str
#     email: str
#     password: str    

class Admin(BaseModel):
    user_id: str
    name: str
    password:str
    email:str

class Supervisor(BaseModel):
    user_id: str
    attempts: int
    supervisor: Optional[str]
    requested: bool
    self_answers: Optional[List[int]]
    supervisor_answers: Optional[List[int]]

class Notification(BaseModel):
    sender_id: str
    name: str
    reciever_id: Optional[str]
    datetime: datetime
    ntype: str 
    viewed: bool
    
