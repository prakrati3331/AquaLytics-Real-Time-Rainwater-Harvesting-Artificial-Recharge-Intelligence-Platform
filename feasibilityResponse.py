from bs4 import BeautifulSoup

with open("maps\\MP.svg", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "xml")

# Find the Bhopal path
bhopal = soup.find("path", {"id": "Indore"})

# Change its color (e.g., red)
if bhopal:
    bhopal["fill"] = "#ff0000"   # red
    bhopal["stroke"] = "#000000" # black border for clarity

# Save new SVG
svg_tag = soup.find("svg")
if svg_tag and not svg_tag.has_attr("xmlns"):
    svg_tag["xmlns"] = "http://www.w3.org/2000/svg"


with open("madhyapradesh_colored.svg", "w", encoding="utf-8") as f:
    f.write(soup.decode())
