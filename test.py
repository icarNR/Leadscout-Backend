from fastapi import FastAPI, Path
from typing import Optional
from pydantic import BaseModel
app = FastAPI()

fighters={
    1:{
        "name":"jimmy rings",
        "age": 2
    }
}

class Fighter(BaseModel):
    name:str
    age:int

class UpdateFighter(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None

@app.get("/")
def index():
    return {"name":"first data"}  

@app.get("/get-student/{fighter_id}")
def get_student(fighter_id:int):
    if fighter_id not in fighters:
        return {"Data": "Not Found"}
    return fighters[fighter_id]

@app.get("/get-by-fname")
def get_student(*, fname: str, age: Optional[int]):
    for fighter_id in fighters:
        if fighters[fighter_id]["name"]==fname:
            return fighters[fighter_id]
        return {"Data": "Not Found"}

@app.post("/create-fighter/{f_id}")
def create_student(f_id: int, fighter: Fighter):
    if f_id in fighters:
        return {"Error":"Fighter exists"}
    fighters[f_id] = fighter
    return fighters[f_id]

@app.put("/update-fighter/{fighter_id}")
def update_student(fighter_id :int, fighter:UpdateFighter):
    if fighter_id not in fighters:
        return {"Error":"Who the fuck is that?"}
    
    if fighter.name !=None:
        fighters[fighter_id]["name"] = fighter.name

    if fighter.age !=None:
        fighters[fighter_id]["age"] = fighter.age
    
    return fighters[fighter_id]

@app.delete("/delete-fighter/{f-id}")
def delete_student(fid: int):
    if fid not in fighters:
        return {"Error":"Who?"}
    del fighters[fid]
    return {"Message":"Fighter Eliminated!"}