from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.models import Apartment, Block
from app.schemas import ApartmentOut, ApartmentCreate, BlockOut, BlockCreate

router = APIRouter(tags=["setup"])

@router.post("/apartments",response_model= ApartmentOut, status_code=201)
def create_apartment(body:ApartmentCreate, db:Session = Depends(get_db)):
    apartment = Apartment(**body.model_dump())
    db.add(apartment)
    db.commit()
    db.refresh(apartment)
    return apartment


@router.get("/apartments", response_model=list[ApartmentOut])
def list_aprtments(db:Session = Depends(get_db)):
    return db.scalars(select(Apartment)).all()


@router.post("/blocks", response_model = BlockOut, status_code = 201)
def create_block(body:BlockCreate, db:Session = Depends(get_db)):
    if db.get(Apartment, body.apartment_id) is None:
        raise HTTPException(status_code=404, detail= "Apartment does not found")
    block = Block(**body.model_dump())
    db.add(block)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code = 409, detail= "Block name already exists in this apartment")
    db.refresh(block)
    return block

@router.get("/blocks", response_model=list[BlockOut])
def list_blocks(db:Session = Depends(get_db)):
    return db.scalars(select(Block).order_by(Block.name)).all()