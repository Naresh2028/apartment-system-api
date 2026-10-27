from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models import User
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.security import decode_token
import jwt
from sqlalchemy  import select

ADMIN = 'admin'
SECRETARY = 'secretary'
SECURITY = 'security'

bearer = HTTPBearer(auto_error=False)

def get_current_user(
    creds:HTTPAuthorizationCredentials | None = Depends(bearer),
    db:Session = Depends(get_db)
    ) -> User:
    if creds is None:
        raise HTTPException(status_code=401, detail="Not logged in")
    try:
        user_id = decode_token(creds.credentials)["sub"]
    except (jwt.PyJWTError,KeyError,ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    smtp = (
        select(User)
        .options(joinedload(User.role), joinedload(User.profile))
        .where(User.id == user_id)
    )
    
    user = db.scalar(smtp)
    if user is None:
        raise HTTPException(status_code=401, detail="User is removed permenantly, contact Naresh")
    return user


def require_roles(*allowed:str):
    def checker(user:User = Depends(get_current_user)) -> User:
        if user.role.role_name not in allowed:
            raise HTTPException(status_code=403, detail="this action is restricted, please contact naresh")
        return user
    
    return checker

