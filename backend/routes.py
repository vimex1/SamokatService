from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from auth import admin_only, manager_only
import models
from database import get_db
from schemas import ScooterBase

router = APIRouter()


# Эндпоинт для получения списка самокатов (без проверки прав)
@router.get('/scooters/', response_model=List[ScooterBase])
async def get_scooters(db: Session = Depends(get_db)):
    return db.query(models.Scooter).all()

# Эндпоинт для добавления примеров самокатов (доступно только для администратора)
@router.post('/scooter/add_sample')
async def insert_scooters(db: Session = Depends(get_db), current_user: models.Users = Depends(admin_only)):
    scooters = [
        models.Scooter(model='Xiaomi M365', location='55.751244, 37.618423', frame='aluminum', battery=85, status='available', connection_status='online'),
        models.Scooter(model='Segway Ninebot', location='55.752220, 37.615560', frame='carbon', battery=90, status='in_use', connection_status='online'),
        models.Scooter(model='Lyme', location='55.755544, 37.615423', frame='aluminum', battery=15, status='available', connection_status='online'),
        models.Scooter(model='Scooter', location='55.752220, 37.615560', frame='carbon', battery=10, status='in_use', connection_status='online'),
    ]
    db.add_all(scooters)
    db.commit()
    return {"code": 200, "message": "Самокаты успешно добавлены"}

# Эндпоинт для удаления всех самокатов (доступно только для администратора)
@router.delete('/scooters/delete_all')
async def delete_all_scooters(db: Session = Depends(get_db), current_user: models.Users = Depends(admin_only)):
    db.query(models.Scooter).delete()
    db.commit()
    return {"code": 200, "message": "Все самокаты удалены"}

# Эндпоинт для добавления одного самоката (доступно только для администратора)
@router.post('/scooter/add_scooter')
async def create_scooter(scooter: ScooterBase, db: Session = Depends(get_db), current_user: models.Users = Depends(admin_only)):
    db_scooter = models.Scooter(**scooter.model_dump())
    db.add(db_scooter)
    db.commit()
    db.refresh(db_scooter)
    return {
        "scooter": db_scooter,
        "code": 200,
        "message": "Самокат добавлен"
    }
