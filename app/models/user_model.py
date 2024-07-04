from typing import Optional, Dict, List, Tuple
from ast import Str
from pydantic import BaseModel,EmailStr,Field
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
    role: str

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
    role: str
    skills: Optional[List[Tuple[str, int]]]  = Field(default=None)
    
    
    
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
    sender_name: str
    reciever_id: Optional[str]
    datetime: datetime
    ntype: str 
    viewed: bool

class OTPRequest(BaseModel):
    email: EmailStr

class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: str

class SetPasswordRequest(BaseModel):
    email: EmailStr
    password: str
