import os
import bcrypt
from datetime import datetime, timezone, timedelta
import jwt

SECRET_KEY = os.getenv("SECRET_KEY", "To error is human; to forgive, divine.")
ALGORITH = 'HS256'
TOKEN_MINUTES = 60


def hash_password(password:str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")    

def verify_password(password:str,password_hash:str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except  ValueError:
        return False
    
def create_access_token(user_id:int, role:str) -> str:
    expire  = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_MINUTES)
    payload = {"sub": str(user_id), "role" : role, "expire" : expire}
    return jwt.encode(payload,SECRET_KEY,ALGORITH)

def decode_token(token:str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms= [ALGORITH])
    




