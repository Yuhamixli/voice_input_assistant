#!/usr/bin/env python3
"""
API Key配置工具
快速设置OpenAI API Key以启用大模型优化
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "src"))

from utils.config_manager import ConfigManager


def setup_api_key():
    """配置API Key"""
    print("🔧 OpenAI API Key配置工具")
    print("=" * 50)
    print("大模型优化可以显著提高语音识别准确率，将类似：")
    print("  '我说请说一个脚长的句子,包含着点泡。'")
    print("  优化为：")
    print("  '我说请说一个较长的句子，包含标点符号。'")
    print()
    
    # 获取API Key
    print("请访问 https://platform.openai.com/api-keys 获取API Key")
    api_key = input("请输入你的OpenAI API Key (输入'skip'跳过): ").strip()
    
    if api_key.lower() == 'skip':
        print("⚠️  跳过API Key配置，将禁用大模型优化")
        return
    
    if not api_key or not api_key.startswith('sk-'):
        print("❌ 无效的API Key格式")
        return
    
    # 保存配置
    config = ConfigManager()
    config.set('llm_optimization', 'api_key', api_key)
    config.set('llm_optimization', 'enabled', True)
    config.save_config()
    
    print("✅ API Key配置成功！")
    print("✅ 大模型优化已启用")
    
    # 测试API Key
    print("\n🧪 测试API Key...")
    try:
        from core.voice_recognizer import VoiceRecognizer
        recognizer = VoiceRecognizer(config)
        
        # 测试优化功能
        test_text = "我说请说一个脚长的句子,包含着点泡。"
        optimized_text = recognizer._optimize_text_with_llm(test_text)
        
        print(f"测试文本: {test_text}")
        print(f"优化结果: {optimized_text}")
        print("✅ API Key测试成功！")
        
    except Exception as e:
        print(f"❌ API Key测试失败: {e}")
        print("请检查API Key是否正确，或网络连接是否正常")


def main():
    """主函数"""
    try:
        setup_api_key()
    except KeyboardInterrupt:
        print("\n用户取消配置")
    except Exception as e:
        print(f"配置过程中发生错误: {e}")


if __name__ == "__main__":
    main() 