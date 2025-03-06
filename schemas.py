from pydantic import BaseModel
from typing import Optional

class ScooterSchema(BaseModel):
    model: str
    location: str
    frame: str
    battery: int
    status: str
    connection_status: str
    last_action_id: Optional[str]

    class Config:
        from_attributes = True