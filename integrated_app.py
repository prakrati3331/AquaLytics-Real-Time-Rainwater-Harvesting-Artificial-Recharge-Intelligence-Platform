from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import pandas as pd
import numpy as np
import joblib
import os
import uuid
import glob
from typing import Dict
from pathlib import Path

# Initialize FastAPI app
app = FastAPI(
    title="Integrated Water Resource Management System",
    description="Combined Rainwater Harvesting and Aquifer Analysis System",
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

# Import custom modules
from rwh import RainwaterHarvesting
from file_handling import getAquifer, getRainfall, aquiferScore, getGroundWaterLevel
from SVGcoloring import rainfallColoring, postMonsoonColoring, preMonsoonColoring, aquiferColoring, highlightBorder

# Load aquifer model and encoders
MODEL_PATH = "aquifer_recommendation_model.pkl"
model_loaded = False

try:
    model_data = joblib.load(MODEL_PATH)
    aquifer_model = model_data['model']
    scaler = model_data['scaler']
    label_encoder = model_data['label_encoder']
    target_encoder = model_data['target_encoder']
    features = model_data['features']
    model_loaded = True
except FileNotFoundError:
    print(f"Warning: Aquifer model file '{MODEL_PATH}' not found. Aquifer prediction features will be disabled.")
    aquifer_model = None
    scaler = None
    label_encoder = None
    target_encoder = None
    features = []

# Request/Response Models for Rainwater Harvesting
class RWHRequest(BaseModel):
    district: str
    state: str
    roofArea: float
    roofType: str
    dwellers: int

# Request/Response Models for Aquifer Prediction
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

# Helper function for range conversion
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

# Helper function for SVG generation
def createSVGs(districtName, stateName):
    uid = uuid.uuid4()
    state_code_map = {
        "ANDHRA PRADESH": "AP", "ARUNACHAL PRADESH": "AR", "ASSAM": "AS", "BIHAR": "BR",
        "CHHATTISGARH": "CG", "GOA": "GA", "GUJARAT": "GJ", "HARYANA": "HR",
        "HIMACHAL PRADESH": "HP", "JAMMU & KASHMIR": "JK", "LADAKH": "LA", "JHARKHAND": "JH",
        "KARNATAKA": "KA", "KERALA": "KL", "MADHYA PRADESH": "MP", "MAHARASHTRA": "MH",
        "MANIPUR": "MN", "MEGHALAYA": "ML", "MIZORAM": "MZ", "NAGALAND": "NL",
        "ODISHA": "OD", "PUNJAB": "PB", "RAJASTHAN": "RJ", "SIKKIM": "SK",
        "TAMIL NADU": "TN", "TELANGANA": "TG", "TRIPURA": "TR", "UTTAR PRADESH": "UP",
        "UTTARAKHAND": "UK", "WEST BENGAL": "WB", "DELHI": "DL", "CHANDIGARH": "CH",
        "PUDUCHERRY": "PY", "DAMAN & DIU": "DD", "ANDAMAN & NICOBAR": "AN"
    }
    stateCode = state_code_map.get(f"{stateName.upper()}", stateName.upper()[:2])

    try:
        rainfallColoring(stateCode,)
        preMonsoonColoring(stateCode)
        postMonsoonColoring(stateCode)
        aquiferColoring()
        highlightBorder(districtName, "postmonsoon.svg")
        highlightBorder(districtName, "premonsoon.svg")
        highlightBorder(districtName, "rainfall.svg")
        highlightBorder(stateCode, "aquifer_map.svg")
    except Exception as e:
        print(f"SVG generation warning: {e}")

# Main Routes (from app.py)
@app.get("/")
def serve_index():
    """Serve the main web interface"""
    file_path = os.path.join("static", "newindex.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"message": "Integrated Water Resource Management System is running"}

@app.post("/process-location")
def process_location(data: RWHRequest):
    """Process rainwater harvesting feasibility"""
    try:
        # Fetch data
        rainfall = getRainfall(data.district, data.state)
        aquifer = getAquifer(data.district, data.state)
        score = aquiferScore(aquifer)
        gw_pre, gw_post = getGroundWaterLevel(data.district, data.state)

        # Calculate RWH
        user_rwh = RainwaterHarvesting(
            roofArea=data.roofArea,
            roofType=data.roofType,
            rainfallMM=rainfall,
            dwellers=data.dwellers
        )

        feasibility = user_rwh.feasibility(gw_pre, gw_post, score)

        # Generate SVGs
        try:
            createSVGs(data.district, data.state)
        except Exception as e:
            print("SVG generation failed:", e)

        response = {
            "district": data.district,
            "state": data.state,
            "roofArea": data.roofArea,
            "roofType": data.roofType,
            "dwellers": data.dwellers,
            "aquiferType": aquifer,
            "aquiferScore": score,
            "groundwaterPreMonsoon": gw_pre,
            "groundwaterPostMonsoon": gw_post,
            "rainfallMM": rainfall,
            "annualDemandLiters": user_rwh.annualDemand(),
            "harvestedWaterLiters": user_rwh.harvestedWaterFromRoof(),
            "feasibilityScore": feasibility
        }

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/groundwater-trends")
def groundwater_trends():
    """Get historical groundwater level trends"""
    allFiles = glob.glob("databases\\groundwater*.csv")
    fileList = [pd.read_csv(f) for f in allFiles]
    groundwater = pd.concat(fileList, ignore_index=True)
    trend_data = {}
    for district, group in groundwater.groupby("District"):
        group_sorted = group.sort_values("Year")
        trend_data[district] = {
            "Pre_Monsoon": group_sorted[["Year","Pre_Monsoon"]].values.tolist(),
            "Post_Monsoon": group_sorted[["Year","Post_Monsoon"]].values.tolist()
        }
    return trend_data

# Aquifer Prediction Routes (from aquifier_main.py)
@app.get("/aquifer")
def aquifer_root(request: Request):
    """Serve aquifer prediction interface"""
    file_path = os.path.join("static", "aquifer_interface.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    if templates:
        return templates.TemplateResponse("index.html", {"request": request})
    return {"message": "Aquifer Type Recommendation System is running"}

@app.get("/aquifer-analysis")
def aquifer_analysis_page(request: Request):
    """Serve advanced aquifer analysis interface"""
    file_path = os.path.join("static", "aquifer_prediction.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"message": "Advanced Aquifer Analysis System is running"}

@app.get("/aquifer/status")
def aquifer_api_status():
    """Get aquifer API status"""
    return {
        "message": "Aquifer Type Recommendation API",
        "status": "running",
        "model_loaded": model_loaded
    }

@app.post("/aquifer/predict", response_model=AquiferPredictionResponse)
def predict_aquifer(data: AquiferPredictionRequest):
    """Predict aquifer type based on input parameters"""
    if not model_loaded or aquifer_model is None:
        raise HTTPException(status_code=503, detail="Aquifer model not loaded. Please check the server logs.")

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
        prediction_encoded = aquifer_model.predict(input_scaled)
        prediction = target_encoder.inverse_transform(prediction_encoded)[0]

        # Get probabilities
        probabilities = aquifer_model.predict_proba(input_scaled)[0]
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

@app.get("/aquifer/features")
def get_aquifer_features():
    """Get aquifer model features"""
    if not model_loaded:
        raise HTTPException(status_code=503, detail="Aquifer model not loaded")
    return {"features": features}

@app.get("/aquifer/classes")
def get_aquifer_classes():
    """Get possible aquifer classes"""
    if not model_loaded:
        raise HTTPException(status_code=503, detail="Aquifer model not loaded")
    return {"classes": list(target_encoder.classes_)}

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "rainwater_harvesting": "active",
            "aquifer_prediction": "active" if model_loaded else "inactive"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
