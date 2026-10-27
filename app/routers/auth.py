from fastapi import APIRouter, Depends, HTTPException
from app.models import User
from app.schemas import UserOut, LoginRequest, TokenOut, DutyUpdate
from sqlalchemy.orm import Session, joinedload

from app.deps import get_current_user, require_roles, SECURITY

from app.database import get_db

from sqlalchemy import select

from app.security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags = ["auth"])


@router.post("/login", response_model=TokenOut)
def login(body:LoginRequest, db:Session = Depends(get_db)):
    user = db.scalar(
        select(User)
            .options(joinedload(User.role)).where(User.username == body.username)
    )
    
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    role = user.role.role_name
    return TokenOut(access_token=create_access_token(user.id, role), role = role, username=user.username)


@router.get("/me", response_model=UserOut)
def me(user:User = Depends(get_current_user)):
    return user

@router.patch("me/duty", response_model=UserOut)
def set_duty(
    body:DutyUpdate,
    user:User = Depends(require_roles(SECURITY)),
    db:Session = Depends(get_db)
):
    if user.profile is None:
        raise HTTPException(status_code=409, detail="This user has no staff profile")
    user.profile.is_on_duty = body.on_duty
    db.commit()
    db.refresh(user)
    return user