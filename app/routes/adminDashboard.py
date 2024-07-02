from fastapi import FastAPI, HTTPException, Query, APIRouter
from pydantic import BaseModel, ValidationError
from typing import List, Optional, Tuple
from pymongo import MongoClient
import json

router = APIRouter()

client = MongoClient("mongodb+srv://nisalRavindu:tonyStark#117@cluster0.wsf6jk3.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['Cluster0']
leadership_collection = db['Users']

class Leadership(BaseModel):
    picture: str = " "
    name: str = " "
    user_id: str
    position: str = " "
    potential: float 
    skills: List[Tuple[str, int]]
    observed: bool
    competency: float 
    department: str = "No Department"

# Endpoint to fetch unique departments
@router.get("/departments", response_model=List[str])
async def get_departments():
    try:
        departments = leadership_collection.distinct("department")
        departments = ["No Department" if dept is None else dept for dept in departments]
        return departments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to fetch unique skills    
@router.get("/skills", response_model=List[str])
async def get_skills():
    try:
        leadership_data = leadership_collection.find({}, {"skills": 1})
        unique_skills = set()
        for leader in leadership_data:
            skills = leader.get("skills", [])
            for skill in skills:
                unique_skills.add(skill[0])
        return list(unique_skills)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Helper function to set default values for missing or None fields
def set_default_string(value, default=" "):
    return value if value is not None else default

max_skill_score = 10

def calculate_competency_and_normalize(leader_skills, all_skills):
    # Calculate D values for non-zero skills
    D_values = {skill: leader_skills[skill] - all_skills[skill] for skill in all_skills if skill in leader_skills and all_skills[skill] != 0}
    max_D_value = {skill: max_skill_score - all_skills[skill] for skill in all_skills if skill in leader_skills and all_skills[skill] != 0}

    # Calculate M values for non-zero skills
    M_values = {skill: all_skills[skill] for skill in all_skills if all_skills[skill] != 0}
    max_M_value = {skill: max_skill_score for skill in all_skills if all_skills[skill] != 0}

    if not M_values:
        return 0.0  # Set to 0.0 if no non-zero skills

    # Calculate weights
    M_squared_sum = sum(value ** 2 for value in M_values.values())
    max_M_squared_sum = sum(value ** 2 for value in max_M_value.values())

    W_values = {skill: (value ** 2) / M_squared_sum for skill, value in M_values.items()}
    max_W_values = {skill: (value ** 2) / max_M_squared_sum for skill, value in max_M_value.items()}

    # Calculate competency scores
    competency_score = sum(D_values[skill] * W_values.get(skill, 0) for skill in D_values)
    max_competency_score = sum(max_D_value[skill] * max_W_values.get(skill, 0) for skill in max_D_value)

    # Normalize and return
    return round(0 if max_competency_score == 0 else competency_score / max_competency_score, 4)


# Endpoint to fetch leadership data
@router.get("/src/component/admin/LeadershipTable/", response_model=List[Leadership])
async def get_leadership_data(
    department: Optional[str] = Query(None),
    session_data: Optional[str] = Query(None)
):
    try:
        query = {}
        if department:
            if department == "No Department":
                query['department'] = None
            else:
                query['department'] = department
        else:
            query = {
                "$or": [
                    {"department": {"$exists": False}},
                    {"department": {"$type": 10}},
                    {"department": {"$eq": ""}},
                    {"department": {"$ne": None}}
                ]
            }

        leadership_data = list(leadership_collection.find(query))
        
        filtered_leadership_data = leadership_data

        if session_data:
            session_skills = json.loads(session_data)
            filtered_leadership_data = []
            for leadership in leadership_data:
                leadership_skills = dict(leadership['skills'])
                if all(skill in leadership_skills and leadership_skills[skill] >= int(value) for skill, value in session_skills.items()):
                    filtered_leadership_data.append(leadership)
        
        # Calculate competency scores
        for leader in filtered_leadership_data:
            if session_data:
                all_skills = json.loads(session_data)
                leader_skills = {skill[0]: skill[1] for skill in leader['skills']}

                leader['competency'] = int(calculate_competency_and_normalize(leader_skills, all_skills)*100)
            else:
                leader['competency'] = 0.0 

        for leader in filtered_leadership_data:
            if 'potential' not in leader or leader['potential'] is None:
                leader['potential'] = 0.0
            leader['potential'] = int(leader['potential']*100)  # Convert to percentage and round to two decimal points

            # Set default values for missing or None string fields
            leader['picture'] = set_default_string(leader.get('picture'))
            leader['name'] = set_default_string(leader.get('name'))
            leader['position'] = set_default_string(leader.get('position'))  # Set default for position if None
            leader['department'] = set_default_string(leader.get('department'))  # Add missing key

        # Validate and return filtered leadership data
        leadership_models = []
        for item in filtered_leadership_data:
            try:
                model = Leadership(**item)
                leadership_models.append(model)
            except ValidationError as e:
                pass  # Skip invalid items

        return leadership_models

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def competency_score (D_values, M_values):
    M_squared_sum = sum(value ** 2 for value in M_values.values())
    W_values = {skill: (value ** 2) / M_squared_sum for skill, value in M_values.items()}
    competency_score = sum(D_values[skill] * W_values.get(skill, 0) for skill in D_values)
    return round(competency_score, 3)