#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语音输入助手启动脚本
检查环境并启动主程序
"""

import sys
import os
import subprocess
from pathlib import Path
import importlib.util

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("错误: 需要Python 3.8或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    return True

def check_requirements():
    """检查必需的包"""
    required_packages = {
        'PyQt5': 'PyQt5',
        'whisper': 'openai-whisper',
        'sounddevice': 'sounddevice',
        'pyautogui': 'pyautogui',
        'pynput': 'pynput',
        'loguru': 'loguru',
        'pywin32': 'pywin32'
    }
    
    missing_packages = []
    
    for package, pip_name in required_packages.items():
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
            missing_packages.append(pip_name)
    
    if missing_packages:
        print("错误: 缺少以下必需的包:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\n请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
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
            print("请确保麦克风已正确连接")
            return False
        
        print(f"检测到 {len(input_devices)} 个音频输入设备")
        return True
        
    except Exception as e:
        print(f"音频设备检查失败: {e}")
        return False


def safe_input(prompt, default_response='n'):
    """安全的输入函数，处理stdin丢失的情况"""
    try:
        # 检查是否有标准输入
        if not sys.stdin or not sys.stdin.isatty():
            print(f"{prompt} (自动选择: {default_response})")
            return default_response
        return input(prompt)
    except (EOFError, RuntimeError):
        print(f"{prompt} (自动选择: {default_response})")
        return default_response

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
    
    print("必需目录已创建")

def main():
    """主函数"""
    print("语音输入助手启动检查")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        safe_input("按回车键退出...")
        sys.exit(1)
    
    # 检查必需的包
    if not check_requirements():
        safe_input("按回车键退出...")
        sys.exit(1)
    
    # 创建必需目录
    create_directories()
    
    # 检查音频设备
    if not check_audio_devices():
        response = safe_input("音频设备检查失败，是否继续启动？(y/N): ", 'y')
        if response.lower() != 'y':
            sys.exit(1)
    
    # 安装Whisper模型
    if not install_whisper_model():
        response = safe_input("Whisper模型安装失败，是否继续启动？(y/N): ", 'y')
        if response.lower() != 'y':
            sys.exit(1)
    
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
        print("\n用户中断，程序退出")
        sys.exit(0)
    except Exception as e:
        print(f"\n程序启动失败: {e}")
        print("请检查错误信息并重试")
        safe_input("按回车键退出...")
        sys.exit(1)

if __name__ == "__main__":
    main() 