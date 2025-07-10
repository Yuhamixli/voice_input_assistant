#!/usr/bin/env python3
"""
语音输入助手发布前检查脚本
"""

import os
import sys
import subprocess
import importlib
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        return False, f"Python版本过低: {sys.version}，需要3.8+"
    return True, f"Python版本正常: {sys.version}"

def check_dependencies():
    """检查依赖包"""
    required = ['openai', 'whisper', 'sounddevice', 'pyautogui', 'pynput', 
                'loguru', 'PyQt5', 'psutil', 'requests', 'numpy', 'torch',
                'python-dotenv', 'pillow', 'pyinstaller']
    
    missing = []
    for package in required:
        try:
            if package == 'PyQt5':
                import PyQt5
            elif package == 'python-dotenv':
                import dotenv
            elif package == 'pillow':
                import PIL
            elif package == 'pyinstaller':
                import PyInstaller
            else:
                importlib.import_module(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        return False, f"缺少依赖包: {missing}"
    return True, "所有依赖包已安装"

def check_files():
    """检查必要文件"""
    required = [
        'src/main.py', 'src/core/voice_recognizer.py', 'src/core/text_injector.py',
        'src/core/hotkey_manager.py', 'src/gui/main_window.py', 'src/gui/tray_icon.py',
        'src/utils/config_manager.py', 'start.py', 'start_silent.py', 'build_exe.py',
        'requirements.txt', 'env.example', 'README.md', 'LICENSE'
    ]
    
    missing = [f for f in required if not Path(f).exists()]
    if missing:
        return False, f"缺少文件: {missing}"
    return True, "所有必要文件存在"

def check_modules():
    """检查核心模块"""
    try:
        sys.path.insert(0, 'src')
        
        from utils.config_manager import ConfigManager
        config = ConfigManager()
        
        from core.voice_recognizer import VoiceRecognizer
        recognizer = VoiceRecognizer(config)
        
        from core.text_injector import TextInjector
        injector = TextInjector(config)
        
        from gui.main_window import MainWindow
        from gui.tray_icon import TrayIcon
        
        return True, "核心模块检查通过"
        
    except Exception as e:
        return False, f"核心模块检查失败: {e}"

def check_build_system():
    """检查打包系统"""
    try:
        result = subprocess.run(['pyinstaller', '--version'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            return False, "PyInstaller不可用"
        
        if not Path('build_exe.py').exists():
            return False, "build_exe.py不存在"
        
        return True, "打包系统正常"
        
    except Exception as e:
        return False, f"打包系统检查失败: {e}"

def main():
    """主函数"""
    print("=" * 50)
    print("语音输入助手 - 发布前检查")
    print("=" * 50)
    
    checks = [
        ("Python版本", check_python_version),
        ("依赖包", check_dependencies),
        ("文件结构", check_files),
        ("核心模块", check_modules),
        ("打包系统", check_build_system),
    ]
    
    passed = 0
    failed = 0
    
    for check_name, check_func in checks:
        print(f"\n📋 检查: {check_name}")
        try:
            success, result = check_func()
            if success:
                print(f"✅ 通过: {result}")
                passed += 1
            else:
                print(f"❌ 失败: {result}")
                failed += 1
        except Exception as e:
            print(f"❌ 错误: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"检查结果: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("🎉 所有检查通过！可以发布。")
        print("\n发布步骤:")
        print("1. 运行: python build_exe.py")
        print("2. 测试生成的exe文件")
        print("3. 创建GitHub Release")
        print("4. 上传便携版压缩包")
        return True
    else:
        print("⚠️  存在问题，请修复后重试。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)