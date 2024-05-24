from fastapi import FastAPI,APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from database.db import DatabaseConnection
from crorSetting import setup_cors
from models.user_model import User, Results, Notification
router = APIRouter()
# Call the function to set up CORS

class AssessmentAnswers(BaseModel):
    user_id: str
    assessed_id: str
    answers: List[Optional[int]]  # Optional because some questions


def sum_of_indices(lst, indices):
    return sum(lst[i] for i in indices if i < len(lst))

def cal_extro(lst) : return (sum_of_indices(lst,[0,10,15,25,35])-sum_of_indices(lst,[5,20,30]))/(10)
def cal_agree(lst) : return (sum_of_indices(lst,[6,16,21,31,41])-sum_of_indices(lst,[1,11,26,36]))/(5)
def cal_consc(lst) : return (sum_of_indices(lst,[2,12,27,32,37])-sum_of_indices(lst,[7,17,22,42]))/(5)
def cal_neuro(lst) : return (sum_of_indices(lst,[3,13,18,28,38])-sum_of_indices(lst,[8,23,33]))/(10)
def cal_openn(lst) : return(sum_of_indices(lst,[4,9,14,19,24,29,39,43])-sum_of_indices(lst,[34,40]))/(30)


@router.post("/submit_assessment/")
async def submit_assessment(assessment_answers: AssessmentAnswers):

    #make changes to user
    db = DatabaseConnection("Users")
    docId=db.find_id_by_attribute("user_id",assessment_answers.assessed_id)
    print(assessment_answers.assessed_id + "is the id ------------------------------------")
    document = db.get_document_by_id(docId)
    document.pop("_id", None)
    instance= User(**document)
    
    if(assessment_answers.user_id==assessment_answers.assessed_id):
        instance.self_answers=assessment_answers.answers  #set self_answers
        instance.attempts+=1
    else:
        instance.supervisor_answers=assessment_answers.answers  #set supervisor_answers

    db.replace_document_by_id(docId, instance.model_dump())
    print("record updated :"+docId)

    #check if supervisor has assessed
    if instance.supervisor_answers and instance.self_answers:
        print('both have assesed')
        Extraversion= round((cal_extro(instance.self_answers)*0.5+ cal_extro(instance.supervisor_answers)*0.5),2)*100
        Agreeableness= round((cal_agree(instance.self_answers)*0.5+ cal_agree(instance.supervisor_answers)*0.5),2)*100
        Conscientiousness= round((cal_consc(instance.self_answers)*0.5+ cal_consc(instance.supervisor_answers)*0.5),2)*100
        Neuroticism= round((cal_neuro(instance.self_answers)*0.5+ cal_neuro(instance.supervisor_answers)*0.5),2)*100
        Openness= round((cal_openn(instance.self_answers)*0.5+ cal_openn(instance.supervisor_answers)*0.5),2)*100
    elif instance.self_answers:
        print('both have not assesed')
        Extraversion= round(cal_extro(instance.self_answers)*0.5,2)*100
        Agreeableness= round(cal_agree(instance.self_answers)*0.5,2)*100
        Conscientiousness= round(cal_consc(instance.self_answers)*0.5,2)*100
        Neuroticism= round(cal_neuro(instance.self_answers)*0.5,2)*100
        Openness= round(cal_openn(instance.self_answers)*0.5,2)*100
         
        # save to results
    db = DatabaseConnection("Results")
    docId=db.find_id_by_attribute("user_id",assessment_answers.assessed_id)
    instance=Results(
            user_id= assessment_answers.assessed_id,  
            extraversion=Extraversion,
            agreeableness=Agreeableness,
            conscientiousness=Conscientiousness,             
            neuroticism=Neuroticism,
            openness=Openness
                )
    if docId:
        print("well doc is here") 
        db.replace_document_by_id(docId, instance.model_dump())
        print("record updated :"+docId)
    else:
        db.add_document(instance.model_dump())
        print("new record added :"+docId)
    
    return "done"

@router.get("/send_results/{userId}")
async def get_answers(userId :str):
    db = DatabaseConnection("Results")
    docId=db.find_id_by_attribute("user_id",userId)
    if docId:
        document = db.get_document_by_id(docId)
        document.pop("_id", None)
        response =Results(**document).model_dump()
        response.pop("user_id", None)
        print(response)
        return response
    
@router.get("/api/dual_assessment/{user_id}")
async def get_dual_assessment(user_id: str):
    db = DatabaseConnection("Users")
    docId=db.find_id_by_attribute("user_id",user_id)
    if(docId):
        document = db.get_document_by_id(docId)
        document.pop("_id", None)
        instance= User(**document)
        dual_assessment = False
        if(instance.supervisor_answers): #check if superviser assessed
            dual_assessment = True 

    return {"dual_assessment": dual_assessment}
#----------------------------------------------------------------------------------------------------------
@router.get("/get_answers")
async def get_answers():
    # Return the entire answers_db dictionary
    db = DatabaseConnection("Result")
    docId=db.find_id_by_attribute("user_id",'001')
    document = db.get_document_by_id(docId)

    if document:
        document.pop("_id", None)
        instance= User(**document)
        instance.user_id='002'
        db.replace_document_by_id(docId, instance.model_dump())
        return instance
    else: 
        print("not found")

@router.get("/add_record/{userID}/{name}")
async def create_document(userID,name):
    db = DatabaseConnection("Users")
    results_instance=User(
        user_id= userID,
        name=name,
        position="Senior Softweare Engineer",
        attempts= 0,
        supervisor= "001",
        requested= False,
        self_answers= None,
        supervisor_answers= None
        )
    print(results_instance)
    existing =db.find_id_by_attribute("user_id",userID)
    if existing:
        db.delete_document_by_id(existing)
    db.add_document(results_instance.model_dump()) 

@router.get("/add_record_authentication/{userID}/{name}")
async def create_document(userID,name):
    db = DatabaseConnection("Authentication")
    results_instance=User(
        user_id= userID,
        name=name,
        position="Senior Softweare Engineer",
        attempts= 0,
        supervisor= "001",
        requested= False,
        self_answers= None,
        supervisor_answers= None
        )
    print(results_instance)
    existing =db.find_id_by_attribute("user_id",userID)
    if existing:
        db.delete_document_by_id(existing)
    db.add_document(results_instance.model_dump())
