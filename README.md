# CAVI Мониторинг — REST API

## 📋 Описание
Веб-сервис для получения/редактирования данных из БД (лабораторная работа №3).

## 🚀 Запуск
```bash
pip install -r requirements.txt
docker-compose up -d
python -m alembic upgrade head
python -m uvicorn main:app --reload