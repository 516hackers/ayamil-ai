import os
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from dotenv import load_dotenv


load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET', 'change-me-to-a-secure-random-string')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')




def hash_password(password: str) -> str:
return pwd_context.hash(password)




def verify_password(plain: str, hashed: str) -> bool:
return pwd_context.verify(plain, hashed)




def create_access_token(sub: str, expires_delta: int = ACCESS_TOKEN_EXPIRE_MINUTES):
to_encode = {
'sub': sub,
'exp': datetime.utcnow() + timedelta(minutes=expires_delta)
}
return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)




def decode_token(token: str):
try:
payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
return payload.get('sub')
except JWTError:
return None
