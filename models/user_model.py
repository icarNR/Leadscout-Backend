from pydantic import BaseModel
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
    supervisor: str
    position: str
    name: str
    user_id: str
    email: str

class User(BaseModel):
    user_id: str
    name: str
    password:str
    email:str
    position: str
    attempts: Optional[int]
    supervisor: Optional[str]
    requested: bool
    self_answers: Optional[List[int]]
    supervisor_answers: Optional[List[int]]
    potential:float
    department:str

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
    user_id: str
    name: str
    supervisor: Optional[str]
    date: datetime
    ntype: str 
    
