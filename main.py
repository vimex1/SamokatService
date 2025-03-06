from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from schemas import ScooterSchema


app = FastAPI()
models.Base.metadata.create_all(bind=engine) #creates all the tables


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]     # наше подключение к бд


@app.get('/scooters/', response_model=List[ScooterSchema])
async def get_scooter(db: db_dependency):
    return db.query(models.Scooter).all()


@app.post('/scooter/add_sample')
async def insert_scooters(db: db_dependency):
    scooters = [
        models.Scooter(model='Xiaomi M365', location='55.751244, 37.618423', frame='aluminum', battery=85, status='available', connection_status='online'),
        models.Scooter(model='Segway Ninebot', location='55.752220, 37.615560', frame='carbon', battery=90, status='in_use', connection_status='online'),
        models.Scooter(model='Dualtron Thunder', location='55.755826, 37.617300', frame='steel', battery=70, status='charging', connection_status='offline'),
        models.Scooter(model='Kugoo S3', location='55.758946, 37.620393', frame='aluminum', battery=60, status='maintenance', connection_status='offline'),
        models.Scooter(model='Yandex Scooter', location='55.760451, 37.624056', frame='aluminum', battery=95, status='available', connection_status='online'),
        models.Scooter(model='OKAI ES200', location='55.762890, 37.627021', frame='carbon', battery=80, status='in_use', connection_status='online'),
        models.Scooter(model='Uber Jump', location='55.765020, 37.630280', frame='aluminum', battery=50, status='charging', connection_status='offline'),
        models.Scooter(model='Bolt Scooter', location='55.767550, 37.633700', frame='carbon', battery=40, status='maintenance', connection_status='offline'),
        models.Scooter(model='CityCoco', location='55.769800, 37.636000', frame='steel', battery=100, status='available', connection_status='online'),
        models.Scooter(model='Razor E300', location='55.772100, 37.639200', frame='aluminum', battery=30, status='in_use', connection_status='online'),
    ]

    db.add_all(scooters)
    db.commit()
    return {
        "code": 200,
        "message": "Примеры записей в таблицу 'scooter' успешно добавлены в БД"
        }


@app.delete('/scooters/delete_all')
async def delete_all_scooters(db: db_dependency):
    db.query(models.Scooter).delete()
    db.commit()
    return {
        "code": 200,
        "message": "Записи в таблице 'scooter' удалены"
        }

