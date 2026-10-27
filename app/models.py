from datetime import datetime, timezone
from sqlalchemy import event
from sqlalchemy import ForeignKey, String, UniqueConstraint, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, engine


def utcnow():
    return datetime.now(timezone.utc)


class Role(Base):
    __tablename__ = "roles"

    id:Mapped[int] = mapped_column(primary_key=True)
    role_name:Mapped[str] = mapped_column(String(30),unique=True)
    
    users:Mapped[list["User"]] = relationship(back_populates="role")


class User(Base):
    __tablename__ = "users"

    id:Mapped[int] = mapped_column(primary_key=True)
    username:Mapped[str] = mapped_column(String(45),unique=True)
    password_hash:Mapped[str] = mapped_column(String(60))
    role_id:Mapped[int] = mapped_column(ForeignKey("roles.id"))

    role:Mapped["Role"] = relationship(back_populates="users")
    profile:Mapped["StaffProfile"] = relationship(back_populates="user")
    
class StaffProfile(Base):
    __tablename__ = "staff_profiles"
    
    id:Mapped[int] = mapped_column(primary_key=True)
    full_name:Mapped[str] = mapped_column(String(30))
    phone:Mapped[str] = mapped_column(String(16))
    address:Mapped[str] = mapped_column(String(50))
    shift:Mapped[str | None] = mapped_column(String(10))
    is_on_duty:Mapped[bool] = mapped_column(default=False)
    user_id:Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    
    user:Mapped["User"] = relationship(back_populates="profile")


class Flat(Base):
    __tablename__ = "flats"
    __table_args__ = (UniqueConstraint("block_id","flat_number", name="uq_block_flat"),)

    id:Mapped[int] = mapped_column(primary_key=True)
    floor:Mapped[int] = mapped_column()
    flat_number:Mapped[str] = mapped_column(String(15))
    occupied:Mapped[bool] = mapped_column(default=False)
    block_id:Mapped[int] = mapped_column(ForeignKey("blocks.id"))

    block:Mapped["Block"] = relationship(back_populates="flats")
    residents:Mapped[list["Resident"]] = relationship(back_populates="flat")
    visitors:Mapped[list["Visitor"]] = relationship(back_populates="flat")
    


class Resident(Base):
    __tablename__= "residents"

    id:Mapped[int] = mapped_column(primary_key=True)
    name:Mapped[str] = mapped_column(String(45),index=True)
    phone:Mapped[str] = mapped_column(String(20), nullable=True)
    resident_type:Mapped[str] = mapped_column(String(20))   # owner | rental
    flat_id: Mapped[int] = mapped_column(ForeignKey("flats.id"))
    
    user_id:Mapped[int | None] = mapped_column(ForeignKey("users.id"))

    flat: Mapped["Flat"] = relationship(back_populates="residents")
    vehicles:Mapped[list["Vehicle"]] = relationship(back_populates="resident") # A Resident might have multiple vehicles
    

class Visitor(Base):
    __tablename__ = "visitors"

    id:Mapped[int] = mapped_column(primary_key=True)
    name:Mapped[str] = mapped_column(String(40))
    purpose:Mapped[str] = mapped_column(String(40))
    vehicle_number:Mapped[str | None] = mapped_column(String(20),unique=True)
    check_in_at:Mapped[datetime] = mapped_column(DateTime(timezone=True),default=utcnow,index=True)
    check_out_at:Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    flat_id:Mapped[int] = mapped_column(ForeignKey("flats.id"))
    resident_id:Mapped[int | None ] = mapped_column(ForeignKey("residents.id"))
    recorded_by:Mapped[int] = mapped_column(ForeignKey("users.id"))

    flat: Mapped["Flat"] = relationship(back_populates="visitors")


class Apartment(Base):
    __tablename__  = "apartments"

    id:Mapped[int] = mapped_column(primary_key=True)
    name:Mapped[str] = mapped_column(String(35))
    address:Mapped[str | None] = mapped_column(String(40))
    
    blocks:Mapped[list["Block"]] = relationship(back_populates="apartment")
    

class Block(Base):
    __tablename__ = "blocks"
    __table_args__ = (UniqueConstraint("apartment_id","name", name="uq_apartment_block"),)
    
    id:Mapped[int] = mapped_column(primary_key=True)
    name:Mapped[str] = mapped_column(String(10))
    total_floors:Mapped[int]
    flats_per_floor:Mapped[int]
    apartment_id:Mapped[int] = mapped_column(ForeignKey("apartments.id"))
    
    apartment: Mapped["Apartment"] = relationship(back_populates="blocks")
    flats: Mapped[list["Flat"]] = relationship(back_populates="block")

class Vehicle(Base):
    __tablename__ = "vehicles"

    id:Mapped[int] = mapped_column(primary_key=True)
    vehicle_type:Mapped[str] = mapped_column(String(20)) # Two | Three | Four
    vehicle_number:Mapped[str] = mapped_column(String(30), unique=True) # KL01 AM3450
    resident_id:Mapped[int | None] = mapped_column(ForeignKey("residents.id"))

    resident:Mapped["Resident"] = relationship(back_populates="vehicles")


@event.listens_for(engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    if engine.dialect.name == "sqlite":
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()