"""
文字输入模块
将识别的文字输入到当前光标位置
"""

import time
import threading
from typing import Optional
import pyautogui
import win32api
import win32con
import win32gui
import win32process
import win32clipboard
from loguru import logger
import psutil


class TextInjector:
    """文字输入器"""
    
    def __init__(self):
        # 设置pyautogui参数
        pyautogui.FAILSAFE = False  # 禁用安全机制，避免意外触发
        pyautogui.PAUSE = 0.05  # 减少延迟提升响应速度
        
        # 输入方式配置
        self.input_methods = {
            'clipboard': self._inject_via_clipboard,
            'typing': self._inject_via_typing,
            'sendkeys': self._inject_via_sendkeys
        }
        
        # 默认输入方式
        self.default_method = 'clipboard'
        
    def inject_text(self, text: str, method: Optional[str] = None):
        """输入文字到当前光标位置"""
        if not text.strip():
            return
            
        method = method or self.default_method
        
        try:
            logger.info(f"正在使用 {method} 方式输入文字: {text}")
            
            # 获取当前活动窗口信息
            active_window = self._get_active_window_info()
            logger.info(f"当前活动窗口: {active_window}")
            
            # 添加短暂延迟，避免与系统操作冲突
            time.sleep(0.1)
            
            # 选择合适的输入方法
            if method in self.input_methods:
                self.input_methods[method](text)
            else:
                logger.warning(f"未知的输入方式: {method}，使用默认方式")
                self.input_methods[self.default_method](text)
                
            logger.info("文字输入完成")
            
        except Exception as e:
            logger.warning(f"主要输入方式失败: {e}")
            # 尝试使用备用方法
            self._inject_fallback(text)
            
    def _get_active_window_info(self) -> dict:
        """获取当前活动窗口信息"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(hwnd)
            
            # 获取窗口所属进程
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process_name = ""
            
            try:
                process = psutil.Process(pid)
                process_name = process.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
                
            return {
                'hwnd': hwnd,
                'title': window_title,
                'pid': pid,
                'process_name': process_name
            }
            
        except Exception as e:
            logger.error(f"获取活动窗口信息失败: {e}")
            return {}
            
    def _inject_via_clipboard(self, text: str):
        """通过剪贴板输入文字"""
        try:
            # 备份当前剪贴板内容
            backup_text = self._get_clipboard_text()
            
            # 将文字复制到剪贴板
            self._set_clipboard_text(text)
            
            # 短暂延迟确保剪贴板内容已更新
            time.sleep(0.1)
            
            # 发送Ctrl+V粘贴
            pyautogui.hotkey('ctrl', 'v')
            
            # 短暂延迟后恢复剪贴板内容
            time.sleep(0.2)
            if backup_text is not None:
                self._set_clipboard_text(backup_text)
                
        except Exception as e:
            logger.error(f"剪贴板输入方式失败: {e}")
            raise
            
    def _inject_via_typing(self, text: str):
        """通过模拟键盘输入文字"""
        try:
            # 直接输入文字
            pyautogui.write(text, interval=0.01)
            
        except Exception as e:
            logger.error(f"键盘输入方式失败: {e}")
            raise
            
    def _inject_via_sendkeys(self, text: str):
        """通过SendKeys输入文字"""
        try:
            # 使用Windows API发送字符
            for char in text:
                # 获取虚拟键码
                vk_code = win32api.VkKeyScan(char)
                
                if vk_code != -1:
                    # 发送按键按下和释放事件
                    win32api.keybd_event(vk_code & 0xFF, 0, 0, 0)
                    win32api.keybd_event(vk_code & 0xFF, 0, win32con.KEYEVENTF_KEYUP, 0)
                    time.sleep(0.01)
                    
        except Exception as e:
            logger.error(f"SendKeys输入方式失败: {e}")
            raise
            
    def _inject_fallback(self, text: str):
        """备用输入方法"""
        try:
            logger.info("尝试使用备用输入方法")
            
            # 按优先级尝试不同的输入方法
            backup_methods = ['sendkeys', 'typing', 'clipboard']
            
            for method_name in backup_methods:
                if method_name != self.default_method and method_name in self.input_methods:
                    try:
                        logger.info(f"尝试备用方法: {method_name}")
                        time.sleep(0.2)  # 额外延迟确保系统准备就绪
                        self.input_methods[method_name](text)
                        logger.info(f"✅ 备用方法 {method_name} 成功")
                        return
                    except Exception as e:
                        logger.warning(f"❌ 备用方法 {method_name} 失败: {e}")
                        continue
                        
            logger.error("❌ 所有输入方法都失败了")
            
        except Exception as e:
            logger.error(f"备用输入方法执行失败: {e}")
            
    def _get_clipboard_text(self) -> Optional[str]:
        """获取剪贴板文本"""
        try:
            win32clipboard.OpenClipboard()
            if win32clipboard.IsClipboardFormatAvailable(win32con.CF_TEXT):
                data = win32clipboard.GetClipboardData(win32con.CF_TEXT)
                return data.decode('utf-8') if isinstance(data, bytes) else str(data)
            return None
        except Exception as e:
            logger.warning(f"获取剪贴板内容失败: {e}")
            return None
        finally:
            try:
                win32clipboard.CloseClipboard()
            except:
                pass
                
    def _set_clipboard_text(self, text: str):
        """设置剪贴板文本"""
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text)
        except Exception as e:
            logger.error(f"设置剪贴板内容失败: {e}")
            raise
        finally:
            try:
                win32clipboard.CloseClipboard()
            except:
                pass
                
    def set_input_method(self, method: str):
        """设置输入方式"""
        if method in self.input_methods:
            self.default_method = method
            logger.info(f"输入方式已设置为: {method}")
        else:
            logger.warning(f"未知的输入方式: {method}")
            
    def get_available_methods(self) -> list:
        """获取可用的输入方式"""
        return list(self.input_methods.keys())


class SmartTextInjector(TextInjector):
    """智能文字输入器"""
    
    def __init__(self):
        super().__init__()
        
        # 应用程序特定的输入配置
        self.app_configs = {
            'excel.exe': {
                'method': 'clipboard',
                'pre_action': self._excel_pre_action,
                'post_action': self._excel_post_action
            },
            'winword.exe': {
                'method': 'clipboard',
                'pre_action': None,
                'post_action': None
            },
            'notepad.exe': {
                'method': 'typing',
                'pre_action': None,
                'post_action': None
            },
            'chrome.exe': {
                'method': 'clipboard',
                'pre_action': None,
                'post_action': None
            },
            'wechat.exe': {
                'method': 'clipboard',
                'pre_action': None,
                'post_action': self._wechat_post_action
            }
        }
        
    def inject_text(self, text: str, method: Optional[str] = None):
        """智能输入文字"""
        # 获取当前活动窗口
        window_info = self._get_active_window_info()
        process_name = window_info.get('process_name', '').lower()
        
        # 获取应用特定配置
        app_config = self.app_configs.get(process_name, {})
        
        # 选择输入方法
        if method is None:
            method = app_config.get('method', self.default_method)
            
        # 执行前置动作
        pre_action = app_config.get('pre_action')
        if pre_action:
            try:
                pre_action()
            except Exception as e:
                logger.warning(f"前置动作执行失败: {e}")
                
        # 执行文字输入
        super().inject_text(text, method)
        
        # 执行后置动作
        post_action = app_config.get('post_action')
        if post_action:
            try:
                post_action()
            except Exception as e:
                logger.warning(f"后置动作执行失败: {e}")
                
    def _excel_pre_action(self):
        """Excel前置动作"""
        # 确保单元格处于编辑状态
        pyautogui.press('f2')
        time.sleep(0.1)
        
    def _excel_post_action(self):
        """Excel后置动作"""
        # 按Enter确认输入
        pyautogui.press('enter')
        
    def _wechat_post_action(self):
        """微信后置动作"""
        # 可以选择是否自动发送
        # pyautogui.press('enter')
        pass
        
    def add_app_config(self, process_name: str, config: dict):
        """添加应用程序配置"""
        self.app_configs[process_name.lower()] = config
        logger.info(f"已添加应用程序配置: {process_name}")
        
    def remove_app_config(self, process_name: str):
        """移除应用程序配置"""
        if process_name.lower() in self.app_configs:
            del self.app_configs[process_name.lower()]
            logger.info(f"已移除应用程序配置: {process_name}")
        else:
            logger.warning(f"未找到应用程序配置: {process_name}") 