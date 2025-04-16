from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random
import string

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

@app.get("/generate-code")
def generate_code():
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return {"code": code}

