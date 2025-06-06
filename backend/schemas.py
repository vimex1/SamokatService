from datetime import datetime
from token import OP
from pydantic import BaseModel
from typing import Optional


class ScooterBase(BaseModel):
    model: str
    location: str
    frame: str
    battery: int
    status: str
    connection_status: Optional[str] = None
    last_action_id: Optional[int] = None

    class Config:
        from_attributes = True


class UserOut(BaseModel):
    id: int
    phone: str
    full_name: str | None = None
    email: str | None = None
    disabled: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    id: int | None = None
    phone: str | None = None
    role_id: int | None = None
    username: str | None = None
    balance: float | None = None

class RentalCreate(BaseModel):
    frame: str
    tariff_id: int

class RentalResponse(BaseModel):
    id: int
    user_id: int
    scooter_id: int
    start_time: datetime
    end_time: Optional[datetime]
    start_location: str
    end_location: Optional[str]
    status: bool
    total_cost: Optional[float]
    tariff_id: int

    class Config:
        orm_mode = True