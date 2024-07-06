from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pymongo import MongoClient
from bson import ObjectId
from models.user_model import Skill, Criteria

router = APIRouter()

# Connect to MongoDB
client = MongoClient("mongodb+srv://nisalRavindu:tonyStark#117@cluster0.wsf6jk3.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['Cluster0']
criteria_collection = db['Criteria']

# Helper function
def criteria_helper(criteria) -> Criteria:
    skills = []
    for skill in criteria.get("skills", []):
        if isinstance(skill, list) and len(skill) == 2:
            skills.append({"name": skill[0], "score": skill[1]})
    return Criteria(
        id=criteria["criteria_id"],  # Use criteria_id here
        name=criteria["jobPosition"],
        department=criteria["Department"],
        skills=skills
    )

# Routes for Criteria
@router.get("/criteria", response_model=List[Criteria])
async def get_criteria():
    criteria_list = criteria_collection.find()
    return [criteria_helper(criteria) for criteria in criteria_list]

@router.get("/criteria/{criteria_id}", response_model=Criteria)
async def get_criteria_by_id(criteria_id: str):
    criteria = criteria_collection.find_one({"criteria_id": criteria_id})
    if criteria:
        return criteria_helper(criteria)
    raise HTTPException(status_code=404, detail=f"Criteria with id {criteria_id} not found")

@router.get("/criteriafilter", response_model=List[Criteria])
async def get_criteria_filter(
    department: Optional[str] = Query(None, description="Filter criteria by department"),
    search_id: Optional[str] = Query(None, description="Search criteria by ID")
):
    query = {}
    if department:
        query["Department"] = department
    if search_id:
        query["criteria_id"] = search_id

    criteria_list = criteria_collection.find(query)
    return [criteria_helper(criteria) for criteria in criteria_list]

# Routes for Skills
@router.get("/skills/{criteria_id}", response_model=List[Skill])
async def get_skills_by_criteria(criteria_id: str):
    criteria = criteria_collection.find_one({"criteria_id": criteria_id})
    if criteria:
        skills = []
        for skill in criteria.get("skills", []):
            if isinstance(skill, list) and len(skill) == 2:
                skills.append({"name": skill[0], "score": skill[1]})
        return skills
    raise HTTPException(status_code=404, detail=f"No skills found for criteria ID: {criteria_id}")

# Root welcome message
@router.get("/")
async def read_root():
    return {"message": "Welcome to the combined Criteria and Skills API!"}
