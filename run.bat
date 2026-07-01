@echo off
chcp 65001 >nul
title StudyPal - venv 启动
cd /d D:\code\StudyPal

echo [1/3] 清理占用 5000 端口的旧进程...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000 ^| findstr LISTENING') do (
    echo   杀掉 PID %%a
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 /nobreak >nul

echo [2/3] 验证 venv python...
if not exist ".\.venv\Scripts\python.exe" (
    echo [错误] 找不到 .venv\Scripts\python.exe
    pause
    exit /b 1
)

echo [3/3] 启动 Flask (venv)...
echo   访问 http://localhost:5000
echo.
".\.venv\Scripts\python.exe" app.py
pause