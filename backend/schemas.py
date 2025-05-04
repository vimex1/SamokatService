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