from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import internal modules
from db import users, businesses, chats
from schemas import SignupIn, LoginIn, BusinessTrainIn, ChatIn
from auth import hash_password, verify_password, create_access_token, decode_token
from ai_engine import generate_reply

app = FastAPI(title="Ayamil Coders AI - Backend")

# Allow CORS from any origin (can restrict to your frontend)
origins = os.getenv("CORS_ORIGINS", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origins] if origins != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======== AUTH ROUTES ========
@app.post("/signup")
async def signup(payload: SignupIn):
    if users.find_one({"email": payload.email}):
        raise HTTPException(status_code=400, detail="Email already exists")
    hashed = hash_password(payload.password)
    user = {"name": payload.name, "email": payload.email, "password": hashed}
    res = users.insert_one(user)
    user["_id"] = str(res.inserted_id)
    token = create_access_token(user["_id"])
    return {"token": token, "user": {"id": user["_id"], "name": user["name"], "email": user["email"]}}

@app.post("/login")
async def login(payload: LoginIn):
    user = users.find_one({"email": payload.email})
    if not user or not verify_password(payload.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(str(user["_id"]))
    return {"token": token, "user": {"id": str(user["_id"]), "name": user["name"], "email": user["email"]}}

# ======== BUSINESS TRAINING ROUTE ========
@app.post("/train-business")
async def train_business(payload: BusinessTrainIn, authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    token = authorization.replace("Bearer ", "")
    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    # Save business description
    businesses.update_one(
        {"user_id": user_id},
        {"$set": {"business_text": payload.business_text}},
        upsert=True
    )
    return {"status": "success", "message": "Business text saved"}

# ======== CHAT ROUTE ========
@app.post("/chat")
async def chat(payload: ChatIn, authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    token = authorization.replace("Bearer ", "")
    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Call AI engine to generate reply
    reply = await generate_reply(user_id, payload.message)

    # Save chat to DB (optional)
    chats.insert_one({"user_id": user_id, "message": payload.message, "reply": reply})

    return {"reply": reply}

# ======== HEALTH CHECK ========
@app.get("/health")
async def health():
    return {"status": "ok"}
