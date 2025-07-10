@echo off
chcp 65001 > nul
echo ============================================
echo        语音输入助手 - 打包程序
echo ============================================
echo.

echo 正在检查环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python环境
    echo 请先安装Python 3.8+
    pause
    exit /b 1
)

echo 正在检查依赖...
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装PyInstaller...
    pip install pyinstaller
)

pip show pillow >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装Pillow...
    pip install pillow
)

echo.
echo 开始打包...
echo ============================================
python build_exe.py

echo.
echo ============================================
echo 打包完成！
echo.
echo 生成的文件：
echo - dist/语音输入助手.exe
echo - dist/语音输入助手_便携版/
echo - dist/语音输入助手_便携版.zip
echo.
echo 便携版可以直接分发给其他用户使用
echo ============================================
pause 