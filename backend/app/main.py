from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

from .db import users, businesses, chats
from .schemas import SignupIn, LoginIn, BusinessTrainIn, ChatIn
from .auth import hash_password, verify_password, create_access_token, decode_token
from .ai_engine import generate_reply

app = FastAPI(title="Ayamil Coders AI - Backend")

# CORS setup
origins = os.getenv("CORS_ORIGINS", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origins] if origins != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====== Signup ======
@app.post("/signup")
def signup(data: SignupIn):
    if users.find_one({"email": data.email}):
        raise HTTPException(status_code=400, detail="Email already exists")
    hashed_pw = hash_password(data.password)
    user_doc = {
        "name": data.name,
        "email": data.email,
        "password": hashed_pw,
    }
    result = users.insert_one(user_doc)
    token = create_access_token(str(result.inserted_id))
    return {"token": token, "user": {"id": str(result.inserted_id), "name": data.name, "email": data.email}}

# ====== Login ======
@app.post("/login")
def login(data: LoginIn):
    user = users.find_one({"email": data.email})
    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(str(user["_id"]))
    return {"token": token, "user": {"id": str(user["_id"]), "name": user["name"], "email": user["email"]}}

# ====== Train Business Text ======
@app.post("/train-business")
def train_business(data: BusinessTrainIn, authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization required")
    user_id = decode_token(authorization)
    # Save/update business text
    businesses.update_one(
        {"user_id": user_id},
        {"$set": {"business_text": data.business_text}},
        upsert=True
    )
    return {"status": "success", "message": "Business text saved & training simulated"}

# ====== Chat with AI ======
@app.post("/chat")
def chat(data: ChatIn, authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization required")
    user_id = decode_token(authorization)
    
    # Save user message
    chat_doc = {
        "user_id": user_id,
        "message": data.message
    }
    chats.insert_one(chat_doc)

    # Generate AI reply
    reply = generate_reply(data.message, user_id)
    
    # Save AI reply
    chats.insert_one({"user_id": user_id, "message": reply, "from_ai": True})
    
    return {"reply": reply}
