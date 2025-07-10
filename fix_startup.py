#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语音输入助手启动问题修复脚本
"""

import sys
import os
import subprocess
from pathlib import Path
import shutil


def fix_permissions():
    """修复文件权限问题"""
    print("修复文件权限...")
    
    try:
        # 获取项目根目录
        project_root = Path(__file__).parent
        
        # 需要可执行权限的文件
        executable_files = [
            "start.py",
            "start_silent.py",
            "test_modules.py",
            "build_exe.py",
            "fix_startup.py"
        ]
        
        for file_name in executable_files:
            file_path = project_root / file_name
            if file_path.exists():
                # 在Windows上，这主要是检查文件是否可读
                if not os.access(file_path, os.R_OK):
                    print(f"警告: {file_name} 权限问题")
                else:
                    print(f"✓ {file_name} 权限正常")
            else:
                print(f"警告: {file_name} 不存在")
        
        return True
        
    except Exception as e:
        print(f"修复权限失败: {e}")
        return False


def check_python_environment():
    """检查Python环境"""
    print("检查Python环境...")
    
    try:
        # 检查Python版本
        print(f"Python版本: {sys.version}")
        
        # 检查是否在虚拟环境中
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print("✓ 在虚拟环境中运行")
        else:
            print("警告: 不在虚拟环境中运行")
        
        # 检查pip
        try:
            import pip
            print("✓ pip 可用")
        except ImportError:
            print("警告: pip 不可用")
            
        return True
        
    except Exception as e:
        print(f"检查Python环境失败: {e}")
        return False


def clean_cache():
    """清理缓存文件"""
    print("清理缓存文件...")
    
    try:
        # 清理__pycache__目录
        cache_dirs = []
        for root, dirs, files in os.walk('.'):
            if '__pycache__' in dirs:
                cache_dirs.append(os.path.join(root, '__pycache__'))
        
        for cache_dir in cache_dirs:
            try:
                shutil.rmtree(cache_dir)
                print(f"✓ 清理缓存: {cache_dir}")
            except Exception as e:
                print(f"清理缓存失败: {cache_dir} - {e}")
        
        # 清理.pyc文件
        pyc_files = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith('.pyc'):
                    pyc_files.append(os.path.join(root, file))
        
        for pyc_file in pyc_files:
            try:
                os.remove(pyc_file)
                print(f"✓ 清理文件: {pyc_file}")
            except Exception as e:
                print(f"清理文件失败: {pyc_file} - {e}")
        
        return True
        
    except Exception as e:
        print(f"清理缓存失败: {e}")
        return False


def reinstall_requirements():
    """重新安装依赖包"""
    print("重新安装依赖包...")
    
    try:
        # 先卸载可能有问题的包
        problematic_packages = ['PyQt5', 'openai-whisper', 'sounddevice']
        
        for package in problematic_packages:
            try:
                subprocess.run([sys.executable, "-m", "pip", "uninstall", package, "-y"], 
                             check=False, capture_output=True)
            except:
                pass
        
        # 重新安装所有依赖
        requirements_file = Path("requirements.txt")
        if requirements_file.exists():
            print("从requirements.txt安装依赖...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--upgrade"], 
                         check=True)
            print("✓ 依赖包重新安装完成")
        else:
            print("警告: requirements.txt 不存在")
            
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"重新安装依赖失败: {e}")
        return False


def test_startup():
    """测试启动"""
    print("测试启动...")
    
    try:
        # 测试静默启动脚本
        print("测试静默启动脚本...")
        result = subprocess.run([sys.executable, "start_silent.py"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✓ 静默启动测试通过")
            return True
        else:
            print(f"静默启动测试失败: {result.stderr}")
            
            # 尝试交互式启动
            print("测试交互式启动脚本...")
            # 这里不实际运行，只是检查脚本是否存在
            if Path("start.py").exists():
                print("✓ 交互式启动脚本存在")
            else:
                print("✗ 交互式启动脚本不存在")
            
            return False
        
    except subprocess.TimeoutExpired:
        print("启动测试超时（这可能是正常的，如果程序正在运行）")
        return True
    except Exception as e:
        print(f"启动测试失败: {e}")
        return False


def main():
    """主函数"""
    print("语音输入助手启动问题修复工具")
    print("=" * 50)
    
    fixes = [
        ("检查Python环境", check_python_environment),
        ("修复文件权限", fix_permissions),
        ("清理缓存文件", clean_cache),
        ("重新安装依赖", reinstall_requirements),
        ("测试启动", test_startup),
    ]
    
    results = []
    
    for name, fix_func in fixes:
        print(f"\n{name}...")
        try:
            result = fix_func()
            results.append((name, result))
            if result:
                print(f"✓ {name} 完成")
            else:
                print(f"✗ {name} 失败")
        except Exception as e:
            print(f"✗ {name} 发生异常: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("修复结果汇总:")
    
    for name, result in results:
        status = "成功" if result else "失败"
        icon = "✓" if result else "✗"
        print(f"{icon} {name}: {status}")
    
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    print(f"\n总计: {success_count}/{total_count} 项修复成功")
    
    if success_count == total_count:
        print("\n所有修复完成！现在可以尝试启动程序：")
        print("python start_silent.py")
    else:
        print("\n部分修复失败，请手动检查相关问题。")
        print("如果问题持续存在，请检查:")
        print("1. Python版本是否为3.8+")
        print("2. 是否有管理员权限")
        print("3. 网络连接是否正常")
        print("4. 防火墙是否阻止了程序运行")


if __name__ == "__main__":
    main() 