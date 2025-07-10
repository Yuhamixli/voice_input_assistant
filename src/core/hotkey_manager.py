"""
热键管理模块
全局热键监听和管理
"""

import threading
import time
from typing import Callable, Optional, Dict, List
from pynput import keyboard
from loguru import logger
import win32api
import win32con
import win32gui


class HotkeyManager:
    """热键管理器"""
    
    def __init__(self):
        self.callback: Optional[Callable] = None
        self.listener: Optional[keyboard.Listener] = None
        self.is_running = False
        
        # 默认热键配置
        self.hotkey_config = {
            'key': 'f9',  # 默认热键
            'modifier': None,  # 修饰键：shift, ctrl, alt
            'press_type': 'press'  # press, release, hold
        }
        
        # 按键状态跟踪
        self.pressed_keys = set()
        self.hotkey_pressed = False
        
    def set_callback(self, callback: Callable):
        """设置热键回调函数"""
        self.callback = callback
        
    def set_hotkey(self, key: str, modifier: Optional[str] = None, press_type: str = 'press'):
        """设置热键"""
        self.hotkey_config = {
            'key': key.lower(),
            'modifier': modifier.lower() if modifier else None,
            'press_type': press_type
        }
        
        logger.info(f"热键已设置为: {self._get_hotkey_description()}")
        
        # 如果监听器正在运行，重启它
        if self.is_running:
            self.stop()
            self.start()
            
    def _get_hotkey_description(self) -> str:
        """获取热键描述"""
        desc = ""
        if self.hotkey_config['modifier']:
            desc += f"{self.hotkey_config['modifier'].upper()} + "
        desc += self.hotkey_config['key'].upper()
        return desc
        
    def start(self):
        """启动热键监听"""
        if self.is_running:
            logger.warning("热键监听器已经在运行")
            return
            
        self.is_running = True
        
        try:
            # 创建键盘监听器
            self.listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            
            # 启动监听器
            self.listener.start()
            logger.info(f"热键监听器已启动，热键: {self._get_hotkey_description()}")
            
        except Exception as e:
            logger.error(f"启动热键监听器失败: {e}")
            self.is_running = False
            raise
            
    def stop(self):
        """停止热键监听"""
        if not self.is_running:
            return
            
        self.is_running = False
        
        if self.listener:
            self.listener.stop()
            self.listener = None
            
        self.pressed_keys.clear()
        self.hotkey_pressed = False
        
        logger.info("热键监听器已停止")
        
    def _on_key_press(self, key):
        """按键按下事件"""
        try:
            # 获取按键名称
            key_name = self._get_key_name(key)
            if key_name:
                self.pressed_keys.add(key_name)
                
                # 检查是否匹配热键
                if self._is_hotkey_match() and not self.hotkey_pressed:
                    self.hotkey_pressed = True
                    
                    if self.hotkey_config['press_type'] == 'press':
                        self._trigger_hotkey()
                        
        except Exception as e:
            logger.error(f"处理按键按下事件时发生错误: {e}")
            
    def _on_key_release(self, key):
        """按键释放事件"""
        try:
            # 获取按键名称
            key_name = self._get_key_name(key)
            if key_name:
                self.pressed_keys.discard(key_name)
                
                # 检查热键释放
                if self.hotkey_pressed and not self._is_hotkey_match():
                    self.hotkey_pressed = False
                    
                    if self.hotkey_config['press_type'] == 'release':
                        self._trigger_hotkey()
                        
        except Exception as e:
            logger.error(f"处理按键释放事件时发生错误: {e}")
            
    def _get_key_name(self, key) -> Optional[str]:
        """获取按键名称"""
        try:
            if hasattr(key, 'name'):
                return key.name.lower()
            elif hasattr(key, 'char') and key.char:
                return key.char.lower()
            else:
                return str(key).lower()
        except:
            return None
            
    def _is_hotkey_match(self) -> bool:
        """检查当前按键是否匹配热键"""
        target_key = self.hotkey_config['key']
        target_modifier = self.hotkey_config['modifier']
        
        # 检查主键
        if target_key not in self.pressed_keys:
            return False
            
        # 检查修饰键
        if target_modifier:
            modifier_keys = {
                'ctrl': ['ctrl_l', 'ctrl_r', 'ctrl'],
                'shift': ['shift_l', 'shift_r', 'shift'],
                'alt': ['alt_l', 'alt_r', 'alt'],
                'cmd': ['cmd_l', 'cmd_r', 'cmd'],
                'win': ['cmd_l', 'cmd_r', 'cmd']
            }
            
            modifier_pressed = False
            for mod_key in modifier_keys.get(target_modifier, []):
                if mod_key in self.pressed_keys:
                    modifier_pressed = True
                    break
                    
            if not modifier_pressed:
                return False
                
        return True
        
    def _trigger_hotkey(self):
        """触发热键回调"""
        if self.callback:
            try:
                logger.info(f"热键被触发: {self._get_hotkey_description()}")
                # 在新线程中执行回调，避免阻塞监听器
                thread = threading.Thread(target=self.callback)
                thread.daemon = True
                thread.start()
            except Exception as e:
                logger.error(f"执行热键回调时发生错误: {e}")
                
    def get_pressed_keys(self) -> set:
        """获取当前按下的按键"""
        return self.pressed_keys.copy()
        
    def is_key_pressed(self, key: str) -> bool:
        """检查指定按键是否被按下"""
        return key.lower() in self.pressed_keys


class AdvancedHotkeyManager(HotkeyManager):
    """高级热键管理器"""
    
    def __init__(self):
        super().__init__()
        
        # 多热键配置
        self.hotkey_configs = {
            'start_recording': {
                'key': 'f9',
                'modifier': None,
                'press_type': 'press',
                'callback': None
            },
            'stop_recording': {
                'key': 'f10',
                'modifier': None,
                'press_type': 'press',
                'callback': None
            },
            'toggle_recording': {
                'key': 'f11',
                'modifier': None,
                'press_type': 'press',
                'callback': None
            },
            'show_window': {
                'key': 'f12',
                'modifier': 'ctrl',
                'press_type': 'press',
                'callback': None
            }
        }
        
        # 组合键状态
        self.combo_states = {}
        
    def set_hotkey_callback(self, name: str, callback: Callable):
        """设置指定热键的回调函数"""
        if name in self.hotkey_configs:
            self.hotkey_configs[name]['callback'] = callback
            logger.info(f"热键 {name} 的回调函数已设置")
        else:
            logger.warning(f"未找到热键配置: {name}")
            
    def add_hotkey(self, name: str, key: str, modifier: Optional[str] = None, 
                   press_type: str = 'press', callback: Optional[Callable] = None):
        """添加热键配置"""
        self.hotkey_configs[name] = {
            'key': key.lower(),
            'modifier': modifier.lower() if modifier else None,
            'press_type': press_type,
            'callback': callback
        }
        
        logger.info(f"已添加热键 {name}: {self._get_hotkey_description_for_config(name)}")
        
    def remove_hotkey(self, name: str):
        """移除热键配置"""
        if name in self.hotkey_configs:
            del self.hotkey_configs[name]
            logger.info(f"已移除热键: {name}")
        else:
            logger.warning(f"未找到热键配置: {name}")
            
    def _get_hotkey_description_for_config(self, name: str) -> str:
        """获取指定热键配置的描述"""
        if name not in self.hotkey_configs:
            return ""
            
        config = self.hotkey_configs[name]
        desc = ""
        if config['modifier']:
            desc += f"{config['modifier'].upper()} + "
        desc += config['key'].upper()
        return desc
        
    def _on_key_press(self, key):
        """按键按下事件（重写）"""
        try:
            # 获取按键名称
            key_name = self._get_key_name(key)
            if key_name:
                self.pressed_keys.add(key_name)
                
                # 检查所有热键配置
                for name, config in self.hotkey_configs.items():
                    if self._is_hotkey_match_for_config(config):
                        if name not in self.combo_states or not self.combo_states[name]:
                            self.combo_states[name] = True
                            
                            if config['press_type'] == 'press':
                                self._trigger_hotkey_for_config(name, config)
                                
        except Exception as e:
            logger.error(f"处理按键按下事件时发生错误: {e}")
            
    def _on_key_release(self, key):
        """按键释放事件（重写）"""
        try:
            # 获取按键名称
            key_name = self._get_key_name(key)
            if key_name:
                self.pressed_keys.discard(key_name)
                
                # 检查所有热键配置
                for name, config in self.hotkey_configs.items():
                    if name in self.combo_states and self.combo_states[name]:
                        if not self._is_hotkey_match_for_config(config):
                            self.combo_states[name] = False
                            
                            if config['press_type'] == 'release':
                                self._trigger_hotkey_for_config(name, config)
                                
        except Exception as e:
            logger.error(f"处理按键释放事件时发生错误: {e}")
            
    def _is_hotkey_match_for_config(self, config: dict) -> bool:
        """检查当前按键是否匹配指定热键配置"""
        target_key = config['key']
        target_modifier = config['modifier']
        
        # 检查主键
        if target_key not in self.pressed_keys:
            return False
            
        # 检查修饰键
        if target_modifier:
            modifier_keys = {
                'ctrl': ['ctrl_l', 'ctrl_r', 'ctrl'],
                'shift': ['shift_l', 'shift_r', 'shift'],
                'alt': ['alt_l', 'alt_r', 'alt'],
                'cmd': ['cmd_l', 'cmd_r', 'cmd'],
                'win': ['cmd_l', 'cmd_r', 'cmd']
            }
            
            modifier_pressed = False
            for mod_key in modifier_keys.get(target_modifier, []):
                if mod_key in self.pressed_keys:
                    modifier_pressed = True
                    break
                    
            if not modifier_pressed:
                return False
                
        return True
        
    def _trigger_hotkey_for_config(self, name: str, config: dict):
        """触发指定热键配置的回调"""
        callback = config.get('callback')
        if callback:
            try:
                logger.info(f"热键被触发: {name} - {self._get_hotkey_description_for_config(name)}")
                # 在新线程中执行回调，避免阻塞监听器
                thread = threading.Thread(target=callback)
                thread.daemon = True
                thread.start()
            except Exception as e:
                logger.error(f"执行热键回调时发生错误: {e}")
                
    def get_all_hotkeys(self) -> Dict[str, str]:
        """获取所有热键配置的描述"""
        result = {}
        for name, config in self.hotkey_configs.items():
            result[name] = self._get_hotkey_description_for_config(name)
        return result 