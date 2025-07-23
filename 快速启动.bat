@echo off
chcp 65001 >nul
title 语音输入助手 - 快速启动

echo 🚀 语音输入助手快速启动中...
echo.

python start_fast.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ 快速启动失败，正在尝试完整启动...
    echo.
    python start.py
)

pause 