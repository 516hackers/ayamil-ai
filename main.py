from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId
from dotenv import load_dotenv
import os

# Import your modules (make sure they exist and are correct)
from db import users, businesses, chats
from schemas import SignupIn, LoginIn, BusinessTrainIn, ChatIn
from auth import hash_password, verify_password, create_access_token, decode_token
from ai_engine import generate_reply

load_dotenv()

app = FastAPI(title='Ayamil Coders AI - Backend')

# CORS settings
origins = os.getenv('CORS_ORIGINS', '*')
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origins] if origins != '*' else ['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# -------------------------
# Signup Endpoint
# -------------------------
@app.post("/signup")
async def signup(data: SignupIn):
    if users.find_one({"email": data.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = hash_password(data.password)
    user = {
        "name": data.name,
        "email": data.email,
        "password": hashed,
    }
    users.insert_one(user)
    return {"message": "Signup successful"}

# -------------------------
# Login Endpoint
# -------------------------
@app.post("/login")
async def login(data: LoginIn):
    user = users.find_one({"email": data.email})
    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"user_id": str(user["_id"])})
    return {"access_token": token, "token_type": "bearer"}

# -------------------------
# Chat Endpoint
# -------------------------
@app.post("/chat")
async def chat(data: ChatIn, authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    try:
        user_data = decode_token(authorization.split(" ")[1])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    reply = generate_reply(data.message, user_id=user_data["user_id"])
    
    # Store chat in DB
    chats.insert_one({
        "user_id": ObjectId(user_data["user_id"]),
        "message": data.message,
        "reply": reply
    })
    return {"reply": reply}

# -------------------------
# Train Business AI Endpoint
# -------------------------
@app.post("/train-business")
async def train_business(data: BusinessTrainIn, authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    try:
        user_data = decode_token(authorization.split(" ")[1])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Train AI logic here
    businesses.update_one(
        {"user_id": ObjectId(user_data["user_id"])},
        {"$set": {"business_data": data.business_data}},
        upsert=True
    )
    return {"message": "Business AI trained successfully"}

# -------------------------
# Test Endpoint
# -------------------------
@app.get("/")
async def root():
    return {"message": "Ayamil Coders AI backend is running"}
