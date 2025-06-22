@echo off
call venv\Scripts\activate
python manage.py runserver 127.0.0.1:8080
pause
