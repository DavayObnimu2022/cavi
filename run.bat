@echo off
title CAVI Мониторинг
echo ========================================
echo   УСТАНОВКА ЗАВИСИМОСТЕЙ...
echo ========================================
pip install fastapi uvicorn jinja2 aiofiles
echo.
echo ========================================
echo   ЗАПУСК ПРИЛОЖЕНИЯ
echo   Откройте браузер: http://127.0.0.1:8000
echo ========================================
echo.
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
pause