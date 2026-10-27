from fastapi import APIRouter, Depends, HTTPException

from app.deps import require_roles, ADMIN

from app.schemas import UserOut, UserCreate, PasswordReset

from app.models import Role, User, StaffProfile

from app.database import get_db

from sqlalchemy import select

from sqlalchemy.orm import Session, joinedload

from sqlalchemy.exc import IntegrityError

from app.security import hash_password


router = APIRouter(prefix="/users", tags=["users"], dependencies=[Depends(require_roles(ADMIN))])


@router.post("", response_model=UserOut, status_code=201)
def create_user(body:UserCreate, db:Session= Depends(get_db)):
    role = db.scalar(select(Role).where(Role.role_name == body.role_name))
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found. Did you run seed?")
    
    user = User(
        username = body.username,
        password_hash = hash_password(body.password),        
        role_id = role.id,
        profile = StaffProfile(**body.profile.model_dump()),
    )
    
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409,detail="Username already taken")
    db.refresh(user)
    return user
    
@router.get("", response_model=list[UserOut])
def list_users(db:Session = Depends(get_db)):
    stmt = select(User).options(joinedload(User.role), joinedload(User.profile)).order_by(User.username)
    return db.scalars(stmt).all()


@router.put("/{user_id}/password",status_code=204)
def reset_password(user_id:int, body:PasswordReset, db:Session = Depends(get_db)):
    user = db.get(User, user_id)
    if user is None:
       raise HTTPException(status_code=404, detail="User Not Found")
    user.password_hash = hash_password(body.new_password) 
    db.commit()
    return 
    