"""
语音输入助手 - 主程序入口
高识别率的Windows语音输入助手，支持大模型优化
"""

import sys
import os
import threading
from pathlib import Path
from loguru import logger
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon

# 添加src目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from gui.main_window import MainWindow
from gui.tray_icon import TrayIcon
from core.voice_recognizer import VoiceRecognizer
from core.text_injector import TextInjector
from core.hotkey_manager import HotkeyManager
from utils.config_manager import ConfigManager


class VoiceInputAssistant:
    """语音输入助手主类"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.voice_recognizer = VoiceRecognizer(self.config)
        self.text_injector = TextInjector()
        self.hotkey_manager = HotkeyManager()
        self.main_window = None
        self.tray_icon = None
        
        # 设置日志
        self.setup_logging()
        
        # 初始化组件
        self.setup_components()
        
    def setup_logging(self):
        """设置日志配置"""
        log_dir = Path(__file__).parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logger.add(
            log_dir / "voice_assistant.log",
            rotation="10 MB",
            retention="7 days",
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
        )
        
    def setup_components(self):
        """初始化各组件"""
        # 设置热键回调
        self.hotkey_manager.set_callback(self.on_hotkey_pressed)
        
        # 启动热键监听器
        self.hotkey_manager.start()
        
        # 设置语音识别回调
        self.voice_recognizer.set_callback(self.on_text_recognized)
        
        logger.info("语音输入助手初始化完成")
        
    def on_hotkey_pressed(self):
        """热键按下回调"""
        logger.info("热键被按下，开始语音识别")
        if hasattr(self, 'tray_icon'):
            self.tray_icon.set_recording_state(True)
        self.voice_recognizer.start_recognition()
        
    def on_text_recognized(self, text: str):
        """文本识别完成回调"""
        if text.strip():
            logger.info(f"识别到文本: {text}")
            if hasattr(self, 'tray_icon'):
                self.tray_icon.on_text_recognized(text)
                self.tray_icon.set_recording_state(False)
            self.text_injector.inject_text(text)
        else:
            if hasattr(self, 'tray_icon'):
                self.tray_icon.set_recording_state(False)
            
    def show_main_window(self):
        """显示主窗口"""
        if self.main_window is None:
            self.main_window = MainWindow(self.config, self.voice_recognizer)
        self.main_window.show()
        self.main_window.raise_()
        
    def quit_application(self):
        """退出应用程序"""
        logger.info("正在退出语音输入助手...")
        self.hotkey_manager.stop()
        self.voice_recognizer.stop()
        QApplication.quit()


def main():
    """主函数"""
    try:
        # 创建QApplication实例
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        
        # 检查是否支持系统托盘
        if not QSystemTrayIcon.isSystemTrayAvailable():
            logger.error("系统托盘不可用")
            sys.exit(1)
        
        # 创建语音输入助手实例
        assistant = VoiceInputAssistant()
        
        # 创建系统托盘图标
        tray_icon = TrayIcon(assistant)
        tray_icon.show()
        
        # 将托盘图标绑定到助手实例
        assistant.tray_icon = tray_icon
        
        logger.info("语音输入助手已启动")
        
        # 运行应用程序
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error(f"程序启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 