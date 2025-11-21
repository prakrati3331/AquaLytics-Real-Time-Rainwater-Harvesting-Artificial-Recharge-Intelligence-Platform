# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rwh import RainwaterHarvesting
from fastapi.responses import HTMLResponse
from file_handling import getAquifer, getRainfall, aquiferScore, getGroundWaterLevel

app = FastAPI(
    title="Rainwater Harvesting API",
    description="API for calculating rainwater harvesting feasibility",
    version="1.0.0"
)

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Input model
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>Rainwater Harvesting API</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; max-width: 800px; margin: 0 auto; }
                h1 { color: #2c3e50; }
                .endpoint { 
                    background: #f8f9fa; 
                    padding: 15px; 
                    border-radius: 5px; 
                    margin: 20px 0; 
                    border-left: 4px solid #3498db;
                }
                code { 
                    background: #e9ecef; 
                    padding: 2px 5px; 
                    border-radius: 3px; 
                    font-family: monospace;
                }
                .method { 
                    display: inline-block; 
                    background: #3498db; 
                    color: white; 
                    padding: 2px 8px; 
                    border-radius: 3px; 
                    margin-right: 10px;
                    font-weight: bold;
                    font-size: 0.9em;
                }
            </style>
        </head>
        <body>
            <h1>🌧️ Rainwater Harvesting API</h1>
            <p>Welcome to the Rainwater Harvesting Feasibility API. Use the following endpoint to check feasibility:</p>
            
            <div class="endpoint">
                <div><span class="method">POST</span> <code>/process-location</code></div>
                <p>Check the feasibility of rainwater harvesting for a specific location.</p>
                <h4>Request Body:</h4>
                <pre>{
  "district": "string",
  "state": "string",
  "roofArea": 0,
  "roofType": "string",
  "dwellers": 0
}</pre>
                <p><strong>Note:</strong> You can test this endpoint using tools like Postman or curl.</p>
            </div>
            
            <p>For detailed API documentation, visit <a href="/docs">/docs</a> or <a href="/redoc">/redoc</a>.</p>
        </body>
    </html>
    """

class RWHRequest(BaseModel):
    district: str
    state: str
    roofArea: float
    roofType: str
    dwellers: int

@app.post("/process-location")
def process_location(data: RWHRequest):
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

    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except FileNotFoundError as fe:
        raise HTTPException(status_code=500, detail=str(fe))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")
