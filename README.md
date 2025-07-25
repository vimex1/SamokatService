
# SamokatService

SamokatService — это приложение для управления арендой самокатов. Оно включает серверную часть (backend) на FastAPI и клиентскую часть (frontend) на React.

---

## Установка проекта

### 1. Клонирование репозитория
Склонируйте репозиторий на ваш компьютер:
```bash
git clone <https://github.com/vimex1/SamokatService.git>
```

Перейдите в папку проекта:
```bash
cd SamokatService
```

---

## Установка зависимостей

### Backend
1. Перейдите в папку `backend`:
   ```bash
   cd backend
   ```

2. Убедитесь, что у вас установлен Python версии 3.10 или выше.

3. Создайте виртуальное окружение:
   ```bash
   python -m venv .venv
   ```

4. Активируйте виртуальное окружение:
   - **Windows**:
     ```bash
     .venv\Scripts\activate
     ```
   - **Linux/macOS**:
     ```bash
     source .venv/bin/activate
     ```

5. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

6. Настройте базу данных:
   - Убедитесь, что PostgreSQL установлен и запущен.
   - Создайте базу данных, указанную в файле `.env`.

7. Выполните миграции:
   ```bash
   alembic upgrade head
   ```

---

### Frontend
1. Перейдите в папку samokat-app:
   ```bash
   cd ../samokat-app
   ```

2. Убедитесь, что у вас установлен Node.js версии 16 или выше.

3. Установите зависимости:
   ```bash
   npm install
   ```

---

## Запуск проекта

### Backend
1. Перейдите в папку backend:
   ```bash
   cd backend
   ```

2. Активируйте виртуальное окружение:
   - **Windows**:
     ```bash
     .venv\Scripts\activate
     ```
   - **Linux/macOS**:
     ```bash
     source .venv/bin/activate
     ```

3. Запустите сервер:
   ```bash
   uvicorn main:app --reload
   ```

Сервер будет доступен по адресу: `http://localhost:8000`.

---

### Frontend
1. Перейдите в папку samokat-app:
   ```bash
   cd ../samokat-app
   ```

2. Запустите приложение:
   ```bash
   npm start
   ```

Приложение будет доступно по адресу: `http://localhost:3000`.

---

## Основные функции
- **Профиль пользователя**: Просмотр информации о пользователе и истории поездок.
- **Аренда самокатов**: Выбор тарифа и управление текущей арендой.
- **Администрирование**: Управление самокатами и пользователями.

---

## Требования
- Python 3.10+
- Node.js 16+
- PostgreSQL

---

## Лицензия
Этот проект распространяется под лицензией MIT.
