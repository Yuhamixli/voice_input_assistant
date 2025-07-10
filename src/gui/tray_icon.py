"""
系统托盘图标
语音输入助手的系统托盘界面
"""

from PyQt5.QtWidgets import (QSystemTrayIcon, QMenu, QAction, QMessageBox, 
                             QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QFrame, QTextEdit)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from loguru import logger
import sys
from pathlib import Path


class StatusWidget(QWidget):
    """状态显示小窗口"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("语音输入助手 - 状态")
        self.setFixedSize(300, 200)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
        # 设置样式
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: white;
                border-radius: 10px;
            }
            QLabel {
                color: #ffffff;
                font-size: 12px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("语音输入助手")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # 状态信息
        self.status_label = QLabel("准备就绪")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # 热键提示
        hotkey_label = QLabel("按 F9 开始语音识别")
        hotkey_label.setAlignment(Qt.AlignCenter)
        hotkey_label.setStyleSheet("color: #cccccc; font-size: 10px;")
        layout.addWidget(hotkey_label)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #555555;")
        layout.addWidget(line)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.settings_button = QPushButton("设置")
        self.settings_button.clicked.connect(self.show_settings)
        button_layout.addWidget(self.settings_button)
        
        self.quit_button = QPushButton("退出")
        self.quit_button.clicked.connect(self.quit_app)
        button_layout.addWidget(self.quit_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 自动隐藏定时器
        self.hide_timer = QTimer()
        self.hide_timer.timeout.connect(self.hide)
        
    def show_settings(self):
        """显示设置"""
        # 这里需要通过信号通知主程序显示设置窗口
        pass
        
    def quit_app(self):
        """退出应用"""
        QApplication.quit()
        
    def update_status(self, status):
        """更新状态"""
        self.status_label.setText(status)
        
    def show_temporary(self, duration=3000):
        """临时显示"""
        self.show()
        self.hide_timer.start(duration)
        
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.LeftButton:
            self.hide()


class TrayIcon(QSystemTrayIcon):
    """系统托盘图标"""
    
    # 自定义信号
    show_settings_signal = pyqtSignal()
    
    def __init__(self, assistant):
        super().__init__()
        self.assistant = assistant
        self.status_widget = StatusWidget()
        
        # 创建托盘图标
        self.create_icon()
        
        # 创建右键菜单
        self.create_menu()
        
        # 设置信号连接
        self.setup_connections()
        
        # 设置提示文本
        self.setToolTip("语音输入助手 - 准备就绪")
        
        logger.info("系统托盘图标已创建")
        
    def create_icon(self):
        """创建托盘图标"""
        # 创建一个简单的图标
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制圆形背景
        painter.setBrush(QColor(76, 175, 80))  # 绿色
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 32, 32)
        
        # 绘制麦克风图标
        painter.setBrush(QColor(255, 255, 255))
        painter.drawEllipse(12, 6, 8, 12)  # 麦克风主体
        painter.drawRect(15, 18, 2, 6)     # 麦克风杆
        painter.drawRect(12, 24, 8, 2)     # 麦克风底座
        
        painter.end()
        
        icon = QIcon(pixmap)
        self.setIcon(icon)
        
    def create_menu(self):
        """创建右键菜单"""
        menu = QMenu()
        
        # 状态信息
        status_action = QAction("状态: 准备就绪", self)
        status_action.setEnabled(False)
        menu.addAction(status_action)
        
        menu.addSeparator()
        
        # 开始录音
        start_action = QAction("开始录音 (F9)", self)
        start_action.triggered.connect(self.start_recording)
        menu.addAction(start_action)
        
        # 显示状态
        show_status_action = QAction("显示状态", self)
        show_status_action.triggered.connect(self.show_status)
        menu.addAction(show_status_action)
        
        menu.addSeparator()
        
        # 设置
        settings_action = QAction("设置", self)
        settings_action.triggered.connect(self.show_settings)
        menu.addAction(settings_action)
        
        # 帮助
        help_action = QAction("帮助", self)
        help_action.triggered.connect(self.show_help)
        menu.addAction(help_action)
        
        menu.addSeparator()
        
        # 退出
        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self.quit_application)
        menu.addAction(quit_action)
        
        self.setContextMenu(menu)
        
    def setup_connections(self):
        """设置信号连接"""
        # 双击托盘图标显示设置
        self.activated.connect(self.on_tray_activated)
        
        # 连接状态小窗口的信号
        self.status_widget.settings_button.clicked.connect(self.show_settings)
        self.status_widget.quit_button.clicked.connect(self.quit_application)
        
    def on_tray_activated(self, reason):
        """托盘图标激活事件"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_settings()
        elif reason == QSystemTrayIcon.Trigger:
            self.show_status()
            
    def start_recording(self):
        """开始录音"""
        try:
            self.assistant.on_hotkey_pressed()
            self.update_status("正在录音...")
            self.showMessage("语音输入助手", "开始录音", QSystemTrayIcon.Information, 2000)
        except Exception as e:
            logger.error(f"开始录音失败: {e}")
            self.showMessage("语音输入助手", f"开始录音失败: {e}", QSystemTrayIcon.Critical, 3000)
            
    def show_status(self):
        """显示状态窗口"""
        # 获取托盘图标位置
        geometry = self.geometry()
        
        # 计算状态窗口位置
        x = geometry.x() - 150
        y = geometry.y() - 220
        
        # 确保窗口在屏幕内
        screen = QApplication.desktop().screenGeometry()
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        if x + 300 > screen.width():
            x = screen.width() - 300
        if y + 200 > screen.height():
            y = screen.height() - 200
            
        self.status_widget.move(x, y)
        self.status_widget.show_temporary(5000)
        
    def show_settings(self):
        """显示设置窗口"""
        try:
            self.assistant.show_main_window()
        except Exception as e:
            logger.error(f"显示设置窗口失败: {e}")
            
    def show_help(self):
        """显示帮助信息"""
        help_text = """
语音输入助手 - 使用帮助

快捷键：
• F9 - 开始语音识别
• F10 - 停止语音识别
• F11 - 切换语音识别状态
• Ctrl+F12 - 显示设置窗口

使用步骤：
1. 按下 F9 开始录音
2. 清晰地说出要输入的内容
3. 程序会自动识别并输入到当前光标位置

支持的应用程序：
• Microsoft Word
• Microsoft Excel
• 微信
• QQ
• 记事本
• 浏览器
• 其他支持文本输入的应用

注意事项：
• 请确保麦克风正常工作
• 在安静环境中使用效果更佳
• 说话时保持正常语速
• 可在设置中调整识别参数
        """
        
        msg = QMessageBox()
        msg.setWindowTitle("使用帮助")
        msg.setText(help_text)
        msg.setIcon(QMessageBox.Information)
        msg.exec_()
        
    def quit_application(self):
        """退出应用程序"""
        reply = QMessageBox.question(
            None,
            "确认退出",
            "确定要退出语音输入助手吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.assistant.quit_application()
            
    def update_status(self, status):
        """更新状态"""
        self.setToolTip(f"语音输入助手 - {status}")
        self.status_widget.update_status(status)
        
        # 更新菜单中的状态
        menu = self.contextMenu()
        if menu:
            actions = menu.actions()
            if actions:
                actions[0].setText(f"状态: {status}")
                
    def show_notification(self, title, message, icon=None, duration=3000):
        """显示通知"""
        if icon is None:
            icon = QSystemTrayIcon.Information
            
        self.showMessage(title, message, icon, duration)
        
    def set_recording_state(self, is_recording):
        """设置录音状态"""
        if is_recording:
            self.update_status("正在录音...")
            # 创建录音状态的图标
            self.create_recording_icon()
        else:
            self.update_status("准备就绪")
            # 恢复正常图标
            self.create_icon()
            
    def create_recording_icon(self):
        """创建录音状态图标"""
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制圆形背景（红色表示录音中）
        painter.setBrush(QColor(244, 67, 54))  # 红色
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 32, 32)
        
        # 绘制麦克风图标
        painter.setBrush(QColor(255, 255, 255))
        painter.drawEllipse(12, 6, 8, 12)  # 麦克风主体
        painter.drawRect(15, 18, 2, 6)     # 麦克风杆
        painter.drawRect(12, 24, 8, 2)     # 麦克风底座
        
        # 绘制录音指示点
        painter.setBrush(QColor(255, 255, 255))
        painter.drawEllipse(26, 6, 4, 4)
        
        painter.end()
        
        icon = QIcon(pixmap)
        self.setIcon(icon)
        
    def set_error_state(self, error_message):
        """设置错误状态"""
        self.update_status(f"错误: {error_message}")
        self.show_notification("语音输入助手", error_message, QSystemTrayIcon.Critical)
        
        # 创建错误状态的图标
        self.create_error_icon()
        
    def create_error_icon(self):
        """创建错误状态图标"""
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制圆形背景（灰色表示错误）
        painter.setBrush(QColor(158, 158, 158))  # 灰色
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 32, 32)
        
        # 绘制X图标
        painter.setPen(QColor(255, 255, 255))
        painter.drawLine(10, 10, 22, 22)
        painter.drawLine(10, 22, 22, 10)
        
        painter.end()
        
        icon = QIcon(pixmap)
        self.setIcon(icon)
        
    def on_text_recognized(self, text):
        """文本识别完成回调"""
        self.update_status("识别完成")
        self.show_notification("语音输入助手", f"识别结果: {text}", QSystemTrayIcon.Information)
        
        # 短暂显示识别结果后恢复正常状态
        QTimer.singleShot(3000, lambda: self.update_status("准备就绪"))
        
    def minimize_to_tray(self):
        """最小化到托盘"""
        self.show_notification("语音输入助手", "程序已最小化到系统托盘", QSystemTrayIcon.Information, 2000) 