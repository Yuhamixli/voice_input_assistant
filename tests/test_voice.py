#!/usr/bin/env python3
"""
语音识别测试程序
用于测试语音识别功能
"""

import sys
import time
from pathlib import Path
from loguru import logger

# 添加src目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "src"))

from core.voice_recognizer import VoiceRecognizer
from core.text_injector import TextInjector
from utils.config_manager import ConfigManager

def test_callback(text: str):
    """语音识别回调函数"""
    print(f"🎤 识别结果: {text}")
    if text.strip():
        # 创建文本注入器并注入文本
        text_injector = TextInjector()
        text_injector.inject_text(text)
        print(f"✅ 文本已注入: {text}")
    else:
        print("❌ 未识别到有效文本")

def main():
    """主函数"""
    print("语音识别测试程序")
    print("=" * 50)
    print("1. 程序将初始化Whisper模型")
    print("2. 按回车键开始语音识别")
    print("3. 开始录音后，请说话")
    print("4. 输入'quit'退出程序")
    print("=" * 50)
    
    # 设置日志
    logger.remove()
    logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss} | {level} | {message}")
    
    try:
        # 创建配置管理器
        config = ConfigManager()
        
        # 创建语音识别器
        print("正在初始化语音识别器...")
        voice_recognizer = VoiceRecognizer(config)
        voice_recognizer.set_callback(test_callback)
        
        print("✅ 语音识别器初始化完成")
        
        # 交互式测试
        while True:
            user_input = input("\n按回车键开始录音，输入'quit'退出: ")
            
            if user_input.lower() == 'quit':
                break
                
            print("🎤 开始录音，请说话...")
            voice_recognizer.start_recognition()
            
            # 等待录音完成
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序运行出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("程序退出")

if __name__ == "__main__":
    main() 