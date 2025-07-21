"""
主窗口界面
语音输入助手的主要设置界面
"""

import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTabWidget, QLabel, QLineEdit, QPushButton, 
                             QComboBox, QCheckBox, QSlider, QSpinBox, 
                             QTextEdit, QGroupBox, QGridLayout, QMessageBox,
                             QSystemTrayIcon, QFrame, QProgressBar, QListWidget,
                             QListWidgetItem, QSplitter, QFileDialog, QStatusBar)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPalette, QColor
from loguru import logger
import json
import os
from pathlib import Path


class VoiceTestThread(QThread):
    """语音测试线程"""
    finished = pyqtSignal(str)
    
    def __init__(self, voice_recognizer):
        super().__init__()
        self.voice_recognizer = voice_recognizer
        
    def run(self):
        """运行语音测试"""
        original_callback = None
        try:
            # 设置临时回调
            original_callback = self.voice_recognizer.callback
            result_text = ""
            
            def test_callback(text):
                nonlocal result_text
                if text.strip():  # 避免空文本
                    result_text = text
                
            self.voice_recognizer.set_callback(test_callback)
            self.voice_recognizer.start_recognition()
            
            # 等待识别完成
            while self.voice_recognizer.is_recording:
                self.msleep(100)
                
            self.finished.emit(result_text)
            
        except Exception as e:
            logger.error(f"语音测试失败: {e}")
            self.finished.emit(f"测试失败: {e}")
        finally:
            # 确保恢复原回调
            if original_callback is not None:
                self.voice_recognizer.set_callback(original_callback)


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self, config_manager, voice_recognizer, assistant=None):
        super().__init__()
        self.config = config_manager
        self.voice_recognizer = voice_recognizer
        self.assistant = assistant  # 添加assistant引用
        
        self.init_ui()
        self.load_settings()
        self.setup_connections()
        
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("语音输入助手 - 设置")
        self.setGeometry(100, 100, 800, 600)
        
        # 设置窗口图标
        self.setWindowIcon(QIcon())
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 创建各个标签页
        self.create_voice_tab()
        self.create_hotkey_tab()
        self.create_input_tab()
        self.create_llm_tab()
        self.create_ui_tab()
        self.create_about_tab()
        
        # 创建按钮区域
        button_layout = QHBoxLayout()
        
        self.test_button = QPushButton("测试语音识别")
        self.test_button.clicked.connect(self.test_voice_recognition)
        button_layout.addWidget(self.test_button)
        
        button_layout.addStretch()
        
        self.save_button = QPushButton("保存设置")
        self.save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.close)
        button_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(button_layout)
        
        # 创建状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("准备就绪")
        
        # 应用样式
        self.apply_style()
        
    def create_voice_tab(self):
        """创建语音识别标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 语音识别模型设置
        model_group = QGroupBox("语音识别模型")
        model_layout = QGridLayout(model_group)
        
        model_layout.addWidget(QLabel("Whisper模型:"), 0, 0)
        self.model_combo = QComboBox()
        self.model_combo.addItems(["tiny", "base", "small", "medium", "large", "turbo"])
        model_layout.addWidget(self.model_combo, 0, 1)
        
        model_layout.addWidget(QLabel("语言:"), 1, 0)
        self.language_combo = QComboBox()
        self.language_combo.addItems(["zh", "en", "auto"])
        model_layout.addWidget(self.language_combo, 1, 1)
        
        layout.addWidget(model_group)
        
        # 录音设置
        record_group = QGroupBox("录音设置")
        record_layout = QGridLayout(record_group)
        
        record_layout.addWidget(QLabel("手动录音时长(秒):"), 0, 0)
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 30)
        self.duration_spin.setValue(5)
        record_layout.addWidget(self.duration_spin, 0, 1)
        
        record_layout.addWidget(QLabel("采样率:"), 1, 0)
        self.sample_rate_combo = QComboBox()
        self.sample_rate_combo.addItems(["16000", "22050", "44100", "48000"])
        record_layout.addWidget(self.sample_rate_combo, 1, 1)
        
        self.noise_reduction_check = QCheckBox("启用降噪")
        record_layout.addWidget(self.noise_reduction_check, 2, 0, 1, 2)
        
        self.auto_stop_check = QCheckBox("自动停止录音")
        record_layout.addWidget(self.auto_stop_check, 3, 0, 1, 2)
        
        layout.addWidget(record_group)
        
        # 连续识别设置
        continuous_group = QGroupBox("连续识别设置")
        continuous_layout = QGridLayout(continuous_group)
        
        continuous_layout.addWidget(QLabel("语音检测阈值:"), 0, 0)
        self.vad_threshold_slider = QSlider(Qt.Horizontal)
        self.vad_threshold_slider.setRange(5, 50)  # 0.005 到 0.050
        self.vad_threshold_slider.setValue(20)  # 默认 0.020
        continuous_layout.addWidget(self.vad_threshold_slider, 0, 1)
        
        self.vad_threshold_label = QLabel("0.020")
        continuous_layout.addWidget(self.vad_threshold_label, 0, 2)
        
        continuous_layout.addWidget(QLabel("连续录音时长(秒):"), 1, 0)
        self.auto_duration_spin = QSpinBox()
        self.auto_duration_spin.setRange(1, 10)
        self.auto_duration_spin.setValue(3)  # 默认3秒
        self.auto_duration_spin.setSingleStep(1)
        continuous_layout.addWidget(self.auto_duration_spin, 1, 1)
        
        continuous_layout.addWidget(QLabel("录音间隔时间(秒):"), 2, 0)
        self.cooldown_spin = QSpinBox()
        self.cooldown_spin.setRange(0, 5)
        self.cooldown_spin.setValue(1)  # 默认1秒
        self.cooldown_spin.setSingleStep(1)
        continuous_layout.addWidget(self.cooldown_spin, 2, 1)
        
        # 动态录音开关
        self.dynamic_recording_check = QCheckBox("启用智能动态录音")
        self.dynamic_recording_check.setChecked(True)  # 默认启用
        continuous_layout.addWidget(self.dynamic_recording_check, 3, 0, 1, 2)
        
        # 添加说明文字
        help_label = QLabel("语音检测阈值：数值越小越敏感，但可能误触发")
        help_label.setStyleSheet("color: #666; font-size: 11px;")
        continuous_layout.addWidget(help_label, 4, 0, 1, 3)
        
        dynamic_help_label = QLabel("智能动态录音：根据语音长度自动调整录音时间（2秒说话录2秒，5秒说话录5秒）")
        dynamic_help_label.setStyleSheet("color: #666; font-size: 11px;")
        continuous_layout.addWidget(dynamic_help_label, 5, 0, 1, 3)
        
        layout.addWidget(continuous_group)
        
        # 高级设置
        advanced_group = QGroupBox("高级设置")
        advanced_layout = QGridLayout(advanced_group)
        
        advanced_layout.addWidget(QLabel("静音阈值:"), 0, 0)
        self.silence_threshold_slider = QSlider(Qt.Horizontal)
        self.silence_threshold_slider.setRange(1, 100)
        self.silence_threshold_slider.setValue(1)
        advanced_layout.addWidget(self.silence_threshold_slider, 0, 1)
        
        self.silence_threshold_label = QLabel("0.01")
        advanced_layout.addWidget(self.silence_threshold_label, 0, 2)
        
        advanced_layout.addWidget(QLabel("最小录音长度(秒):"), 1, 0)
        self.min_length_spin = QSpinBox()
        self.min_length_spin.setRange(1, 10)
        self.min_length_spin.setValue(1)
        advanced_layout.addWidget(self.min_length_spin, 1, 1)
        
        layout.addWidget(advanced_group)
        
        # 连接信号
        self.silence_threshold_slider.valueChanged.connect(
            lambda v: self.silence_threshold_label.setText(f"{v/100:.2f}")
        )
        
        self.vad_threshold_slider.valueChanged.connect(
            lambda v: self.vad_threshold_label.setText(f"{v/1000:.3f}")
        )
        
        layout.addStretch()
        self.tab_widget.addTab(widget, "语音识别")
        
    def create_hotkey_tab(self):
        """创建热键设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 热键设置
        hotkey_group = QGroupBox("热键设置")
        hotkey_layout = QGridLayout(hotkey_group)
        
        hotkey_layout.addWidget(QLabel("开始录音:"), 0, 0)
        self.start_hotkey_edit = QLineEdit()
        self.start_hotkey_edit.setPlaceholderText("按下热键...")
        hotkey_layout.addWidget(self.start_hotkey_edit, 0, 1)
        
        hotkey_layout.addWidget(QLabel("停止录音:"), 1, 0)
        self.stop_hotkey_edit = QLineEdit()
        self.stop_hotkey_edit.setPlaceholderText("按下热键...")
        hotkey_layout.addWidget(self.stop_hotkey_edit, 1, 1)
        
        hotkey_layout.addWidget(QLabel("切换录音:"), 2, 0)
        self.toggle_hotkey_edit = QLineEdit()
        self.toggle_hotkey_edit.setPlaceholderText("按下热键...")
        hotkey_layout.addWidget(self.toggle_hotkey_edit, 2, 1)
        
        hotkey_layout.addWidget(QLabel("显示窗口:"), 3, 0)
        self.show_window_hotkey_edit = QLineEdit()
        self.show_window_hotkey_edit.setPlaceholderText("按下热键...")
        hotkey_layout.addWidget(self.show_window_hotkey_edit, 3, 1)
        
        layout.addWidget(hotkey_group)
        
        # 帮助信息
        help_group = QGroupBox("热键说明")
        help_layout = QVBoxLayout(help_group)
        
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setMaximumHeight(120)
        help_text.setPlainText("""
热键格式说明：
- 单个键：F9, Space, Enter 等
- 组合键：Ctrl+F9, Alt+Space, Shift+Enter 等
- 支持的修饰键：Ctrl, Alt, Shift, Win

常用热键建议：
- 开始录音：F9 或 Ctrl+Space
- 停止录音：F10 或 Ctrl+Shift+Space
- 切换录音：F11
- 显示窗口：Ctrl+F12
        """)
        help_layout.addWidget(help_text)
        
        layout.addWidget(help_group)
        
        layout.addStretch()
        self.tab_widget.addTab(widget, "热键设置")
        
    def create_input_tab(self):
        """创建文本输入标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 输入方式设置
        input_group = QGroupBox("输入方式")
        input_layout = QGridLayout(input_group)
        
        input_layout.addWidget(QLabel("输入方式:"), 0, 0)
        self.input_method_combo = QComboBox()
        self.input_method_combo.addItems(["clipboard", "typing", "sendkeys"])
        input_layout.addWidget(self.input_method_combo, 0, 1)
        
        self.smart_mode_check = QCheckBox("启用智能模式")
        input_layout.addWidget(self.smart_mode_check, 1, 0, 1, 2)
        
        layout.addWidget(input_group)
        
        # 文本处理设置
        text_group = QGroupBox("文本处理")
        text_layout = QGridLayout(text_group)
        
        self.auto_capitalize_check = QCheckBox("自动首字母大写")
        text_layout.addWidget(self.auto_capitalize_check, 0, 0)
        
        self.auto_punctuation_check = QCheckBox("自动添加标点")
        text_layout.addWidget(self.auto_punctuation_check, 0, 1)
        
        text_layout.addWidget(QLabel("打字速度:"), 1, 0)
        self.typing_speed_slider = QSlider(Qt.Horizontal)
        self.typing_speed_slider.setRange(1, 100)
        self.typing_speed_slider.setValue(50)
        text_layout.addWidget(self.typing_speed_slider, 1, 1)
        
        layout.addWidget(text_group)
        
        # 应用程序特定设置
        app_group = QGroupBox("应用程序特定设置")
        app_layout = QVBoxLayout(app_group)
        
        app_help = QLabel("为不同应用程序设置特定的输入行为")
        app_help.setStyleSheet("color: #666; font-size: 11px;")
        app_layout.addWidget(app_help)
        
        self.app_list = QListWidget()
        self.app_list.addItem("Excel - 优化表格输入")
        self.app_list.addItem("Word - 优化文档输入")
        self.app_list.addItem("微信 - 优化聊天输入")
        self.app_list.addItem("QQ - 优化聊天输入")
        app_layout.addWidget(self.app_list)
        
        layout.addWidget(app_group)
        
        layout.addStretch()
        self.tab_widget.addTab(widget, "文本输入")
        
    def create_llm_tab(self):
        """创建大模型优化标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 大模型设置
        llm_group = QGroupBox("大模型优化")
        llm_layout = QGridLayout(llm_group)
        
        self.llm_enabled_check = QCheckBox("启用大模型优化")
        llm_layout.addWidget(self.llm_enabled_check, 0, 0, 1, 2)
        
        llm_layout.addWidget(QLabel("提供商:"), 1, 0)
        self.llm_provider_combo = QComboBox()
        self.llm_provider_combo.addItems(["OpenAI", "Azure OpenAI", "本地模型"])
        llm_layout.addWidget(self.llm_provider_combo, 1, 1)
        
        llm_layout.addWidget(QLabel("模型:"), 2, 0)
        self.llm_model_combo = QComboBox()
        self.llm_model_combo.addItems(["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"])
        llm_layout.addWidget(self.llm_model_combo, 2, 1)
        
        llm_layout.addWidget(QLabel("API Key:"), 3, 0)
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        self.api_key_edit.setPlaceholderText("请输入API Key...")
        llm_layout.addWidget(self.api_key_edit, 3, 1)
        
        llm_layout.addWidget(QLabel("API Base:"), 4, 0)
        self.api_base_edit = QLineEdit()
        self.api_base_edit.setPlaceholderText("https://api.openai.com/v1")
        llm_layout.addWidget(self.api_base_edit, 4, 1)
        
        layout.addWidget(llm_group)
        
        # 优化参数
        param_group = QGroupBox("优化参数")
        param_layout = QGridLayout(param_group)
        
        param_layout.addWidget(QLabel("温度:"), 0, 0)
        self.temperature_slider = QSlider(Qt.Horizontal)
        self.temperature_slider.setRange(0, 100)
        self.temperature_slider.setValue(30)
        param_layout.addWidget(self.temperature_slider, 0, 1)
        
        self.temperature_label = QLabel("0.3")
        param_layout.addWidget(self.temperature_label, 0, 2)
        
        param_layout.addWidget(QLabel("最大令牌数:"), 1, 0)
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(50, 1000)
        self.max_tokens_spin.setValue(200)
        param_layout.addWidget(self.max_tokens_spin, 1, 1)
        
        layout.addWidget(param_group)
        
        # 系统提示词
        prompt_group = QGroupBox("系统提示词")
        prompt_layout = QVBoxLayout(prompt_group)
        
        self.system_prompt_edit = QTextEdit()
        self.system_prompt_edit.setPlainText(
            "你是一个专业的文本优化助手。请对用户的语音识别文本进行优化，包括：\n"
            "1. 纠正语音识别错误\n"
            "2. 添加合适的标点符号\n"
            "3. 规范化表达\n"
            "4. 保持原意不变\n"
            "请直接返回优化后的文本，不要添加任何解释。"
        )
        prompt_layout.addWidget(self.system_prompt_edit)
        
        layout.addWidget(prompt_group)
        
        # 连接信号
        self.temperature_slider.valueChanged.connect(
            lambda v: self.temperature_label.setText(f"{v/100:.1f}")
        )
        
        layout.addStretch()
        self.tab_widget.addTab(widget, "大模型优化")
        
    def create_ui_tab(self):
        """创建界面设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 界面设置
        ui_group = QGroupBox("界面设置")
        ui_layout = QGridLayout(ui_group)
        
        ui_layout.addWidget(QLabel("主题:"), 0, 0)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["浅色", "深色", "自动"])
        ui_layout.addWidget(self.theme_combo, 0, 1)
        
        ui_layout.addWidget(QLabel("语言:"), 1, 0)
        self.language_ui_combo = QComboBox()
        self.language_ui_combo.addItems(["简体中文", "繁体中文", "English"])
        ui_layout.addWidget(self.language_ui_combo, 1, 1)
        
        self.start_minimized_check = QCheckBox("启动时最小化")
        ui_layout.addWidget(self.start_minimized_check, 2, 0, 1, 2)
        
        self.show_notifications_check = QCheckBox("显示通知")
        ui_layout.addWidget(self.show_notifications_check, 3, 0, 1, 2)
        
        self.always_on_top_check = QCheckBox("窗口置顶")
        ui_layout.addWidget(self.always_on_top_check, 4, 0, 1, 2)
        
        ui_layout.addWidget(QLabel("窗口透明度:"), 5, 0)
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(50, 100)
        self.opacity_slider.setValue(95)
        ui_layout.addWidget(self.opacity_slider, 5, 1)
        
        layout.addWidget(ui_group)
        
        # 日志设置
        log_group = QGroupBox("日志设置")
        log_layout = QGridLayout(log_group)
        
        log_layout.addWidget(QLabel("日志级别:"), 0, 0)
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        log_layout.addWidget(self.log_level_combo, 0, 1)
        
        log_layout.addWidget(QLabel("日志保留天数:"), 1, 0)
        self.log_retention_spin = QSpinBox()
        self.log_retention_spin.setRange(1, 30)
        self.log_retention_spin.setValue(7)
        log_layout.addWidget(self.log_retention_spin, 1, 1)
        
        layout.addWidget(log_group)
        
        layout.addStretch()
        self.tab_widget.addTab(widget, "界面设置")
        
    def create_about_tab(self):
        """创建关于标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 版本信息
        version_group = QGroupBox("版本信息")
        version_layout = QVBoxLayout(version_group)
        
        title_label = QLabel("语音输入助手")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        version_layout.addWidget(title_label)
        
        version_label = QLabel("版本: 1.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        version_layout.addWidget(version_label)
        
        desc_label = QLabel("高识别率的Windows语音输入助手")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("color: #666;")
        version_layout.addWidget(desc_label)
        
        layout.addWidget(version_group)
        
        # 功能特性
        features_group = QGroupBox("功能特性")
        features_layout = QVBoxLayout(features_group)
        
        features_text = QTextEdit()
        features_text.setReadOnly(True)
        features_text.setMaximumHeight(200)
        features_text.setPlainText("""
✓ 基于Whisper的高精度中文语音识别
✓ 支持多种文本输入方式（剪贴板、模拟键盘、Windows API）
✓ 全局热键支持，方便快捷操作
✓ 大模型优化，提升识别准确度
✓ 智能应用程序适配（Excel、Word、微信等）
✓ 系统托盘运行，不占用桌面空间
✓ 完全本地化，保护隐私安全
✓ 可自定义配置，满足不同需求
        """)
        features_layout.addWidget(features_text)
        
        layout.addWidget(features_group)
        
        # 开源信息
        open_source_group = QGroupBox("开源信息")
        open_source_layout = QVBoxLayout(open_source_group)
        
        open_source_label = QLabel("本项目基于MIT许可证开源")
        open_source_label.setAlignment(Qt.AlignCenter)
        open_source_layout.addWidget(open_source_label)
        
        layout.addWidget(open_source_group)
        
        layout.addStretch()
        self.tab_widget.addTab(widget, "关于")
        
    def setup_connections(self):
        """设置信号连接"""
        # 启用/禁用大模型相关控件
        self.llm_enabled_check.toggled.connect(self.toggle_llm_controls)
        
        # 智能模式切换
        self.smart_mode_check.toggled.connect(self.toggle_smart_mode)
        
    def toggle_llm_controls(self, enabled):
        """切换大模型控件状态"""
        controls = [
            self.llm_provider_combo, self.llm_model_combo,
            self.api_key_edit, self.api_base_edit,
            self.temperature_slider, self.max_tokens_spin,
            self.system_prompt_edit
        ]
        
        for control in controls:
            control.setEnabled(enabled)
            
    def toggle_smart_mode(self, enabled):
        """切换智能模式"""
        if enabled:
            self.status_bar.showMessage("智能模式已启用")
        else:
            self.status_bar.showMessage("智能模式已禁用")
            
    def load_settings(self):
        """加载设置"""
        try:
            # 语音识别设置
            self.model_combo.setCurrentText(self.config.get('voice_recognition', 'model', fallback='base'))
            self.language_combo.setCurrentText(self.config.get('voice_recognition', 'language', fallback='zh'))
            self.duration_spin.setValue(self.config.get('voice_recognition', 'duration', fallback=5))
            self.sample_rate_combo.setCurrentText(self.config.get('voice_recognition', 'sample_rate', fallback='16000'))
            self.noise_reduction_check.setChecked(self.config.get('voice_recognition', 'noise_reduction', fallback=True))
            self.auto_stop_check.setChecked(self.config.get('voice_recognition', 'auto_stop', fallback=True))
            
            # 连续识别设置
            vad_threshold = float(self.config.get('voice_recognition', 'vad_threshold', fallback=0.020))
            self.vad_threshold_slider.setValue(int(vad_threshold * 1000))
            self.vad_threshold_label.setText(f"{vad_threshold:.3f}")
            
            auto_duration = float(self.config.get('voice_recognition', 'auto_recording_duration', fallback=2.5))
            self.auto_duration_spin.setValue(int(auto_duration))
            
            cooldown_time = float(self.config.get('voice_recognition', 'cooldown_time', fallback=0.3))
            self.cooldown_spin.setValue(int(cooldown_time))
            
            # 动态录音设置
            dynamic_recording = self.config.get('voice_recognition', 'dynamic_recording', fallback=True)
            self.dynamic_recording_check.setChecked(dynamic_recording)
            
            # 高级设置
            silence_threshold = float(self.config.get('voice_recognition', 'silence_threshold', fallback=0.01))
            self.silence_threshold_slider.setValue(int(silence_threshold * 100))
            self.silence_threshold_label.setText(f"{silence_threshold:.2f}")
            
            min_length = float(self.config.get('voice_recognition', 'min_recording_length', fallback=0.5))
            self.min_length_spin.setValue(int(min_length))
            
            # 热键设置
            self.start_hotkey_edit.setText(self.config.get('hotkeys', 'start_recording', fallback='f9'))
            self.stop_hotkey_edit.setText(self.config.get('hotkeys', 'stop_recording', fallback='f10'))
            self.toggle_hotkey_edit.setText(self.config.get('hotkeys', 'toggle_recording', fallback='f11'))
            self.show_window_hotkey_edit.setText(self.config.get('hotkeys', 'show_window', fallback='ctrl+f12'))
            
            # 文本输入设置
            self.input_method_combo.setCurrentText(self.config.get('text_input', 'method', fallback='clipboard'))
            self.smart_mode_check.setChecked(self.config.get('text_input', 'smart_mode', fallback=True))
            self.auto_capitalize_check.setChecked(self.config.get('text_input', 'auto_capitalize', fallback=True))
            self.auto_punctuation_check.setChecked(self.config.get('text_input', 'auto_punctuation', fallback=True))
            
            # 大模型设置
            self.llm_enabled_check.setChecked(self.config.get('llm_optimization', 'enabled', fallback=False))
            self.llm_model_combo.setCurrentText(self.config.get('llm_optimization', 'model', fallback='gpt-3.5-turbo'))
            self.api_key_edit.setText(self.config.get('llm_optimization', 'api_key', fallback=''))
            self.api_base_edit.setText(self.config.get('llm_optimization', 'api_base', fallback=''))
            self.temperature_slider.setValue(int(self.config.get('llm_optimization', 'temperature', fallback=0.3) * 100))
            self.max_tokens_spin.setValue(self.config.get('llm_optimization', 'max_tokens', fallback=200))
            self.system_prompt_edit.setPlainText(self.config.get('llm_optimization', 'system_prompt', fallback=''))
            
            # 界面设置
            self.theme_combo.setCurrentText(self.config.get('ui', 'theme', fallback='light'))
            self.language_ui_combo.setCurrentText(self.config.get('ui', 'language', fallback='zh_CN'))
            self.start_minimized_check.setChecked(self.config.get('ui', 'start_minimized', fallback=True))
            self.show_notifications_check.setChecked(self.config.get('ui', 'show_notifications', fallback=True))
            self.always_on_top_check.setChecked(self.config.get('ui', 'always_on_top', fallback=False))
            self.opacity_slider.setValue(int(self.config.get('ui', 'window_opacity', fallback=0.95) * 100))
            
            # 日志设置
            self.log_level_combo.setCurrentText(self.config.get('advanced', 'log_level', fallback='INFO'))
            self.log_retention_spin.setValue(self.config.get('advanced', 'log_retention', fallback=7))
            
            # 初始化控件状态
            self.toggle_llm_controls(self.llm_enabled_check.isChecked())
            
            logger.info("设置已加载")
            
        except Exception as e:
            logger.error(f"加载设置失败: {e}")
            QMessageBox.warning(self, "错误", f"加载设置失败: {e}")
            
    def save_settings(self):
        """保存设置"""
        try:
            # 语音识别设置
            self.config.set('voice_recognition', 'model', self.model_combo.currentText())
            self.config.set('voice_recognition', 'language', self.language_combo.currentText())
            self.config.set('voice_recognition', 'duration', str(self.duration_spin.value()))
            self.config.set('voice_recognition', 'sample_rate', self.sample_rate_combo.currentText())
            self.config.set('voice_recognition', 'noise_reduction', str(self.noise_reduction_check.isChecked()))
            self.config.set('voice_recognition', 'auto_stop', str(self.auto_stop_check.isChecked()))
            
            # 连续识别设置
            self.config.set('voice_recognition', 'vad_threshold', str(self.vad_threshold_slider.value() / 1000))
            self.config.set('voice_recognition', 'auto_recording_duration', str(self.auto_duration_spin.value()))
            self.config.set('voice_recognition', 'cooldown_time', str(self.cooldown_spin.value()))
            self.config.set('voice_recognition', 'dynamic_recording', str(self.dynamic_recording_check.isChecked()))
            
            # 高级设置
            self.config.set('voice_recognition', 'silence_threshold', str(self.silence_threshold_slider.value() / 100))
            self.config.set('voice_recognition', 'min_recording_length', str(self.min_length_spin.value()))
            
            # 热键设置
            self.config.set('hotkeys', 'start_recording', self.start_hotkey_edit.text())
            self.config.set('hotkeys', 'stop_recording', self.stop_hotkey_edit.text())
            self.config.set('hotkeys', 'toggle_recording', self.toggle_hotkey_edit.text())
            self.config.set('hotkeys', 'show_window', self.show_window_hotkey_edit.text())
            
            # 文本输入设置
            self.config.set('text_input', 'method', self.input_method_combo.currentText())
            self.config.set('text_input', 'smart_mode', str(self.smart_mode_check.isChecked()))
            self.config.set('text_input', 'auto_capitalize', str(self.auto_capitalize_check.isChecked()))
            self.config.set('text_input', 'auto_punctuation', str(self.auto_punctuation_check.isChecked()))
            
            # 大模型设置
            self.config.set('llm_optimization', 'enabled', str(self.llm_enabled_check.isChecked()))
            self.config.set('llm_optimization', 'model', self.llm_model_combo.currentText())
            self.config.set('llm_optimization', 'api_key', self.api_key_edit.text())
            self.config.set('llm_optimization', 'api_base', self.api_base_edit.text())
            self.config.set('llm_optimization', 'temperature', str(self.temperature_slider.value() / 100))
            self.config.set('llm_optimization', 'max_tokens', str(self.max_tokens_spin.value()))
            self.config.set('llm_optimization', 'system_prompt', self.system_prompt_edit.toPlainText())
            
            # 界面设置
            self.config.set('ui', 'theme', self.theme_combo.currentText())
            self.config.set('ui', 'language', self.language_ui_combo.currentText())
            self.config.set('ui', 'start_minimized', str(self.start_minimized_check.isChecked()))
            self.config.set('ui', 'show_notifications', str(self.show_notifications_check.isChecked()))
            self.config.set('ui', 'always_on_top', str(self.always_on_top_check.isChecked()))
            self.config.set('ui', 'window_opacity', str(self.opacity_slider.value() / 100))
            
            # 日志设置
            self.config.set('advanced', 'log_level', self.log_level_combo.currentText())
            self.config.set('advanced', 'log_retention', str(self.log_retention_spin.value()))
            
            # 保存配置文件
            self.config.save_config()
            
            # 重新加载语音识别配置（立即生效）
            if self.assistant:
                self.assistant.reload_voice_config()
            
            logger.info("设置已保存")
            self.status_bar.showMessage("设置已保存")
            
            QMessageBox.information(self, "成功", "设置已保存并生效！")
            
        except Exception as e:
            logger.error(f"保存设置失败: {e}")
            QMessageBox.critical(self, "错误", f"保存设置失败: {e}")
            
    def test_voice_recognition(self):
        """测试语音识别"""
        try:
            self.test_button.setText("正在测试...")
            self.test_button.setEnabled(False)
            self.status_bar.showMessage("请开始说话...")
            
            # 创建测试线程
            self.test_thread = VoiceTestThread(self.voice_recognizer)
            self.test_thread.finished.connect(self.on_test_finished)
            self.test_thread.start()
            
        except Exception as e:
            logger.error(f"测试语音识别失败: {e}")
            QMessageBox.critical(self, "错误", f"测试失败: {e}")
            self.test_button.setText("测试语音识别")
            self.test_button.setEnabled(True)
            
    def on_test_finished(self, result):
        """测试完成"""
        self.test_button.setText("测试语音识别")
        self.test_button.setEnabled(True)
        
        if result:
            self.status_bar.showMessage(f"识别结果: {result}")
            QMessageBox.information(self, "测试结果", f"识别结果:\n{result}")
        else:
            self.status_bar.showMessage("测试失败或未识别到语音")
            QMessageBox.warning(self, "测试结果", "未识别到语音内容")
            
    def apply_style(self):
        """应用样式"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                background-color: white;
            }
            
            QTabBar::tab {
                background-color: #e0e0e0;
                border: 1px solid #c0c0c0;
                padding: 8px 16px;
                margin-right: 2px;
            }
            
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #c0c0c0;
                border-radius: 8px;
                margin: 8px 0;
                padding-top: 8px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }
            
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #45a049;
            }
            
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            
            QLineEdit, QComboBox, QSpinBox {
                padding: 6px;
                border: 1px solid #c0c0c0;
                border-radius: 4px;
            }
            
            QTextEdit {
                border: 1px solid #c0c0c0;
                border-radius: 4px;
            }
            
            QCheckBox {
                spacing: 8px;
            }
            
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B1B1B1, stop:1 #c4c4c4);
                margin: 2px 0;
                border-radius: 4px;
            }
            
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #8f8f8f);
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
        """)
        
    def closeEvent(self, event):
        """关闭事件"""
        # 最小化到系统托盘而不是退出
        event.ignore()
        self.hide()
        
        if self.show_notifications_check.isChecked():
            from PyQt5.QtWidgets import QSystemTrayIcon
            if QSystemTrayIcon.isSystemTrayAvailable():
                # 这里应该通过信号通知托盘图标显示消息
                pass 