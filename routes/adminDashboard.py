from fastapi import FastAPI, HTTPException, Query, APIRouter
from pydantic import BaseModel, ValidationError
from typing import List, Optional, Tuple
from database.db import DatabaseConnection
import json

router = APIRouter()

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

# Helper function for distinct operation
def get_distinct_values(db_connection, key):
    try:
        return db_connection.collection.distinct(key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Helper function for find operation
def find_documents(db_connection, query, projection=None):
    try:
        if projection:
            return list(db_connection.collection.find(query, projection))
        else:
            return list(db_connection.collection.find(query))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/departments", response_model=List[str])
async def get_departments():
    db_connection = DatabaseConnection("Users")
    try:
        departments = get_distinct_values(db_connection, "department")
        departments = ["No Department" if dept is None else dept for dept in departments]
        return departments
    finally:
        db_connection.close()

@router.get("/skills", response_model=List[str])
async def get_skills():
    db_connection = DatabaseConnection("Users")
    try:
        leadership_data = find_documents(db_connection, {}, {"skills": 1})
        unique_skills = set()
        for leader in leadership_data:
            skills = leader.get("skills", [])
            for skill in skills:
                unique_skills.add(skill[0])
        return list(unique_skills)
    finally:
        db_connection.close()

def set_default_string(value, default=" "):
    return value if value is not None else default

@router.get("/src/component/admin/LeadershipTable/", response_model=List[Leadership])
async def get_leadership_data(
    department: Optional[str] = Query(None),
    session_data: Optional[str] = Query(None)
):
    db_connection = DatabaseConnection("Users")
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

        leadership_data = find_documents(db_connection, query)
        filtered_leadership_data = leadership_data

        if session_data:
            session_skills = json.loads(session_data)
            filtered_leadership_data = []
            for leadership in leadership_data:
                leadership_skills = dict(leadership['skills'])
                if all(skill in leadership_skills and leadership_skills[skill] >= int(value) for skill, value in session_skills.items()):
                    filtered_leadership_data.append(leadership)

        for leader in filtered_leadership_data:
            if session_data:
                all_skills = json.loads(session_data)
                leader_skills = {skill[0]: skill[1] for skill in leader['skills']}

                D_values = {skill: leader_skills[skill] - all_skills[skill] for skill in all_skills if skill in leader_skills and all_skills[skill] != 0}
                M_values = {skill: all_skills[skill] for skill in all_skills if all_skills[skill] != 0}

                if M_values:
                    M_squared_sum = sum(value ** 2 for value in M_values.values())
                    W_values = {skill: (value ** 2) / M_squared_sum for skill, value in M_values.items()}
                    competency_score = sum(D_values[skill] * W_values.get(skill, 0) for skill in D_values)
                    leader['competency'] = round(competency_score, 3)
                else:
                    leader['competency'] = 0.0
            else:
                leader['competency'] = 0.0

        for leader in filtered_leadership_data:
            if 'potential' not in leader or leader['potential'] is None:
                leader['potential'] = 0.0
            leader['potential'] = round(leader['potential'] * 100, 2)
            leader['picture'] = set_default_string(leader.get('picture'))
            leader['name'] = set_default_string(leader.get('name'))
            leader['position'] = set_default_string(leader.get('position'))
            leader['department'] = set_default_string(leader.get('department'))

        leadership_models = []
        for item in filtered_leadership_data:
            try:
                model = Leadership(**item)
                leadership_models.append(model)
            except ValidationError as e:
                pass

        return leadership_models
    finally:
        db_connection.close()
