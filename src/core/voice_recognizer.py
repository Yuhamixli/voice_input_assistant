"""
语音识别核心模块
支持Whisper本地识别和大模型优化
"""

import threading
import time
import numpy as np
import sounddevice as sd
import whisper
from typing import Callable, Optional
from loguru import logger
from pathlib import Path
import tempfile
import wave
import os

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class VoiceRecognizer:
    """语音识别器"""
    
    def __init__(self, config):
        self.config = config
        self.model = None
        self.is_recording = False
        self.callback: Optional[Callable[[str], None]] = None
        self.recording_thread = None
        
        # 音频参数
        self.sample_rate = 16000
        self.channels = 1
        self.chunk_size = 1024
        self.max_recording_time = 30  # 最大录音时间（秒）
        
        # 初始化模型
        self.load_model()
        
    def load_model(self):
        """加载Whisper模型"""
        try:
            model_name = self.config.get('voice_recognition', 'model', fallback='base')
            logger.info(f"正在加载Whisper模型: {model_name}")
            self.model = whisper.load_model(model_name)
            logger.info("Whisper模型加载成功")
        except Exception as e:
            logger.error(f"加载Whisper模型失败: {e}")
            raise
            
    def set_callback(self, callback: Callable[[str], None]):
        """设置识别结果回调函数"""
        self.callback = callback
        
    def start_recognition(self):
        """开始语音识别"""
        if self.is_recording:
            logger.warning("正在录音中，忽略新的识别请求")
            return
            
        self.is_recording = True
        self.recording_thread = threading.Thread(target=self._record_and_recognize)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
    def stop_recognition(self):
        """停止语音识别"""
        self.is_recording = False
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=1)
            
    def _record_and_recognize(self):
        """录音并识别"""
        try:
            logger.info("开始录音...")
            
            # 录音参数
            duration = self.config.get('voice_recognition', 'duration', fallback=5)
            
            # 录音
            audio_data = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.float32
            )
            
            # 等待录音完成
            sd.wait()
            
            if not self.is_recording:
                return
                
            logger.info("录音完成，开始识别...")
            
            # 语音识别
            text = self._recognize_audio(audio_data.flatten())
            
            if text and self.callback:
                # 可选：使用大模型优化文本
                if self.config.get('llm_optimization', 'enabled', fallback=False):
                    text = self._optimize_text_with_llm(text)
                    
                self.callback(text)
                
        except Exception as e:
            logger.error(f"语音识别过程中发生错误: {e}")
        finally:
            self.is_recording = False
            
    def _recognize_audio(self, audio_data: np.ndarray) -> str:
        """识别音频数据"""
        try:
            # 使用Whisper进行识别
            result = self.model.transcribe(
                audio_data,
                language='zh',  # 中文
                task='transcribe'
            )
            
            text = result['text'].strip()
            logger.info(f"Whisper识别结果: {text}")
            return text
            
        except Exception as e:
            logger.error(f"Whisper识别失败: {e}")
            return ""
            
    def _optimize_text_with_llm(self, text: str) -> str:
        """使用大模型优化文本"""
        if not OPENAI_AVAILABLE:
            logger.warning("OpenAI库不可用，跳过大模型优化")
            return text
            
        try:
            api_key = self.config.get('llm_optimization', 'openai_api_key', fallback='')
            if not api_key:
                logger.warning("未配置OpenAI API Key，跳过大模型优化")
                return text
                
            client = openai.OpenAI(api_key=api_key)
            
            system_prompt = """你是一个专业的文本优化助手。请对用户的语音识别文本进行优化，包括：
1. 纠正语音识别错误
2. 添加合适的标点符号
3. 规范化表达
4. 保持原意不变
请直接返回优化后的文本，不要添加任何解释。"""
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            optimized_text = response.choices[0].message.content.strip()
            logger.info(f"大模型优化后: {optimized_text}")
            return optimized_text
            
        except Exception as e:
            logger.error(f"大模型优化失败: {e}")
            return text
            
    def stop(self):
        """停止语音识别器"""
        self.stop_recognition()
        logger.info("语音识别器已停止")


class ContinuousVoiceRecognizer(VoiceRecognizer):
    """连续语音识别器"""
    
    def __init__(self, config):
        super().__init__(config)
        self.vad_threshold = 0.01  # 语音活动检测阈值
        self.silence_duration = 1.0  # 静音持续时间（秒）
        
    def start_continuous_recognition(self):
        """开始连续语音识别"""
        if self.is_recording:
            return
            
        self.is_recording = True
        self.recording_thread = threading.Thread(target=self._continuous_record_and_recognize)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
    def _continuous_record_and_recognize(self):
        """连续录音并识别"""
        logger.info("开始连续语音识别...")
        
        audio_buffer = []
        silence_start = None
        
        def audio_callback(indata, frames, time, status):
            if status:
                logger.warning(f"音频输入状态: {status}")
                
            # 计算音频能量
            energy = np.sqrt(np.mean(indata ** 2))
            
            if energy > self.vad_threshold:
                # 检测到语音
                audio_buffer.extend(indata[:, 0])
                silence_start = None
            else:
                # 静音
                if silence_start is None:
                    silence_start = time.inputBufferAdcTime
                elif time.inputBufferAdcTime - silence_start > self.silence_duration:
                    # 静音持续时间超过阈值，处理缓冲区中的音频
                    if len(audio_buffer) > 0:
                        self._process_audio_buffer(np.array(audio_buffer))
                        audio_buffer.clear()
                    silence_start = None
                    
        try:
            with sd.InputStream(
                callback=audio_callback,
                samplerate=self.sample_rate,
                channels=1,
                dtype=np.float32
            ):
                while self.is_recording:
                    time.sleep(0.1)
                    
        except Exception as e:
            logger.error(f"连续语音识别过程中发生错误: {e}")
        finally:
            self.is_recording = False
            
    def _process_audio_buffer(self, audio_data: np.ndarray):
        """处理音频缓冲区"""
        if len(audio_data) < self.sample_rate * 0.5:  # 少于0.5秒的音频忽略
            return
            
        try:
            text = self._recognize_audio(audio_data)
            if text and self.callback:
                if self.config.get('llm_optimization', 'enabled', fallback=False):
                    text = self._optimize_text_with_llm(text)
                self.callback(text)
        except Exception as e:
            logger.error(f"处理音频缓冲区时发生错误: {e}") 