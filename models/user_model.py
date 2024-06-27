from pydantic import BaseModel
from typing import Optional, Dict, List,Tuple
from datetime import datetime

class Results(BaseModel):
    user_id: str
    openness: float = 0
    conscientiousness: float = 0
    extraversion: float = 0
    agreeableness: float = 0
    neuroticism: float = 0

class Employee(BaseModel):
    name: str
    user_id: str
    email: str
    supervisor: str
    position: str
    department: str

class User(BaseModel):
    user_id: str
    name: str
    password:str
    email:str
    position: Optional[str]
    attempts: Optional[int]
    supervisor: Optional[str]
    requested: bool
    observed: bool
    allowed_assess: bool
    self_answers: Optional[List[int]]
    supervisor_answers: Optional[List[int]]
    potential:Optional[float] 
    department:Optional[str]
    admin: bool
    competency: float 
    skills: List[Tuple[str, int]]

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
    
