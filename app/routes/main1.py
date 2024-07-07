import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Retrieve API key from environment variables
api_key = os.getenv("GEMINI_API_KEY")
if api_key is None:
    logger.error("GEMINI_API_KEY not found in environment variables.")
    raise ValueError("GEMINI_API_KEY not found in environment variables.")

# Configure GenAI
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# FastAPI application instance
app = FastAPI()

# Pydantic models
class Question(BaseModel):
    question: str

class PersonalityQualities(BaseModel):
    Neuroticism: float = Field(..., gt=0, le=1, description="Neuroticism score must be between 0 and 1.")
    Extraversion: float = Field(..., gt=0, le=1, description="Extraversion score must be between 0 and 1.")
    Openness_to: float = Field(..., gt=0, le=1, description="Openness score must be between 0 and 1.")
    Agreeableness: float = Field(..., gt=0, le=1, description="Agreeableness score must be between 0 and 1.")
    Conscientiousness: float = Field(..., gt=0, le=1, description="Conscientiousness score must be between 0 and 1.")
    strength_and_weakness: str = Field(..., description="Details about strengths and weaknesses")

# Routes and endpoint handlers
@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the GenAI Q&A API. Use the /ask endpoint to ask questions."}

@app.post("/ask")
async def ask_question(question: Question):
    logger.info(f"Received question: {question.question}")
    try:
        # Extracting the marks and job position from the question
        question_data = question.question.split(',')
        scores = {item.split('=')[0].strip(): float(item.split('=')[1].strip()) for item in question_data[:-1]}
        job_position = question_data[-1].split('=')[1].strip()
        
        # Modify the question before sending it to Gemini AI
        modified_question = (f"Generate personalized guidance for an employee based on their Big Five personality trait scores and job role. The scores are provided on a scale from 0 to 1. Use the scores to create recommendations in the following areas: possible struggles or challenges they face specific to their job roles, and how to overcaome them, tips to improve using their strength '{job_position}': "
                             f"Neuroticism={scores['Neuroticism']}, Extraversion={scores['Extraversion']}, "
                             f"Openness to Experience={scores['Openness_to']}, Agreeableness={scores['Agreeableness']}, "
                             f"Conscientiousness={scores['Conscientiousness']}, Use these scores to provide comprehensive and tailored advice, ensuring the guidance is highly personalized and unique for the employee.i want to have this structure of output challanges and howtoovercome strenghths and tips to improve.spesifi output related to job role.")
        logger.info(f"Modified question: {modified_question}")
        
        response = model.generate_content(modified_question)
        logger.info(f"Response from GenAI: {response.text}")
        
        # Process and format the response as required
        formatted_response = {
            "message": "Here is the assessment result:",
            "response": response.text.strip()
        }
        
        return formatted_response
    except Exception as e:
        logger.error(f"Failed to fetch answer from GenAI: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch answer from GenAI: {str(e)}")

@app.post("/improvement")
async def get_improvement(personality: PersonalityQualities):
    logger.info(f"Received personality qualities and marks: {personality.dict()}")

    # Example logic to generate improvement suggestions
    suggestions = []
    if personality.Neuroticism > 0.20:
        suggestions.append("Consider techniques to manage neuroticism.")
    if personality.Extraversion < 0.30:
        suggestions.append("Enhance extraversion skills for better interaction.")
    if personality.Openness_to < 0.25:
        suggestions.append("Explore opportunities to increase openness.")
    if personality.Agreeableness < 0.10:
        suggestions.append("Work on agreeableness for better teamwork.")
    if personality.Conscientiousness < 0.30:
        suggestions.append("Develop conscientiousness for improved productivity.")

    logger.info(f"Generated improvement suggestions: {suggestions}")

    return {"suggestions": suggestions}
