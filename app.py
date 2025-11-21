from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import uuid
from pydantic import BaseModel
from rwh import RainwaterHarvesting
from file_handling import getAquifer, getRainfall, aquiferScore, getGroundWaterLevel
from SVGcoloring import rainfallColoring, postMonsoonColoring,preMonsoonColoring,aquiferColoring, highlightBorder
import pandas as pd
import glob

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RWHRequest(BaseModel):
    district: str
    state: str
    roofArea: float
    roofType: str
    dwellers: int

def createSVGs(districtName,stateName):
    uid = uuid.uuid4()
    state_code_map = {
        "ANDHRA PRADESH": "AP",
        "ARUNACHAL PRADESH": "AR",
        "ASSAM": "AS",
        "BIHAR": "BR",
        "CHHATTISGARH": "CG",
        "GOA": "GA",
        "GUJARAT": "GJ",
        "HARYANA": "HR",
        "HIMACHAL PRADESH": "HP",
        "JAMMU & KASHMIR": "JK",
        "LADAKH": "LA",
        "JHARKHAND": "JH",
        "KARNATAKA": "KA",
        "KERALA": "KL",
        "MADHYA PRADESH": "MP",
        "MAHARASHTRA": "MH",
        "MANIPUR": "MN",
        "MEGHALAYA": "ML",
        "MIZORAM": "MZ",
        "NAGALAND": "NL",
        "ODISHA": "OD",
        "PUNJAB": "PB",
        "RAJASTHAN": "RJ",
        "SIKKIM": "SK",
        "TAMIL NADU": "TN",
        "TELANGANA": "TG",
        "TRIPURA": "TR",
        "UTTAR PRADESH": "UP",
        "UTTARAKHAND": "UK",
        "WEST BENGAL": "WB",
        "DELHI": "DL",
        "CHANDIGARH": "CH",
        "PUDUCHERRY": "PY",
        "DAMAN & DIU": "DD",
        "ANDAMAN & NICOBAR": "AN"
    }
    stateCode = state_code_map[f"{stateName.upper()}"]
    
    rainfallColoring(stateCode,)
    preMonsoonColoring(stateCode)
    postMonsoonColoring(stateCode)
    aquiferColoring()
    highlightBorder(districtName,"postmonsoon.svg")
    highlightBorder(districtName,"premonsoon.svg")
    highlightBorder(districtName,"rainfall.svg")
    highlightBorder(stateCode,"aquifer_map.svg")
    return


@app.get("/groundwater-trends")
def groundwater_trends():
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



@app.get("/")
def serve_index():
    file_path = os.path.join("static", "newindex.html")
    return FileResponse(file_path)

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

        try:
            createSVGs(data.district,data.state)
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
        return {"error": str(e)}
