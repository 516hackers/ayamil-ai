
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId
from dotenv import load_dotenv
import os


load_dotenv()


from .db import users, businesses, chats
from .schemas import SignupIn, LoginIn, BusinessTrainIn, ChatIn
from .auth import hash_password, verify_password, create_access_token, decode_token
from .ai_engine import generate_reply


app = FastAPI(title='Ayamil Coders AI - Backend')


# Allow requests from GitHub Pages and local dev
origins = os.getenv('CORS_ORIGINS', '*')
app.add_middleware(
CORSMiddleware,
allow_origins=[origins] if origins != '*' else ['*'],
allow_credentials=True,
allow_methods=['*'],
allow_headers=['*'],
)




return {'reply': reply}
