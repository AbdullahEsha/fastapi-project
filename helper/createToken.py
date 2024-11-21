#filepath @helper/createToken.py

from typing import Union
from jose import JWTError, jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    secret_key = os.getenv("SECRET_KEY", "default_secret_key")
    algorithm = os.getenv("ALGORITHM", "HS256")
    
    if not secret_key or not algorithm:
        raise ValueError("SECRET_KEY or ALGORITHM not configured in environment variables.")
    
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes = os.getenv("TOKEN_EXPIRES", 15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt
