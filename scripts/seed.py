from app.database import Base, engine, SessionLocal
from sqlalchemy import select
from fastapi import Depends, HTTPException
from app.models import Role, User
import getpass
from app.security import hash_password


ROLE_NAMES = ["admin", "secretory", "security"]

def main():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        for name in ROLE_NAMES:
            if db.scalar(select(Role).where(Role.role_name == name)) is None:
                db.add(Role(role_name=name))
        db.commit()
        
        if db.scalar(select(User).where(User.username == "admin")) is  None:
            password = getpass.getpass("Choose an admin password (min 8 characters): ")
            admin_role = db.scalar(select(Role).where(Role.role_name == "admin"))
            
            if admin_role is None:
                raise HTTPException(status_code=404, detail="role is not found")
            db.add(User(username="admin", password_hash=hash_password(password), role_id = admin_role.id))
            db.commit()
            print("Admin Created")
        else:
            print("Admin creation failed")    
            
if __name__ == "__main__":
    main()

            