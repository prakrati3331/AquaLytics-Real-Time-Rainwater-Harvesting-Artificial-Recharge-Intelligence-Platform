import pandas as pd
from bs4 import BeautifulSoup
import os

# ---------------- Rainfall Classification ----------------
def classifyRainfall(mm):
    if pd.isna(mm) or mm <= 0:
        return "*"
    elif mm > 1500:
        return "LE"
    elif mm > 1000:
        return "E"
    elif mm > 700:
        return "N"
    elif mm > 400:
        return "D"
    else:
        return "LD"
    
def rainfallColoring(stateName,outputDir="static"):
    outputFile = os.path.join(outputDir, f"rainfall.svg")
    df = pd.read_csv("databases\\rainfall_database.csv")
    df["SvgCat"] = df["NORMAL"].apply(classifyRainfall)

    categoryColors = {
        "LE": "#08306b", "E": "#2171b5", "N": "#6baed6",
        "D": "#9ecae1", "LD": "#c6dbef", "*": "#f2f2f2"
    }

    with open(f"maps\\{stateName}.svg", "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml-xml")
    if not soup.find("svg").has_attr("xmlns"):
        soup.find("svg")["xmlns"] = "http://www.w3.org/2000/svg"

    df["NAME"] = df["NAME"].str.strip().str.upper()
    for _, row in df.iterrows():
        district = row["NAME"]
        cat = str(row["SvgCat"]).strip()
        color = categoryColors.get(cat, "#ffffff")
        for path in soup.find_all("path"):
            if path.get("id", "").strip().upper() == district:
                path["fill"] = color
                path["stroke"] = "#000000"
                path["stroke-width"] = "0.75"
                break

    with open(outputFile, "w", encoding="utf-8") as f:
        f.write(str(soup))
    return outputFile

def preMonsoonColoring(stateName,outputDir="static"):
    outputFile = os.path.join(outputDir, f"premonsoon.svg")
    df = pd.read_csv("databases\\groundwater2023.csv")
    categoryColors = {
        "0 to 2": "#ffffcc", "2 to 5": "#ffeda0", "5 to 10": "#fed976",
        "10 to 20": "#feb24c", "20 to 40": "#fd8d3c", ">40": "#e31a1c"
    }

    with open(f"maps\\{stateName}.svg", "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml-xml")
    if not soup.find("svg").has_attr("xmlns"):
        soup.find("svg")["xmlns"] = "http://www.w3.org/2000/svg"

    df["District"] = df["District"].str.strip().str.upper()
    for _, row in df.iterrows():
        district = row["District"]
        cat = str(row["Pre_Monsoon"]).strip()
        color = categoryColors.get(cat, "#ffffff")
        for path in soup.find_all("path"):
            if path.get("id", "").strip().upper() == district:
                path["fill"] = color
                path["stroke"] = "#000000"
                path["stroke-width"] = "0.75"
                break

    with open(outputFile, "w", encoding="utf-8") as f:
        f.write(str(soup))
    return outputFile

def postMonsoonColoring(stateName,outputDir="static"):
    outputFile = os.path.join(outputDir, f"postmonsoon.svg")
    df = pd.read_csv("databases\\groundwater2023.csv")
    categoryColors = {
        "0 to 2": "#00441b", "2 to 5": "#006d2c", "5 to 10": "#238b45",
        "10 to 20": "#41ab5d", "20 to 40": "#74c476", ">40": "#c7e9c0"
    }

    with open(f"maps\\{stateName}.svg", "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml-xml")
    if not soup.find("svg").has_attr("xmlns"):
        soup.find("svg")["xmlns"] = "http://www.w3.org/2000/svg"

    df["District"] = df["District"].str.strip().str.upper()
    for _, row in df.iterrows():
        district = row["District"]
        cat = str(row["Pre_Monsoon"]).strip()
        color = categoryColors.get(cat, "#ffffff")
        for path in soup.find_all("path"):
            if path.get("id", "").strip().upper() == district:
                path["fill"] = color
                path["stroke"] = "#000000"
                path["stroke-width"] = "0.75"
                break

    with open(outputFile, "w", encoding="utf-8") as f:
        f.write(str(soup))
    return outputFile

def aquiferColoring(outputDir="static"):
    outputFile = os.path.join(outputDir, f"aquiferMap.svg")
    df = pd.read_csv("databases\\statewise_aquifier.csv")
    aquiferColors = {
        "ALLUVIUM": "#FFF3B0", "SANDSTONE": "#A3C4F3", "BASALT": "#B9FBC0",
        "CRYSTALLINE": "#FFADAD", "LIMESTONE": "#D7BDE2", "OTHER": "#E6B8A2"
    }
    stateCodeMap = {
        "ANDHRA PRADESH": "AP","ARUNACHAL PRADESH": "AR","ASSAM": "AS","BIHAR": "BR",
        "CHHATTISGARH": "CG","GOA": "GA","GUJARAT": "GJ","HARYANA": "HR",
        "HIMACHAL PRADESH": "HP","JAMMU & KASHMIR": "JK","LADAKH": "LA","JHARKHAND": "JH",
        "KARNATAKA": "KA","KERALA": "KL","MADHYA PRADESH": "MP","MAHARASHTRA": "MH",
        "MANIPUR": "MN","MEGHALAYA": "ML","MIZORAM": "MZ","NAGALAND": "NL","ODISHA": "OD",
        "PUNJAB": "PB","RAJASTHAN": "RJ","SIKKIM": "SK","TAMIL NADU": "TN","TELANGANA": "TG",
        "TRIPURA": "TR","UTTAR PRADESH": "UP","UTTARAKHAND": "UK","WEST BENGAL": "WB",
        "DELHI": "DL","CHANDIGARH": "CH","PUDUCHERRY": "PY","DAMAN & DIU": "DD",
        "ANDAMAN & NICOBAR": "AN"
    }

    with open("maps\\INDIA.svg", "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml-xml")

    for _, row in df.iterrows():
        state = row["State"].strip().upper()
        aquifer = row["Dominant_Aquifer_Type"].upper()
        stateCode = stateCodeMap.get(state)
        if not stateCode: continue
        aquiferMain = next((k for k in aquiferColors if k in aquifer), "OTHER")
        color = aquiferColors[aquiferMain]
        path = soup.find("path", {"id": stateCode})
        if path:
            path["fill"] = color
            path["stroke"] = "#000000"
            path["stroke-width"] = "0.75"

    if not soup.find("svg").has_attr("xmlns"):
        soup.find("svg")["xmlns"] = "http://www.w3.org/2000/svg"

    with open(outputFile, "w", encoding="utf-8") as f:
        f.write(str(soup))
    return outputFile

# ---------------- Highlight Border ----------------
def highlightBorder(name, inputFile, outputDir="static"):
    baseName = os.path.splitext(os.path.basename(inputFile))[0]
    outputFile = os.path.join(outputDir, f"{baseName}.svg")

    with open(inputFile, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml-xml")

    path = soup.find("path", {"id": name})
    if path:
        path["stroke"] = "#FF00FF"
        path["stroke-width"] = "2.6"

    with open(outputFile, "w", encoding="utf-8") as f:
        f.write(str(soup))
    return outputFile
