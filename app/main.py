from app.routes.requestAssess import router as requestAssess_router
from app.routes.assessment import router as assessment_router
from app.routes.notifications import router as notification_router
from app.routes.authentication import router as authentication_router
from app.routes.otp import router as otp_router
from fastapi import FastAPI
from crorSetting import setup_cors

# The rest of your FastAPI application code goes here


app = FastAPI()
setup_cors(app)
# app.include_router(requestAssess_router)
# app.include_router(assessment_router)
app.include_router(notification_router)
app.include_router(authentication_router)
app.include_router(otp_router)