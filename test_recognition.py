#!/usr/bin/env python3
"""
语音识别测试脚本
测试语音识别功能是否正常工作
"""

import sys
import os
sys.path.insert(0, 'src')

from core.voice_recognizer import VoiceRecognizer, ContinuousVoiceRecognizer
from utils.config_manager import ConfigManager
from loguru import logger
import time

# 设置日志
logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss} | {level} | {message}")

def test_basic_recognition():
    """测试基础识别功能"""
    print("=== 基础语音识别测试 ===")
    
    config = ConfigManager()
    recognizer = VoiceRecognizer(config)
    
    results = []
    
    def on_result(text):
        results.append(text)
        print(f"✅ 识别结果: {text}")
    
    recognizer.set_callback(on_result)
    
    print("按回车开始录音5秒...")
    input()
    
    print("🎤 开始录音...")
    recognizer.start_recognition()
    time.sleep(6)
    
    if results:
        print(f"✅ 基础识别测试通过: {results[0]}")
        return True
    else:
        print("❌ 基础识别测试失败")
        return False

def test_continuous_recognition():
    """测试连续识别功能"""
    print("\n=== 连续语音识别测试 ===")
    
    config = ConfigManager()
    recognizer = ContinuousVoiceRecognizer(config)
    
    results = []
    
    def on_result(text):
        results.append(text)
        print(f"✅ 识别结果: {text}")
    
    recognizer.set_callback(on_result)
    
    print("按回车开始连续识别（说话会自动触发）...")
    input()
    
    print("🎤 连续识别已启动，请说话...")
    recognizer.start_continuous_recognition()
    
    print("等待15秒测试连续识别...")
    time.sleep(15)
    
    recognizer.stop_recognition()
    
    if results:
        print(f"✅ 连续识别测试通过，共识别 {len(results)} 次")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result}")
        return True
    else:
        print("❌ 连续识别测试失败")
        return False

def main():
    """主测试函数"""
    print("语音识别功能测试")
    print("=" * 40)
    
    try:
        # 测试基础识别
        basic_ok = test_basic_recognition()
        
        # 测试连续识别
        continuous_ok = test_continuous_recognition()
        
        # 总结
        print("\n" + "=" * 40)
        print("测试结果:")
        print(f"基础识别: {'✅ 通过' if basic_ok else '❌ 失败'}")
        print(f"连续识别: {'✅ 通过' if continuous_ok else '❌ 失败'}")
        
        if basic_ok and continuous_ok:
            print("🎉 所有测试通过！语音识别功能正常")
        else:
            print("⚠️  部分测试失败，请检查配置")
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 