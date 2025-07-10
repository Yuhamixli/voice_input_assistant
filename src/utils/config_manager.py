"""
配置管理模块
应用程序设置和配置文件管理
"""

import os
import json
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, Union
from configparser import ConfigParser
from loguru import logger

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        # 加载环境变量
        self.load_env_file()
        
        # 默认配置文件路径
        if config_file is None:
            config_dir = Path(__file__).parent.parent.parent / "config"
            config_dir.mkdir(exist_ok=True)
            config_file = config_dir / "config.ini"
            
        self.config_file = Path(config_file)
        self.config = ConfigParser()
        
        # 加载配置
        self.load_config()
        
        # 初始化默认配置
        self.init_default_config()
        
    def load_env_file(self):
        """加载.env文件"""
        if not DOTENV_AVAILABLE:
            logger.debug("python-dotenv 不可用，跳过.env文件加载")
            return
            
        env_files = ['.env', '.env.local']
        project_root = Path(__file__).parent.parent.parent
        
        for env_file in env_files:
            env_path = project_root / env_file
            if env_path.exists():
                try:
                    load_dotenv(env_path)
                    logger.info(f"已加载环境变量文件: {env_path}")
                except Exception as e:
                    logger.warning(f"加载环境变量文件失败 {env_path}: {e}")
        
    def load_config(self):
        """加载配置文件"""
        try:
            if self.config_file.exists():
                self.config.read(self.config_file, encoding='utf-8')
                logger.info(f"配置文件已加载: {self.config_file}")
            else:
                logger.info(f"配置文件不存在，将创建默认配置: {self.config_file}")
                
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            
    def save_config(self):
        """保存配置文件"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.config.write(f)
                
            logger.info(f"配置文件已保存: {self.config_file}")
            
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
            
    def init_default_config(self):
        """初始化默认配置"""
        default_config = {
            'voice_recognition': {
                'model': 'base',  # Whisper模型大小：tiny, base, small, medium, large
                'language': 'zh',  # 语言代码
                'duration': '5',  # 录音时长（秒）
                'sample_rate': '16000',  # 采样率
                'noise_reduction': 'true',  # 降噪
                'auto_stop': 'true',  # 自动停止
                'silence_threshold': '0.01',  # 静音阈值
                'min_recording_length': '1.0'  # 最小录音长度
            },
            'hotkeys': {
                'start_recording': 'f9',
                'stop_recording': 'f10',
                'toggle_recording': 'f11',
                'show_window': 'ctrl+f12'
            },
            'text_input': {
                'method': 'clipboard',  # 输入方式：clipboard, typing, sendkeys
                'smart_mode': 'true',  # 智能模式
                'auto_capitalize': 'true',  # 自动大写
                'auto_punctuation': 'true',  # 自动标点
                'typing_speed': '0.01'  # 打字速度间隔
            },
            'llm_optimization': {
                'enabled': 'false',  # 是否启用大模型优化
                'provider': 'openai',  # 提供商：openai, azure, local
                'model': 'gpt-3.5-turbo',  # 模型名称
                'api_key': '',  # API密钥
                'api_base': '',  # API基础URL
                'temperature': '0.3',  # 温度参数
                'max_tokens': '200',  # 最大令牌数
                'system_prompt': '你是一个专业的文本优化助手。请对用户的语音识别文本进行优化，包括纠正错误、添加标点、规范表达，保持原意不变。'
            },
            'ui': {
                'theme': 'light',  # 主题：light, dark, auto
                'language': 'zh_CN',  # 界面语言
                'start_minimized': 'true',  # 启动时最小化
                'show_notifications': 'true',  # 显示通知
                'window_opacity': '0.95',  # 窗口透明度
                'always_on_top': 'false'  # 总是置顶
            },
            'audio': {
                'device_index': '-1',  # 音频设备索引（-1为默认）
                'channels': '1',  # 声道数
                'chunk_size': '1024',  # 音频块大小
                'volume_threshold': '0.01',  # 音量阈值
                'noise_gate': 'true',  # 噪声门
                'audio_format': 'float32'  # 音频格式
            },
            'advanced': {
                'log_level': 'INFO',  # 日志级别
                'max_log_size': '10MB',  # 最大日志大小
                'log_retention': '7',  # 日志保留天数
                'auto_update': 'true',  # 自动更新
                'telemetry': 'false',  # 遥测数据
                'debug_mode': 'false'  # 调试模式
            }
        }
        
        # 添加缺失的配置项
        for section, options in default_config.items():
            if not self.config.has_section(section):
                self.config.add_section(section)
                
            for key, value in options.items():
                if not self.config.has_option(section, key):
                    self.config.set(section, key, value)
                    
        # 保存配置
        self.save_config()
        
    def get(self, section: str, key: str, fallback: Any = None) -> Any:
        """获取配置值，优先级：环境变量 > 配置文件 > 默认值"""
        try:
            # 1. 首先检查环境变量
            env_key = self._get_env_key(section, key)
            env_value = os.getenv(env_key)
            if env_value is not None:
                logger.debug(f"从环境变量获取配置: {env_key} = {env_value}")
                return self._convert_value(env_value, fallback)
            
            # 2. 然后检查配置文件
            if self.config.has_option(section, key):
                value = self.config.get(section, key)
                return self._convert_value(value, fallback)
            
            # 3. 返回默认值
            return fallback
                
        except Exception as e:
            logger.warning(f"获取配置失败 {section}.{key}: {e}")
            return fallback
            
    def _get_env_key(self, section: str, key: str) -> str:
        """生成环境变量键名"""
        # 特殊映射
        env_mappings = {
            ('llm_optimization', 'api_key'): 'OPENAI_API_KEY',
            ('llm_optimization', 'api_base'): 'OPENAI_API_BASE',
            ('llm_optimization', 'model'): 'OPENAI_MODEL',
            ('voice_recognition', 'model'): 'WHISPER_MODEL',
            ('voice_recognition', 'language'): 'VOICE_LANGUAGE',
            ('ui', 'theme'): 'UI_THEME',
            ('ui', 'language'): 'UI_LANGUAGE',
            ('llm_optimization', 'enabled'): 'ENABLE_LLM_OPTIMIZATION',
            ('ui', 'show_notifications'): 'ENABLE_NOTIFICATIONS',
            ('advanced', 'auto_update'): 'ENABLE_AUTO_UPDATE',
            ('advanced', 'debug_mode'): 'APP_DEBUG',
            ('advanced', 'log_level'): 'APP_LOG_LEVEL',
            ('hotkeys', 'start_recording'): 'CUSTOM_HOTKEY',
            ('voice_recognition', 'duration'): 'CUSTOM_DURATION',
        }
        
        if (section, key) in env_mappings:
            return env_mappings[(section, key)]
        
        # 默认格式：SECTION_KEY
        return f"{section.upper()}_{key.upper()}"
        
    def _convert_value(self, value: str, fallback: Any) -> Any:
        """转换值类型"""
        if isinstance(fallback, bool):
            return self._str_to_bool(value)
        elif isinstance(fallback, int):
            return int(value)
        elif isinstance(fallback, float):
            return float(value)
        else:
            return value
            
    def set(self, section: str, key: str, value: Any):
        """设置配置值"""
        try:
            if not self.config.has_section(section):
                self.config.add_section(section)
                
            self.config.set(section, key, str(value))
            
            logger.info(f"配置已更新: {section}.{key} = {value}")
            
        except Exception as e:
            logger.error(f"设置配置失败 {section}.{key}: {e}")
            
    def get_section(self, section: str) -> Dict[str, Any]:
        """获取整个配置段"""
        try:
            if self.config.has_section(section):
                return dict(self.config.items(section))
            else:
                return {}
                
        except Exception as e:
            logger.error(f"获取配置段失败 {section}: {e}")
            return {}
            
    def update_section(self, section: str, options: Dict[str, Any]):
        """更新整个配置段"""
        try:
            if not self.config.has_section(section):
                self.config.add_section(section)
                
            for key, value in options.items():
                self.config.set(section, key, str(value))
                
            logger.info(f"配置段已更新: {section}")
            
        except Exception as e:
            logger.error(f"更新配置段失败 {section}: {e}")
            
    def _str_to_bool(self, value: str) -> bool:
        """字符串转布尔值"""
        if isinstance(value, bool):
            return value
        return str(value).lower() in ('true', '1', 'yes', 'on')
        
    def reset_to_default(self):
        """重置为默认配置"""
        try:
            self.config.clear()
            self.init_default_config()
            logger.info("配置已重置为默认值")
            
        except Exception as e:
            logger.error(f"重置配置失败: {e}")
            
    def export_config(self, export_file: str):
        """导出配置到文件"""
        try:
            export_path = Path(export_file)
            
            # 根据文件扩展名选择格式
            if export_path.suffix.lower() == '.json':
                self._export_to_json(export_path)
            elif export_path.suffix.lower() in ['.yaml', '.yml']:
                self._export_to_yaml(export_path)
            else:
                # 默认导出为INI格式
                self.config.write(open(export_path, 'w', encoding='utf-8'))
                
            logger.info(f"配置已导出到: {export_path}")
            
        except Exception as e:
            logger.error(f"导出配置失败: {e}")
            
    def import_config(self, import_file: str):
        """从文件导入配置"""
        try:
            import_path = Path(import_file)
            
            if not import_path.exists():
                logger.error(f"配置文件不存在: {import_path}")
                return
                
            # 根据文件扩展名选择格式
            if import_path.suffix.lower() == '.json':
                self._import_from_json(import_path)
            elif import_path.suffix.lower() in ['.yaml', '.yml']:
                self._import_from_yaml(import_path)
            else:
                # 默认导入INI格式
                self.config.read(import_path, encoding='utf-8')
                
            self.save_config()
            logger.info(f"配置已从文件导入: {import_path}")
            
        except Exception as e:
            logger.error(f"导入配置失败: {e}")
            
    def _export_to_json(self, file_path: Path):
        """导出为JSON格式"""
        config_dict = {}
        for section in self.config.sections():
            config_dict[section] = dict(self.config.items(section))
            
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
    def _export_to_yaml(self, file_path: Path):
        """导出为YAML格式"""
        config_dict = {}
        for section in self.config.sections():
            config_dict[section] = dict(self.config.items(section))
            
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)
            
    def _import_from_json(self, file_path: Path):
        """从JSON文件导入"""
        with open(file_path, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
            
        for section, options in config_dict.items():
            if not self.config.has_section(section):
                self.config.add_section(section)
            for key, value in options.items():
                self.config.set(section, key, str(value))
                
    def _import_from_yaml(self, file_path: Path):
        """从YAML文件导入"""
        with open(file_path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)
            
        for section, options in config_dict.items():
            if not self.config.has_section(section):
                self.config.add_section(section)
            for key, value in options.items():
                self.config.set(section, key, str(value))
                
    def validate_config(self) -> bool:
        """验证配置的有效性"""
        try:
            # 检查必需的配置段
            required_sections = ['voice_recognition', 'hotkeys', 'text_input']
            for section in required_sections:
                if not self.config.has_section(section):
                    logger.error(f"缺少必需的配置段: {section}")
                    return False
                    
            # 检查Whisper模型配置
            model = self.get('voice_recognition', 'model', 'base')
            if model not in ['tiny', 'base', 'small', 'medium', 'large']:
                logger.warning(f"无效的Whisper模型: {model}")
                
            # 检查热键配置
            hotkeys = self.get_section('hotkeys')
            if not hotkeys:
                logger.warning("未配置热键")
                
            # 检查文本输入方式
            input_method = self.get('text_input', 'method', 'clipboard')
            if input_method not in ['clipboard', 'typing', 'sendkeys']:
                logger.warning(f"无效的文本输入方式: {input_method}")
                
            return True
            
        except Exception as e:
            logger.error(f"配置验证失败: {e}")
            return False
            
    def get_config_info(self) -> Dict[str, Any]:
        """获取配置信息"""
        return {
            'config_file': str(self.config_file),
            'sections': self.config.sections(),
            'total_options': sum(len(self.config.options(section)) for section in self.config.sections()),
            'file_size': self.config_file.stat().st_size if self.config_file.exists() else 0,
            'last_modified': self.config_file.stat().st_mtime if self.config_file.exists() else None
        } 