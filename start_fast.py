#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语音输入助手快速启动脚本
跳过环境检查，直接启动程序
"""

import sys
import os
from pathlib import Path

def main():
    """快速启动主函数"""
    print("🚀 语音输入助手快速启动中...")
    
    try:
        # 添加src目录到Python路径
        src_path = Path(__file__).parent / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        # 直接导入并运行主程序
        from main import main as main_func
        main_func()
        
    except KeyboardInterrupt:
        print("\n用户中断，程序退出")
        sys.exit(0)
    except Exception as e:
        print(f"\n程序启动失败: {e}")
        print("请尝试运行 start.py 进行完整检查")
        input("按回车键退出...")
        sys.exit(1)

if __name__ == "__main__":
    main() 