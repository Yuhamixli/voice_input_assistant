#!/usr/bin/env python3
"""
简单的键盘监听测试程序
用于测试键盘监听是否正常工作
"""

import sys
from pynput import keyboard

def on_press(key):
    """按键按下事件"""
    try:
        if hasattr(key, 'name'):
            key_name = key.name
            print(f"特殊键按下: {key_name}")
            
            # 检查是否是F9键
            if key_name.lower() == 'f9':
                print("🎉 检测到F9键!")
                
        elif hasattr(key, 'char') and key.char:
            print(f"字符键按下: {key.char}")
        else:
            print(f"其他键按下: {key}")
            
    except Exception as e:
        print(f"处理按键事件时出错: {e}")

def on_release(key):
    """按键释放事件"""
    # 按ESC键退出
    if key == keyboard.Key.esc:
        print("检测到ESC键，退出程序...")
        return False

def main():
    """主函数"""
    print("简单键盘监听测试程序")
    print("=" * 50)
    print("1. 程序将监听所有键盘按键")
    print("2. 按下F9键测试功能键检测")
    print("3. 按ESC键退出程序")
    print("=" * 50)
    
    try:
        # 启动键盘监听
        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            print("键盘监听器已启动，请按键测试...")
            listener.join()
            
    except Exception as e:
        print(f"程序运行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 