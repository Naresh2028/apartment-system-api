from database import Base, engine, SessionLocal
from models import Flat, Resident, User, Visitor, Role, Apartment, Block, Vehicle

from sqlalchemy.exc import IntegrityError


def init_db():
    print("Flushing metadata and creating database tables...")
    
    print('Deleting existing tables')
    Base.metadata.drop_all(bind=engine)
    print('Table deleted successfully....')
    
    print("Table creating...")
    Base.metadata.create_all(bind=engine)
    print('Table created successfully')

if __name__ == "__main__":
    init_db()

    with SessionLocal() as db:
        apartment = Apartment(name="Green Meadows", address = "Chennai")
        roles = [Role(role_name=n) for n in ("admin", "secretary", "security")]
        db.add_all([apartment, *roles])
        db.commit()
    
        block = Block(name="b", total_floors=5, flats_per_floor=4, apartment_id=apartment.id)
        db.add(block)
        db.commit()
    
        flat = Flat(floor=2, flat_number="204", block_id=block.id)
        guard = User(username="guard1", password_hash="not-yet-implemented",role_id=roles[2].id)
        db.add_all([flat,guard])
        db.commit()
    
        resident = Resident(name="Naresh", phone="9654561561", resident_type="rental", flat_id=flat.id)
        db.add(resident)
        db.commit()
    
        db.add(Vehicle(vehicle_type="two_wheeler", vehicle_number="TN24AM3450", resident_id=resident.id))
        db.add(Visitor(name="Sathesan", purpose="business meeting", vehicle_number="KL01AM6846", 
                                    flat_id = flat.id, resident_id = resident.id, recorded_by=guard.id))
        db.commit()
    
        visitor = db.query(Visitor).first()
    
        if visitor is not None:
            print(f"visitor: {visitor.name} Block name {visitor.flat.block.name} at {visitor.check_in_at}")
        else:
            print("Visitor is not found")
            
        # ==========================================================
        # INTEGRITY TESTS (Now safe because 'guard' is still bound)
        # ==========================================================

        print("\n--- Running Integrity Tests ---")

        
        # TEST 1: Foreign Key Protection (Invalid Flat ID)
        db.add(Visitor(name="Ghost", purpose="Test", flat_id=999, recorded_by=guard.id))
        try:
            db.commit()
        except IntegrityError as e:
            db.rollback()
            print("Rejected correctly:", e.orig)
            
            # Fix: Re-bind or refresh objects
            db.add(guard)
            db.add(block)
        
        # TEST 2: Unique Constraint Protection (Duplicate flat number in same block)
        db.add(Flat(floor=1, flat_number="204", block_id=block.id))   # duplicate in same block
        try:
            db.commit()
        except IntegrityError as e:
            db.rollback()
            print("Unique rejected:", e.orig)