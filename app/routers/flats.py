from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from app.models import Flat, Block
from app.database import get_db
from app.schemas import FlatOut, FlatCreate

router = APIRouter(prefix="/flats",tags=["flats"])


@router.post("",response_model=FlatOut,status_code=201)
def create_flat(body:FlatCreate, db:Session = Depends(get_db)):
    block = db.get(Block, body.block_id)
    if block is None:
        raise HTTPException(status_code=404, detail="Block not found")
    
    if body.floor > block.total_floors:
        raise HTTPException(status_code=422, detail=f"Block has only {block.total_floors} floors")
        
    flat = Flat(**body.model_dump())
    db.add(flat)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409,detail="This block, and flat number already exist")
    db.refresh(flat)
    return flat

@router.get("", response_model = list[FlatOut])
def list_flats(db:Session = Depends(get_db)):
    stmt = select(Flat).options(joinedload(Flat.block)).order_by(Flat.block_id, Flat.flat_number)
    return db.scalars(stmt).all()

