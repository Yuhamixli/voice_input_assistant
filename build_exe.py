#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语音输入助手打包脚本
使用PyInstaller生成exe文件
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def check_pyinstaller():
    """检查PyInstaller是否已安装"""
    try:
        import PyInstaller
        print("PyInstaller已安装")
        return True
    except ImportError:
        print("PyInstaller未安装，正在安装...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
            print("PyInstaller安装完成")
            return True
        except subprocess.CalledProcessError:
            print("PyInstaller安装失败")
            return False


def clean_build_files():
    """清理构建文件"""
    dirs_to_remove = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"已清理目录: {dir_name}")


def create_icon():
    """创建应用图标"""
    icon_path = Path('assets/icon.ico')
    if not icon_path.exists():
        print("创建默认图标...")
        try:
            from PIL import Image, ImageDraw
            
            # 创建图标
            size = 256
            image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            
            # 绘制圆形背景
            margin = 20
            draw.ellipse([margin, margin, size-margin, size-margin], 
                        fill=(76, 175, 80, 255))
            
            # 绘制麦克风
            mic_width = 40
            mic_height = 60
            mic_x = (size - mic_width) // 2
            mic_y = (size - mic_height) // 2 - 20
            
            # 麦克风主体
            draw.rounded_rectangle([mic_x, mic_y, mic_x + mic_width, mic_y + mic_height], 
                                 radius=20, fill=(255, 255, 255, 255))
            
            # 麦克风杆
            stand_width = 4
            stand_height = 30
            stand_x = (size - stand_width) // 2
            stand_y = mic_y + mic_height
            draw.rectangle([stand_x, stand_y, stand_x + stand_width, stand_y + stand_height], 
                         fill=(255, 255, 255, 255))
            
            # 麦克风底座
            base_width = 40
            base_height = 8
            base_x = (size - base_width) // 2
            base_y = stand_y + stand_height
            draw.rectangle([base_x, base_y, base_x + base_width, base_y + base_height], 
                         fill=(255, 255, 255, 255))
            
            # 保存图标
            icon_path.parent.mkdir(exist_ok=True)
            image.save(icon_path, format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (256, 256)])
            print(f"图标已创建: {icon_path}")
            
        except ImportError:
            print("PIL不可用，跳过图标创建")
        except Exception as e:
            print(f"创建图标失败: {e}")


def prepare_build_files():
    """准备构建文件"""
    print("准备构建文件...")
    
    # 创建assets目录
    assets_dir = Path('assets')
    assets_dir.mkdir(exist_ok=True)
    
    # 创建图标
    create_icon()
    
    # 复制必要文件到临时位置
    build_files = {
        'env.example': 'env.example',
        'README.md': 'README.md',
        'LICENSE': 'LICENSE'
    }
    
    for src, dst in build_files.items():
        src_path = Path(src)
        dst_path = assets_dir / dst
        if src_path.exists():
            import shutil
            shutil.copy2(src_path, dst_path)
            print(f"复制文件: {src} -> {dst_path}")


def build_exe():
    """构建exe文件"""
    print("开始构建exe文件...")
    
    try:
        # 准备构建文件
        prepare_build_files()
        
        # 检查图标文件
        icon_file = Path('assets/icon.ico')
        icon_arg = f'--icon={icon_file}' if icon_file.exists() else ''
        
        # 构建命令
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--onefile',
            '--windowed',
            '--name=语音输入助手',
            '--add-data=config;config',
            '--add-data=assets;assets',
            '--add-data=env.example;.',
            '--add-data=README.md;.',
            '--add-data=LICENSE;.',
            '--hidden-import=whisper',
            '--hidden-import=openai',
            '--hidden-import=PyQt5',
            '--hidden-import=PyQt5.QtCore',
            '--hidden-import=PyQt5.QtGui',
            '--hidden-import=PyQt5.QtWidgets',
            '--hidden-import=sounddevice',
            '--hidden-import=pyautogui',
            '--hidden-import=pynput',
            '--hidden-import=pynput.keyboard',
            '--hidden-import=pynput.mouse',
            '--hidden-import=loguru',
            '--hidden-import=win32api',
            '--hidden-import=win32con',
            '--hidden-import=win32gui',
            '--hidden-import=win32clipboard',
            '--hidden-import=psutil',
            '--hidden-import=numpy',
            '--hidden-import=torch',
            '--hidden-import=torchaudio',
            '--hidden-import=librosa',
            '--hidden-import=dotenv',
            '--exclude-module=matplotlib',
            '--exclude-module=tk',
            '--exclude-module=tkinter',
            '--clean',
            '--noconfirm',
            'start_silent.py'  # 使用静默启动脚本
        ]
        
        # 添加图标参数
        if icon_arg:
            cmd.append(icon_arg)
        
        print("执行构建命令...")
        print(f"命令: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print("构建成功!")
        print(f"输出: {result.stdout}")
        
        # 检查输出文件
        exe_path = Path('dist/语音输入助手.exe')
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"exe文件大小: {size_mb:.1f} MB")
            print(f"输出路径: {exe_path.absolute()}")
            
            # 创建便携版文件夹
            create_portable_version(exe_path)
            
        else:
            print("警告: exe文件未找到")
            
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        if e.stderr:
            print(f"错误输出: {e.stderr}")
        return False
    
    return True


def create_portable_version(exe_path):
    """创建便携版"""
    print("创建便携版...")
    
    try:
        import shutil
        
        portable_dir = Path('dist/语音输入助手_便携版')
        portable_dir.mkdir(exist_ok=True)
        
        # 复制exe文件
        shutil.copy2(exe_path, portable_dir / '语音输入助手.exe')
        
        # 复制配置文件
        config_dir = portable_dir / 'config'
        config_dir.mkdir(exist_ok=True)
        
        if Path('config/config.example.ini').exists():
            shutil.copy2('config/config.example.ini', config_dir / 'config.example.ini')
            
        # 复制环境变量示例
        if Path('env.example').exists():
            shutil.copy2('env.example', portable_dir / 'env.example')
            
        # 复制文档
        for doc_file in ['README.md', 'LICENSE']:
            if Path(doc_file).exists():
                shutil.copy2(doc_file, portable_dir / doc_file)
        
        # 创建启动脚本
        start_bat = portable_dir / '启动语音助手.bat'
        with open(start_bat, 'w', encoding='utf-8') as f:
            f.write('''@echo off
cd /d %~dp0
echo 启动语音输入助手...
"语音输入助手.exe"
pause
''')
        
        # 创建使用说明
        usage_txt = portable_dir / '使用说明.txt'
        with open(usage_txt, 'w', encoding='utf-8') as f:
            f.write('''语音输入助手便携版使用说明

1. 首次使用：
   - 确保已连接麦克风设备
   - 双击"启动语音助手.bat"或"语音输入助手.exe"启动程序
   - 程序会在系统托盘显示绿色麦克风图标

2. 基本操作：
   - 按F9键开始语音识别
   - 清晰说出要输入的内容
   - 程序自动识别并输入到当前光标位置

3. 设置大模型优化（可选）：
   - 复制env.example为.env
   - 在.env文件中填入OpenAI API Key
   - 右键托盘图标 -> 设置 -> 大模型优化 -> 启用

4. 自定义设置：
   - 右键托盘图标选择"设置"
   - 可以修改热键、录音时长、输入方式等

5. 注意事项：
   - 请在安静环境中使用
   - 保持正常语速说话
   - 支持Excel、Word、微信等各种应用

如有问题请查看README.md文件或访问项目主页。
''')
        
        print(f"便携版已创建: {portable_dir}")
        
        # 创建压缩包
        archive_path = Path('dist/语音输入助手_便携版.zip')
        shutil.make_archive(str(archive_path.with_suffix('')), 'zip', portable_dir)
        print(f"压缩包已创建: {archive_path}")
        
    except Exception as e:
        print(f"创建便携版失败: {e}")


def main():
    """主函数"""
    print("语音输入助手打包工具")
    print("=" * 50)
    
    # 检查PyInstaller
    if not check_pyinstaller():
        return False
    
    # 清理旧的构建文件
    clean_build_files()
    
    # 构建exe
    if build_exe():
        print("\n构建完成!")
        print("文件输出: dist/语音输入助手.exe")
        return True
    else:
        print("构建失败")
        return False


if __name__ == "__main__":
    main() 