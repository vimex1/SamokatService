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


# class RentalSchema(BaseModel):
#     id: int
#     user_id: int
#     scooter_id: int
#     start_time: str
#     end_time: str
#     start_location: Optional[str]
#     end_location: Optional[str]
#     # status: bool
#     # total_coast: Optional[float]
#     # tariff_id: int