@echo off
cd /d %~dp0

:: 静默启动语音输入助手
echo 正在启动语音输入助手...
python start_silent.py

if errorlevel 1 (
    echo 启动失败，尝试使用交互式启动...
    python start.py
)

exit /b 0 