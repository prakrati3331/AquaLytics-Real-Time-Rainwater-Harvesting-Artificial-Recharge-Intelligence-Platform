import pandas as pd
import re

# Load databases
rainfallData = pd.read_csv('databases\\rainfall_database.csv')
stateAquiferData = pd.read_csv('databases\\statewise_aquifier.csv')
aquiferScores = pd.read_csv('databases\\aquifer_score.csv')
aquiferScores['Aquifer_Type'] = aquiferScores['Aquifer_Type'].str.upper()
groundwaterData = pd.read_csv('databases\\groundwater2023.csv')


# Used for Rainfall
def getRainfall(districtName, stateName):
    search_keys = [districtName, stateName]
    for key in search_keys:
        if not key:
            continue
        row = rainfallData[rainfallData['NAME'].str.upper() == key.upper()]
        if not row.empty:
            return float(row.iloc[0]['NORMAL'])
        row = rainfallData[rainfallData['NAME'].str.upper().str.contains(key.upper(), na=False)]
        if not row.empty:
            return float(row.iloc[0]['NORMAL'])
    raise ValueError(f"Rainfall data for {districtName}, {stateName} not available.")


# Used for Aquifer
def getAquifer(districtName, stateName):
    search_keys = [districtName, stateName]
    for key in search_keys:
        if not key:
            continue
        row = stateAquiferData[stateAquiferData['State'].str.upper() == key.upper()]
        if not row.empty:
            return row.iloc[0]['Dominant_Aquifer_Type']
        row = stateAquiferData[stateAquiferData['State'].str.upper().str.contains(key.upper(), na=False)]
        if not row.empty:
            return row.iloc[0]['Dominant_Aquifer_Type']
    raise ValueError(f"Aquifer data for {districtName}, {stateName} not available.")


# Used to return the GroundWaterLevel
def getGroundWaterLevel(districtName, stateName):
    row = groundwaterData[groundwaterData['District'].str.upper() == districtName.upper()]
    if not row.empty:
        return str(row.iloc[0]['Pre_Monsoon']), str(row.iloc[0]['Post_Monsoon'])
    
    row = groundwaterData[groundwaterData['District'].str.upper().str.contains(districtName.upper(), na=False)]
    if not row.empty:
        return str(row.iloc[0]['Pre_Monsoon']), str(row.iloc[0]['Post_Monsoon'])
    
    row = groundwaterData[groundwaterData['State'].str.upper() == stateName.upper()]
    if not row.empty:
        return str(row.iloc[0]['Pre_Monsoon']), str(row.iloc[0]['Post_Monsoon'])
    
    row = groundwaterData[groundwaterData['State'].str.upper().str.contains(stateName.upper(), na=False)]
    if not row.empty:
        return str(row.iloc[0]['Pre_Monsoon']), str(row.iloc[0]['Post_Monsoon'])
    
    raise ValueError(f"GroundWaterLevel data for {districtName}, {stateName} not available.")


def parseDepth(groundWaterLevel):
    if 'to' in groundWaterLevel:
        lo, hi = [float(x.strip()) for x in groundWaterLevel.split('to')]
    elif '>' in groundWaterLevel:
        lo, hi = float(groundWaterLevel.replace('>', '').strip()), float('inf')
    else:
        lo = 6
        hi = 8
    mid = (lo + (hi if hi != float('inf') else lo)) / 2.0
    return hi


# Aquifer score mapping
aquifer_scores = {
    "Alluvium": 5,
    "Limestone": 5,
    "Sandstone": 4,
    "Basalt": 3,
    "Schist": 3,
    "Laterite": 3,
    "Khondalite": 3,
    "Granite": 2,
    "Gneiss": 2,
    "Basement Gneiss": 2,
    "Shale": 2,
    "Quartzite": 2,
    "Intrusive": 2
}


def aquiferScore(aquifer_str):
    parts = aquifer_str.split(',')
    
    majority = []
    secondary = []
    plain = []

    for p in parts:
        p_clean = p.strip()
        base = re.sub(r"\(.*?\)", "", p_clean).strip()

        if "majority" in p_clean.lower() or "dominant" in p_clean.lower() or "major" in p_clean.lower():
            majority.append(base)
        elif "some" in p_clean.lower() or "part" in p_clean.lower():
            secondary.append(base)
        else:
            plain.append(base)

    if majority:
        return aquifer_scores.get(majority[0], "Unknown")
    elif plain:
        return max(aquifer_scores.get(a, 0) for a in plain)
    elif secondary:
        return max(aquifer_scores.get(a, 0) for a in secondary)
    else:
        return "Unknown"
