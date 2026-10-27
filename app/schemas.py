from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

class ORMModel(BaseModel):
    """Parent for every *Out schema: lets pydantic ready SQLAlchamey objects."""
    model_config = ConfigDict(from_attributes=True)
    
# --- Login ---
class LoginRequest(BaseModel):
    username:str
    password:str
    
# --- Token ---

class TokenOut(BaseModel):
    access_token:str
    token_type:str = "bearer"
    role:str
    username:str
    
# --- Role ---

class RoleOut(BaseModel):
    id:int
    role_name:str
    
# --- Staff Profile ---

class StaffProfileBase(BaseModel):
    full_name:str = Field(min_length=1,max_length=30)
    phone:str = Field(min_length=10,max_length=18)
    address:str | None = Field(default=None, max_length=50)
    shift: Literal["day" , "night"] | None = None
    
class StaffProfileOut(ORMModel, StaffProfileBase):
    id:int
    is_duty_on : bool
    
class DutyUpdate(BaseModel):
    on_duty:bool

    
# --- User ---
class UserCreate(BaseModel):
    username:str = Field(min_length=3, max_length = 30)
    password:str = Field(min_length = 10, max_length=72)
    role_name: Literal["Secretory", "Security"]
    profile:StaffProfileBase

class UserOut(ORMModel):
    id:int
    username:str
    role:RoleOut
    profile:StaffProfileOut | None  = None

# --- Password ---
class PasswordReset(BaseModel):
    new_password:str = Field(min_length = 10, max_length=72)

# --- Apartment ---

class ApartmentBase(BaseModel):
    name:str = Field(min_length=1, max_length=25)
    address:str | None = Field(default=None, max_length=30)
    
class ApartmentCreate(ApartmentBase):
    pass

class ApartmentOut(ORMModel, ApartmentBase):
    id:int
    

# --- Block ---

class BlockBase(BaseModel):
    name:str = Field(min_length=1, max_length=15)
    total_floors: int = Field(ge=1)
    flats_per_floor:int = Field(ge=1)
    apartment_id:int
    
class BlockCreate(BlockBase):
    pass

class BlockOut(ORMModel, BlockBase):
    id:int
    apartment_id:int
    
# --- Flat ---

class FlatBase(BaseModel):
    floor:int = Field(ge=0)
    flat_number:str = Field(min_length=1,max_length=5)
    occupied:bool = False
    
class FlatCreate(FlatBase):
    block_id:int
    floor:int

class FlatOut(ORMModel, FlatBase):
    id:int
    block:BlockOut

# --- Resident --- 

class ResidentBase(BaseModel):
    name:str = Field(min_length=1,max_length=30)
    phone:str = Field(min_length=1,max_length=14)
    resident_type:Literal["owner","rental"]

class ResidentCreate(ResidentBase):
    flat_id : int

class ResidentOut(ORMModel, ResidentBase):
    id:int
    flat:FlatOut
    
# --- Vehicle ---
class VehicleBase(BaseModel):
    vehicle_type: Literal["two_wheeler", "three_wheeler", "four_wheeler"]
    vehicle_number: str = Field(min_length=10,max_length=15)
    
    
class VehicleCreate(VehicleBase):
    resident_id:int
    
class VehicleOut(ORMModel, VehicleBase):
    id:int
    resident_id:int