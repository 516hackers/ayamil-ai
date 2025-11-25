from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import internal modules
from db import users, businesses, chats  # your collections
from schemas import SignupIn, LoginIn, BusinessTrainIn, ChatIn
from auth import hash_password, verify_password, create_access_token, decode_token
from ai_engine import generate_reply

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
# Helper functions
# -------------------------
def get_user_from_token(token: str):
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        user = users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


# -------------------------
# Routes
# -------------------------

@app.get("/")
def home():
    return {"message": "Ayamil AI backend is running"}

# ----- Signup -----
@app.post("/signup")
def signup(data: SignupIn):
    existing_user = users.find_one({"email": data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed = hash_password(data.password)
    user_doc = {
        "name": data.name,
        "email": data.email,
        "password": hashed
    }
    result = users.insert_one(user_doc)
    token = create_access_token(str(result.inserted_id))
    return {"token": token, "user": {"id": str(result.inserted_id), "name": data.name, "email": data.email}}

# ----- Login -----
@app.post("/login")
def login(data: LoginIn):
    user = users.find_one({"email": data.email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(str(user["_id"]))
    return {"token": token, "user": {"id": str(user["_id"]), "name": user.get("name"), "email": user.get("email")}}

# ----- Train business -----
@app.post("/train-business")
def train_business(data: BusinessTrainIn, authorization: str = Header(None)):
    user = get_user_from_token(authorization)
    business_doc = {
        "user_id": str(user["_id"]),
        "business_text": data.business_text
    }
    businesses.update_one({"user_id": str(user["_id"])}, {"$set": business_doc}, upsert=True)
    return {"status": "success", "message": "Business saved & training simulated"}

# ----- Chat endpoint -----
@app.post("/chat")
def chat(data: ChatIn, authorization: str = Header(None)):
    user = get_user_from_token(authorization)
    # Save chat
    chat_doc = {
        "user_id": str(user["_id"]),
        "message": data.message
    }
    chats.insert_one(chat_doc)
    # Generate AI reply
    reply = generate_reply(data.message, str(user["_id"]))
    return {"reply": reply}
