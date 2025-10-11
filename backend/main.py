import os
import io
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
app = FastAPI(title="AI Health Backend")

# Allow Streamlit access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini client


# Pydantic model
class HealthProfile(BaseModel):
    age: int
    gender: str
    height: float
    weight: float
    goal: str
    allergies: str
    fitness_level: str

# --- Meal Plan Endpoint ---
@app.post("/generate_meal_plan/")
async def generate_meal_plan(profile: HealthProfile):
    try:
        prompt = f"""
        Create a personalized 1-day meal plan for:
        Age: {profile.age}, Gender: {profile.gender}, Height: {profile.height} cm, Weight: {profile.weight} kg.
        Goal: {profile.goal}, Allergies: {profile.allergies}, Fitness Level: {profile.fitness_level}.
        Include calories, macros, and meal timings.
        """
        model = genai.GenerativeModel("models/gemini-2.5-pro")
        response = model.generate_content(prompt)
        return {"meal_plan": response.text}
    except Exception as e:
        return {"meal_plan": None, "error": str(e)}

# --- Food Analysis Endpoint ---
@app.post("/analyze_food/")
async def analyze_food(file: UploadFile = File(...)):
    try:
        image = Image.open(io.BytesIO(await file.read()))
        model = genai.GenerativeModel("models/gemini-2.5-pro")
        response = model.generate_content(
            ["Analyze this food image. Describe food name, calories, and nutrition details.", image]
        )
        return {"food_analysis": response.text}
    except Exception as e:
        return {"food_analysis": None, "error": str(e)}

# --- Health Query Endpoint ---
@app.post("/health_query/")
async def health_query(query: str = Form(...)):
    try:
        model = genai.GenerativeModel("models/gemini-2.5-pro")
        response = model.generate_content(f"Answer this health question scientifically: {query}")
        return {"answer": response.text}
    except Exception as e:
        return {"answer": None, "error": str(e)}
