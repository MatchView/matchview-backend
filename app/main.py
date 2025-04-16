from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random
import string
import json
import os

app = FastAPI()

# CORS setup (this is important so your frontend on GitHub Pages can access the backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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
