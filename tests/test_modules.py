#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语音输入助手模块测试脚本
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
current_dir = Path(__file__).parent
src_path = current_dir / "src"
sys.path.insert(0, str(src_path))


def test_imports():
    """测试模块导入"""
    print("测试模块导入...")
    
    tests = [
        ("配置管理器", "from utils.config_manager import ConfigManager"),
        ("语音识别器", "from core.voice_recognizer import VoiceRecognizer"),
        ("文本注入器", "from core.text_injector import TextInjector"),
        ("热键管理器", "from core.hotkey_manager import HotkeyManager"),
        ("主窗口", "from gui.main_window import MainWindow"),
        ("系统托盘", "from gui.tray_icon import TrayIcon"),
    ]
    
    results = []
    
    for name, import_code in tests:
        try:
            exec(import_code)
            print(f"✓ {name} 导入成功")
            results.append(True)
        except Exception as e:
            print(f"✗ {name} 导入失败: {e}")
            results.append(False)
    
    return all(results)


def test_dependencies():
    """测试依赖包"""
    print("\n测试依赖包...")
    
    dependencies = [
        ("PyQt5", "from PyQt5.QtWidgets import QApplication"),
        ("Whisper", "import whisper"),
        ("SoundDevice", "import sounddevice"),
        ("PyAutoGUI", "import pyautogui"),
        ("PyNput", "import pynput"),
        ("Loguru", "import loguru"),
        ("Win32API", "import win32api"),
        ("NumPy", "import numpy"),
        ("OpenAI", "import openai"),
    ]
    
    results = []
    
    for name, import_code in dependencies:
        try:
            exec(import_code)
            print(f"✓ {name} 可用")
            results.append(True)
        except Exception as e:
            print(f"✗ {name} 不可用: {e}")
            results.append(False)
    
    return all(results)


def test_audio_devices():
    """测试音频设备"""
    print("\n测试音频设备...")
    
    try:
        import sounddevice as sd
        
        devices = sd.query_devices()
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        
        print(f"检测到 {len(input_devices)} 个输入设备")
        
        if input_devices:
            print("输入设备:")
            for i, device in enumerate(input_devices):
                print(f"  {i}: {device['name']}")
        
        return len(input_devices) > 0
        
    except Exception as e:
        print(f"音频设备测试失败: {e}")
        return False


def main():
    """主函数"""
    print("语音输入助手模块测试")
    print("=" * 50)
    
    tests = [
        ("依赖包", test_dependencies),
        ("模块导入", test_imports),
        ("音频设备", test_audio_devices),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"测试 {name} 时发生异常: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "通过" if result else "失败"
        icon = "✓" if result else "✗"
        print(f"{icon} {name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("所有测试通过！程序应该可以正常运行。")
        return True
    else:
        print("部分测试失败，请检查相关依赖和配置。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 