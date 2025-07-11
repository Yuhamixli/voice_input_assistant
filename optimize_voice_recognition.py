#!/usr/bin/env python3
"""
语音识别优化工具
用于测试和优化语音识别设置
"""

import sys
import time
import numpy as np
import sounddevice as sd
from pathlib import Path
from loguru import logger

# 添加src目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "src"))

from core.voice_recognizer import VoiceRecognizer
from utils.config_manager import ConfigManager


def test_microphone():
    """测试麦克风设备"""
    print("🎤 检测音频设备...")
    devices = sd.query_devices()
    
    print("\n可用的音频设备:")
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            print(f"  {i}: {device['name']} (输入通道: {device['max_input_channels']})")
    
    # 测试默认设备
    print(f"\n当前默认输入设备: {sd.query_devices(kind='input')['name']}")
    
    # 录音测试
    print("\n正在进行5秒录音测试...")
    print("请说话...")
    
    audio_data = sd.rec(5 * 16000, samplerate=16000, channels=1, dtype=np.float32)
    sd.wait()
    
    # 检查音频质量
    volume_level = np.abs(audio_data).mean()
    max_volume = np.abs(audio_data).max()
    
    print(f"音频质量检测:")
    print(f"  平均音量: {volume_level:.4f}")
    print(f"  最大音量: {max_volume:.4f}")
    
    if volume_level < 0.001:
        print("  ⚠️  音量过低，请检查麦克风设置")
    elif volume_level > 0.1:
        print("  ⚠️  音量过高，可能会产生失真")
    else:
        print("  ✅ 音量正常")
    
    return audio_data


def optimize_config():
    """优化配置"""
    print("🔧 语音识别优化配置")
    print("=" * 50)
    
    config = ConfigManager()
    
    # 1. 模型选择
    print("1. Whisper模型选择:")
    print("   - tiny: 最快，准确率低 (~39MB)")
    print("   - base: 平衡，准确率中等 (~74MB)")
    print("   - small: 较慢，准确率较高 (~244MB)")
    print("   - medium: 慢，准确率高 (~769MB)")
    print("   - large: 最慢，准确率最高 (~1550MB)")
    
    current_model = config.get('voice_recognition', 'model', fallback='base')
    print(f"   当前模型: {current_model}")
    
    new_model = input("请选择模型 (tiny/base/small/medium/large) [回车保持当前]: ").strip()
    if new_model and new_model in ['tiny', 'base', 'small', 'medium', 'large']:
        config.set('voice_recognition', 'model', new_model)
        print(f"✅ 模型已更新为: {new_model}")
    
    # 2. 录音时长
    print("\n2. 录音时长设置:")
    current_duration = config.get('voice_recognition', 'duration', fallback=10)
    print(f"   当前录音时长: {current_duration}秒")
    
    new_duration = input("请输入录音时长 (5-30秒) [回车保持当前]: ").strip()
    if new_duration and new_duration.isdigit():
        duration = int(new_duration)
        if 5 <= duration <= 30:
            config.set('voice_recognition', 'duration', duration)
            print(f"✅ 录音时长已更新为: {duration}秒")
    
    # 3. 静音检测
    print("\n3. 静音检测设置:")
    current_threshold = config.get('voice_recognition', 'silence_threshold', fallback=0.01)
    print(f"   当前静音阈值: {current_threshold}")
    print("   阈值越低越敏感，越高越不敏感")
    
    new_threshold = input("请输入静音阈值 (0.001-0.1) [回车保持当前]: ").strip()
    if new_threshold:
        try:
            threshold = float(new_threshold)
            if 0.001 <= threshold <= 0.1:
                config.set('voice_recognition', 'silence_threshold', threshold)
                print(f"✅ 静音阈值已更新为: {threshold}")
        except ValueError:
            print("❌ 请输入有效的数值")
    
    # 4. 大模型优化
    print("\n4. 大模型优化 (可显著提高准确率):")
    current_enabled = config.get('llm_optimization', 'enabled', fallback=False)
    print(f"   当前状态: {'启用' if current_enabled else '禁用'}")
    
    if not current_enabled:
        enable_llm = input("是否启用大模型优化? (y/n) [回车跳过]: ").strip().lower()
        if enable_llm == 'y':
            api_key = input("请输入OpenAI API Key: ").strip()
            if api_key:
                config.set('llm_optimization', 'enabled', True)
                config.set('llm_optimization', 'api_key', api_key)
                print("✅ 大模型优化已启用")
    
    # 保存配置
    config.save_config()
    print("\n✅ 配置已保存")


def test_recognition_with_config():
    """使用当前配置测试识别"""
    print("🎯 测试语音识别准确率")
    print("=" * 50)
    
    config = ConfigManager()
    
    # 显示当前配置
    print("当前配置:")
    print(f"  模型: {config.get('voice_recognition', 'model', fallback='base')}")
    print(f"  录音时长: {config.get('voice_recognition', 'duration', fallback=10)}秒")
    print(f"  静音阈值: {config.get('voice_recognition', 'silence_threshold', fallback=0.01)}")
    print(f"  大模型优化: {'启用' if config.get('llm_optimization', 'enabled', fallback=False) else '禁用'}")
    
    # 创建语音识别器
    try:
        voice_recognizer = VoiceRecognizer(config)
        
        def on_recognition(text):
            print(f"\n🎤 识别结果: '{text}'")
            print(f"字符数: {len(text)}")
            if text.strip():
                print("✅ 识别成功")
            else:
                print("❌ 未识别到文本")
        
        voice_recognizer.set_callback(on_recognition)
        
        # 进行多次测试
        test_phrases = [
            "请说一个简单的句子",
            "请说一个较长的句子，包含标点符号",
            "请说一些专业术语或数字",
            "请随意说话测试"
        ]
        
        for i, phrase in enumerate(test_phrases, 1):
            print(f"\n第{i}次测试: {phrase}")
            input("按回车键开始录音...")
            
            print("🔴 开始录音...")
            voice_recognizer.start_recognition()
            
            # 等待录音完成
            time.sleep(float(config.get('voice_recognition', 'duration', fallback=10)) + 2)
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")


def main():
    """主函数"""
    print("🚀 语音识别优化工具")
    print("=" * 50)
    
    while True:
        print("\n请选择操作:")
        print("1. 测试麦克风")
        print("2. 优化配置")
        print("3. 测试识别准确率")
        print("4. 退出")
        
        choice = input("\n请输入选项 (1-4): ").strip()
        
        if choice == '1':
            test_microphone()
        elif choice == '2':
            optimize_config()
        elif choice == '3':
            test_recognition_with_config()
        elif choice == '4':
            print("👋 再见！")
            break
        else:
            print("❌ 无效选项，请重新输入")


if __name__ == "__main__":
    main() 