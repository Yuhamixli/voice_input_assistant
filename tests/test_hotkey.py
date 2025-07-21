#!/usr/bin/env python3
"""
热键测试程序
用于测试F9热键是否正常工作
"""

import sys
import time
from pathlib import Path
from loguru import logger

# 添加src目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "src"))

from core.hotkey_manager import HotkeyManager

def test_callback():
    """测试回调函数"""
    print("🎉 F9热键被触发了！")
    logger.info("F9热键测试成功")

def main():
    """主函数"""
    print("热键测试程序启动")
    print("=" * 50)
    print("1. 当你看到'热键监听器已启动'消息后")
    print("2. 按下F9键测试热键功能")
    print("3. 按Ctrl+C退出程序")
    print("=" * 50)
    
    # 设置更详细的日志
    logger.remove()
    logger.add(sys.stdout, level="DEBUG", format="{time:HH:mm:ss} | {level} | {message}")
    
    # 创建热键管理器
    hotkey_manager = HotkeyManager()
    
    try:
        # 设置热键回调
        hotkey_manager.set_callback(test_callback)
        
        # 启动热键监听器
        hotkey_manager.start()
        
        # 保持程序运行
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n正在退出程序...")
        hotkey_manager.stop()
        print("程序已退出")
    except Exception as e:
        print(f"程序运行出错: {e}")
        hotkey_manager.stop()

if __name__ == "__main__":
    main() 