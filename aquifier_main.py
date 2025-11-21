from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import pandas as pd
import numpy as np
import joblib
import os
from typing import Dict
from pathlib import Path

# Initialize FastAPI app
app = FastAPI(
    title="Aquifer Type Recommendation System",
    description="Web application for predicting aquifer types based on geological and hydrological features",
    version="1.0.0"
)

# Set up base dir
BASE_DIR = Path(__file__).resolve().parent

# Check for templates and static folders
templates = None
if (BASE_DIR / "templates").exists():
    templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

if (BASE_DIR / "static").exists():
    app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model and encoders
MODEL_PATH = "aquifer_recommendation_model.pkl"

try:
    model_data = joblib.load(MODEL_PATH)
    model = model_data['model']
    scaler = model_data['scaler']
    label_encoder = model_data['label_encoder']
    target_encoder = model_data['target_encoder']
    features = model_data['features']
except FileNotFoundError:
    print(f"Error: Model file '{MODEL_PATH}' not found.")
    model_loaded = False
else:
    model_loaded = True

# Request/Response Models
class AquiferPredictionRequest(BaseModel):
    state: str
    district: str
    pre_monsoon: str
    post_monsoon: str
    fluctuation: float
    elevation: float
    actual_rainfall: float
    normal_rainfall: float
    percent_dep: float

class AquiferPredictionResponse(BaseModel):
    prediction: str
    probabilities: Dict[str, float]

# Helper function
def range_to_midpoint(range_str: str) -> float:
    if not range_str or pd.isna(range_str):
        return np.nan
    if 'to' in range_str:
        parts = range_str.split('to')
        try:
            low = float(parts[0].strip())
            high = float(parts[1].strip())
            return (low + high) / 2
        except (ValueError, IndexError):
            return np.nan
    elif '>' in range_str:
        try:
            value = float(range_str.replace('>', '').strip())
            return value + 5  # Assume >40 means ~45
        except ValueError:
            return np.nan
    else:
        try:
            return float(range_str)
        except ValueError:
            return np.nan

# Frontend route
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    if templates:
        return templates.TemplateResponse("index.html", {"request": request})
    return {"message": "Aquifer Type Recommendation API is running"}

# API endpoints
@app.get("/api/status")
async def api_status():
    return {
        "message": "Aquifer Type Recommendation API",
        "status": "running",
        "model_loaded": model_loaded
    }

@app.post("/predict", response_model=AquiferPredictionResponse)
async def predict_aquifer(data: AquiferPredictionRequest):
    if not model_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded. Please check the server logs.")
    
    try:
        # Encode state and district
        try:
            state_encoded = int(label_encoder.transform([data.state])[0])
        except:
            state_encoded = 0

        try:
            district_encoded = int(label_encoder.transform([data.district])[0])
        except:
            district_encoded = 0

        # Prepare input data
        input_data = {
            'Pre_Monsoon_mid': range_to_midpoint(data.pre_monsoon),
            'Post_Monsoon_mid': range_to_midpoint(data.post_monsoon),
            'Fluctuation': data.fluctuation,
            'Elevation (m)': data.elevation,
            'ACTUAL (mm)': data.actual_rainfall,
            'NORMAL (mm)': data.normal_rainfall,
            '% DEP.': data.percent_dep,
            'State_encoded': state_encoded,
            'District_encoded': district_encoded
        }

        # Create DataFrame and handle missing values
        input_df = pd.DataFrame([input_data])
        input_df = input_df.fillna(input_df.mean())

        # Scale features
        input_scaled = scaler.transform(input_df)

        # Make prediction
        prediction_encoded = model.predict(input_scaled)
        prediction = target_encoder.inverse_transform(prediction_encoded)[0]

        # Get probabilities
        probabilities = model.predict_proba(input_scaled)[0]
        probability_dict = {
            target: float(prob)
            for target, prob in zip(target_encoder.classes_, probabilities)
        }

        return {
            "prediction": prediction,
            "probabilities": probability_dict
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/features")
async def get_features():
    if not model_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"features": features}

@app.get("/classes")
async def get_classes():
    if not model_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"classes": list(target_encoder.classes_)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
