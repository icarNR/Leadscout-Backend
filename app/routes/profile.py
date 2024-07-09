from fastapi import FastAPI,Depends, HTTPException, APIRouter
from pymongo import MongoClient
from pydantic import BaseModel
from app.routes.security import get_current_user

# Connect to MongoDB
client = MongoClient("mongodb+srv://nisalRavindu:tonyStark#117@cluster0.wsf6jk3.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['Cluster0']
results_collection = db['Results']

router = APIRouter()

# Pydantic model for traits data
class TraitsData(BaseModel):
    openness: float = 0.0
    conscientiousness: float = 0.0
    extraversion: float = 0.0
    agreeableness: float = 0.0
    neuroticism: float = 0.0

# API endpoint to fetch profile data by user ID
@router.get("/profile/{user_id}", response_model=TraitsData)
async def get_profile(user_id: str,current_user: dict = Depends(get_current_user(required_roles=["admin"]))):
    profile_data = results_collection.find_one({"user_id": user_id})
    if profile_data:
        traits_data = TraitsData(
            openness=profile_data.get("openness", 0.0),
            conscientiousness=profile_data.get("conscientiousness", 0.0),
            extraversion=profile_data.get("extraversion", 0.0),
            agreeableness=profile_data.get("agreeableness", 0.0),
            neuroticism=profile_data.get("neuroticism", 0.0),
        )
        return traits_data
    else:
        raise HTTPException(status_code=404, detail="Profile not found")
