from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session, joinedload
from app.models import Resident, Flat, Visitor
from app.schemas import ResidentOut, ResidentCreate
from sqlalchemy import select, or_
from app.database import get_db

router = APIRouter(prefix="/residents", tags=["residents"])

def get_resident_or_404(db:Session, resident_id:int) -> Resident:
    resident = db.get(Resident, resident_id)

    if resident is None:
        raise HTTPException(status_code = 404, detail = "Resident not found")
    return resident      #Why empty resident should return?

def ensure_flat_exists(db:Session, flat_id:int) -> None:
    if db.get(Flat, flat_id) is None:
        raise HTTPException(status_code=404, detail="flat not found")

@router.get("", response_model= list[ResidentOut])
def list_residents(q:str | None = None, db:Session = Depends(get_db)):
    stmt = select(Resident).options(joinedload(Resident.flat)).order_by(Resident.name)
    if q:
        like = f"%{q}%"
        stmt = stmt.join(Flat).where(
            or_(Resident.name.ilike(like), Resident.phone.ilike(like), Flat.flat_number.ilike(like))
        )
    return db.scalars(stmt).all()

@router.post("", response_model= ResidentOut, status_code=201)
def create_resident(body:ResidentCreate, db:Session = Depends(get_db)):
    ensure_flat_exists(db, body.flat_id)
    resident = Resident(**body.model_dump())
    db.add(resident)
    db.commit()
    db.refresh(resident)
    return resident

@router.get("/{resident_id}", response_model=ResidentOut)
def get_resident(resident_id:int, db:Session = Depends(get_db)):
    return get_resident_or_404(db=db,resident_id=resident_id)

@router.put("/{resident_id}", response_model = ResidentOut)
def update_resident(resident_id:int, body: ResidentCreate, db:Session = Depends(get_db)):
    resident = get_resident_or_404(db, resident_id)
    ensure_flat_exists(db, body.flat_id)
    for field, value in body.model_dump().items():
        setattr(resident, field, value)
    db.commit()
    db.refresh(resident)
    return resident

@router.delete("?/{resident_id}", status_code=204)
def delete_resident(resident_id:int, db: Session = Depends(get_db)):
    resident = get_resident_or_404(db,resident_id)
    has_visitors = db.scalar(select(Visitor.id).where(Visitor.resident_id == resident_id).limit(1))
    if has_visitors:
        raise HTTPException(status_code=409, detail="Resident has visitor records")
    db.delete(resident)
    db.commit()

