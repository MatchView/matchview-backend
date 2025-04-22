from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random
import string
import json
import os
import requests

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust to your frontend domain for production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Home endpoint
@app.get("/")
def home():
    return {"message": "Welcome to Matchview backend!"}

# Endpoint to generate unique prediction code
@app.get("/generate-code")
def generate_code():
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return {"code": code}

# Endpoint to login with an existing code (or create it if new)
@app.get("/login-code")
def login_code(code: str):
    data_file = "app/data.json"

    # If file doesn't exist, create it
    if not os.path.exists(data_file):
        with open(data_file, "w") as f:
            json.dump({}, f)

    # Load existing data
    with open(data_file, "r") as f:
        data = json.load(f)

    # If code not in data, add it
    if code not in data:
        data[code] = {"predictions": []}
        with open(data_file, "w") as f:
            json.dump(data, f, indent=4)
        return {"message": f"New code created: {code}"}

    # If code exists, confirm login
    return {"message": f"Code {code} logged in successfully"}

# New: Fixtures and odds endpoint (with 1xBet odds, multiplied by 2)
@app.get("/fixtures")
def get_fixtures():
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures?league=39&season=2025"  # adjust league if needed
    odds_url_template = "https://api-football-v1.p.rapidapi.com/v3/odds?fixture={}"

    headers = {
        "X-RapidAPI-Key": "85a7bcac59msh6ae91a3600dcc27p198072jsn4abf45d50cff",  # Replace with your actual API key
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)
    fixtures = response.json()["response"]

    final_data = []

    for fixture in fixtures:
        fixture_id = fixture["fixture"]["id"]
        home_team = fixture["teams"]["home"]["name"]
        away_team = fixture["teams"]["away"]["name"]

        odds_response = requests.get(odds_url_template.format(fixture_id), headers=headers)
        odds_data = odds_response.json()["response"]

        points = {"home": None, "draw": None, "away": None}

        for item in odds_data:
            for bookmaker in item.get("bookmakers", []):
                if bookmaker["name"] == "1xBet":
                    for bet in bookmaker["bets"]:
                        if bet["name"] == "Match Winner":
                            for val in bet["values"]:
                                if val["value"] == "Home":
                                    points["home"] = round(float(val["odd"]) * 2, 2)
                                elif val["value"] == "Draw":
                                    points["draw"] = round(float(val["odd"]) * 2, 2)
                                elif val["value"] == "Away":
                                    points["away"] = round(float(val["odd"]) * 2, 2)
                    break  # Stop after 1xBet
            break  # Stop after first item

        final_data.append({
            "fixture_id": fixture_id,
            "home": home_team,
            "away": away_team,
            "points": points
        })

    return final_data
