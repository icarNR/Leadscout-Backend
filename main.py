from routes.requestAssess import router as requestAssess_router
from routes.assessment import router as assessment_router
from fastapi import FastAPI
from crorSetting import setup_cors

# The rest of your FastAPI application code goes here


app = FastAPI()
setup_cors(app)
app.include_router(requestAssess_router)
app.include_router(assessment_router)