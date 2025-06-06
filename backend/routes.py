from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from auth import admin_only, manager_only, get_current_active_user
import models
from database import get_db
from schemas import ScooterBase, RentalCreate, RentalResponse
from datetime import datetime

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

@router.get('/rentals/history', response_model=list[dict])
async def get_rental_history(
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(get_current_active_user)
):
    # Получение записей о поездках пользователя
    rentals = (
        db.query(
            models.Rentals.start_time,
            models.Rentals.end_time,
            models.Rentals.total_cost,
            models.Rentals.tariff_id,
            models.Scooter.frame
        )
        .join(models.Scooter, models.Rentals.scooter_id == models.Scooter.id)
        .filter(
            models.Rentals.user_id == current_user.id,
            models.Rentals.end_time.isnot(None),
            models.Rentals.end_time > models.Rentals.start_time
        )
        .all()
    )

    # Форматирование данных
    rental_history = []
    for rental in rentals:
        start_time = rental.start_time.strftime("%H:%M")
        end_time = rental.end_time.strftime("%H:%M")
        duration = int((rental.end_time - rental.start_time).total_seconds() // 60)
        rental_history.append({
            "Рама": rental.frame,
            "Время старта": start_time,
            "Время окончания": end_time,
            "Продолжительность (минуты)": duration,
            "Сумма (рубли)": rental.total_cost,
            "Тариф": "Поминутный" if rental.tariff_id == 1 else "Фиксированный"
        })

    return rental_history


# Получение самоката по номеру рамы
@router.get('/scooters/by-frame/{frame}', response_model=ScooterBase)
async def get_scooter_by_frame(frame: str, db: Session = Depends(get_db)):
    scooter = db.query(models.Scooter).filter(models.Scooter.frame == frame).first()
    if not scooter:
        raise HTTPException(status_code=404, detail="Самокат с указанным номером рамы не найден")
    if scooter.status != 'available':
        raise HTTPException(status_code=400, detail="Самокат недоступен для аренды")
    return scooter

# Начало аренды
@router.post('/rentals/start', response_model=RentalResponse)
async def start_rental(
    rental: RentalCreate,
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(get_current_active_user)
):
    # Проверяем самокат
    scooter = db.query(models.Scooter).filter(models.Scooter.frame == rental.frame).first()
    if not scooter:
        raise HTTPException(status_code=404, detail="Самокат не найден")
    if scooter.status != 'available':
        raise HTTPException(status_code=400, detail="Самокат недоступен для аренды")
    
    # Проверяем тариф
    tariff = db.query(models.Tariffs).filter(models.Tariffs.id == rental.tariff_id).first()
    if not tariff:
        raise HTTPException(status_code=404, detail="Тариф не найден")
    
    # Создаём запись аренды
    db_rental = models.Rentals(
        user_id=current_user.id,
        scooter_id=scooter.id,
        start_time=datetime.utcnow(),
        start_location=scooter.location,
        status=True,
        tariff_id=rental.tariff_id
    )
    db.add(db_rental)
    db.commit()
    db.refresh(db_rental)
    
    # Обновляем статус самоката
    scooter.status = 'in_use'
    db.commit()
    
    return db_rental

# Новый эндпоинт: Завершение аренды
@router.patch('/rentals/{rental_id}/end', response_model=RentalResponse)
async def end_rental(
    rental_id: int,
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(get_current_active_user)
):
    rental = db.query(models.Rentals).filter(models.Rentals.id == rental_id, models.Rentals.user_id == current_user.id).first()
    if not rental:
        raise HTTPException(status_code=404, detail="Аренда не найдена или не принадлежит пользователю")
    if not rental.status:
        raise HTTPException(status_code=400, detail="Аренда уже завершена")
    
    # Обновляем end_time и статус
    rental.end_time = datetime.utcnow()
    rental.status = False
    rental.end_location = db.query(models.Scooter).filter(models.Scooter.id == rental.scooter_id).first().location
    
    # Обновляем статус самоката
    scooter = db.query(models.Scooter).filter(models.Scooter.id == rental.scooter_id).first()
    scooter.status = 'available'
    
    db.commit()
    db.refresh(rental)
    return rental



# Добавить функцию активации аренды (таблица rentals)

# Добавить функцию завершения аренды (таблица rentals)

# Добавить функцию получения данных о роли по role_id (таблица roles)

# Добавить функцию получения данных о пользователе по user_id (таблица users)