@echo off
chcp 65001 > nul
title 语音输入助手

echo.
echo ==========================================
echo           语音输入助手 启动程序
echo ==========================================
echo.

cd /d %~dp0

:: 检查Python是否已安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8或更高版本
    echo 下载地址: https://www.python.org/downloads/
    timeout /t 5 /nobreak >nul 2>&1
    exit /b 1
)

:: 检查是否为首次运行
if not exist "config" (
    echo 首次运行，正在初始化...
    echo.
    echo 安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo 依赖包安装失败，请检查网络连接
        timeout /t 5 /nobreak >nul 2>&1
        exit /b 1
    )
    echo 依赖包安装完成！
    echo.
)

:: 启动程序
echo 启动语音输入助手...
python start.py

if errorlevel 1 (
    echo.
    echo 程序启动失败，请查看错误信息
    timeout /t 5 /nobreak >nul 2>&1
)

exit /b 0 