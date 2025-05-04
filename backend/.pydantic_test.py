from datetime import datetime

from pydantic import BaseModel, PositiveInt


class User(BaseModel):
    id: int  # (1)!
    name: str = 'John Doe'  # (2)!
    signup_ts: datetime | None  # (3)!
    tastes: dict[str, PositiveInt]  # (4)!


external_data = {
    'id': 123,
    'signup_ts': '2019-06-01 12:22',  # (5)!
    'tastes': {
        'wine': 9,
        'cheese': 7,  # (6)!
        'cabbage': '1',  # (7)!
    },
}

user = User(**external_data)  # (8)!

print(user.id, user.name)  # (9)!
#> 123
print(user.model_dump())  # (10)!


class Scooter(BaseModel):
    id: int
    name: str
    model: str
    status: str
    rent: bool

data = {
    'id' : 1,
    'name' : 'Segway Ninebot',
    'model' : 'N625',
    'status' : 'On rent',
    'rent' : True
}

scooter = Scooter(**data)

print(scooter)