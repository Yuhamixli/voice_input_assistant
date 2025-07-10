#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语音输入助手静默启动脚本
无需用户交互，适合后台运行
"""

import sys
import os
import subprocess
from pathlib import Path
import time


def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("错误: 需要Python 3.8或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    return True


def check_requirements():
    """检查必需的包"""
    required_packages = [
        'PyQt5',
        'whisper', 
        'sounddevice',
        'pyautogui',
        'pynput',
        'loguru',
        'pywin32'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'whisper':
                import whisper
            elif package == 'PyQt5':
                import PyQt5
            elif package == 'sounddevice':
                import sounddevice
            elif package == 'pyautogui':
                import pyautogui
            elif package == 'pynput':
                import pynput
            elif package == 'loguru':
                import loguru
            elif package == 'pywin32':
                import win32api
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"缺少以下包: {', '.join(missing_packages)}")
        print("尝试自动安装...")
        
        try:
            # 尝试自动安装
            pip_packages = {
                'PyQt5': 'PyQt5',
                'whisper': 'openai-whisper',
                'sounddevice': 'sounddevice',
                'pyautogui': 'pyautogui',
                'pynput': 'pynput',
                'loguru': 'loguru',
                'pywin32': 'pywin32'
            }
            
            for package in missing_packages:
                pip_name = pip_packages.get(package, package)
                print(f"安装 {pip_name}...")
                subprocess.run([sys.executable, "-m", "pip", "install", pip_name], 
                             check=True, capture_output=True)
                
            print("依赖包安装完成")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"自动安装失败: {e}")
            return False
    
    return True


def check_audio_devices():
    """检查音频设备"""
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        
        # 检查是否有输入设备
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        if not input_devices:
            print("警告: 未检测到音频输入设备")
            return False
        
        print(f"检测到 {len(input_devices)} 个音频输入设备")
        return True
        
    except Exception as e:
        print(f"音频设备检查失败: {e}")
        return False


def install_whisper_model():
    """安装Whisper模型"""
    try:
        print("检查Whisper模型...")
        import whisper
        
        # 尝试加载基础模型
        model = whisper.load_model("base")
        print("Whisper基础模型已准备就绪")
        return True
        
    except Exception as e:
        print(f"Whisper模型加载失败: {e}")
        print("正在下载Whisper基础模型...")
        try:
            import whisper
            whisper.load_model("base")
            print("Whisper基础模型下载完成")
            return True
        except Exception as e2:
            print(f"Whisper模型下载失败: {e2}")
            return False


def create_directories():
    """创建必需的目录"""
    directories = [
        "config",
        "logs",
        "data",
        "temp"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)


def main():
    """主函数"""
    print("语音输入助手静默启动")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        print("Python版本不符合要求，退出")
        sys.exit(1)
    
    # 检查必需的包
    if not check_requirements():
        print("依赖包检查失败，退出")
        sys.exit(1)
    
    # 创建必需目录
    create_directories()
    
    # 检查音频设备（非必需）
    check_audio_devices()
    
    # 安装Whisper模型（非必需）
    install_whisper_model()
    
    print("\n环境检查完成，启动语音输入助手...")
    print("=" * 50)
    
    # 启动主程序
    try:
        # 添加src目录到Python路径
        src_path = Path(__file__).parent / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        # 导入并运行主程序
        from main import main as main_func
        main_func()
        
    except KeyboardInterrupt:
        print("用户中断，程序退出")
        sys.exit(0)
    except Exception as e:
        print(f"程序启动失败: {e}")
        # 记录错误但不等待用户输入
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 