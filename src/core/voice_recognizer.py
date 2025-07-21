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
from collections import deque

try:
    import scipy.signal
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# 导入本地标点符号处理器
try:
    from .punctuation_processor import punctuation_processor
    LOCAL_PUNCTUATION_AVAILABLE = True
except ImportError:
    LOCAL_PUNCTUATION_AVAILABLE = False


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
        
        # 音频设备配置
        self.input_device_id = None
        self._setup_audio_device()
        
        # 初始化模型
        self.load_model()
        
    def _setup_audio_device(self):
        """设置音频设备"""
        try:
            # 获取可用的输入设备
            devices = sd.query_devices()
            input_devices = [i for i, d in enumerate(devices) if d['max_input_channels'] > 0]
            
            if not input_devices:
                logger.error("未找到可用的录音设备")
                return
                
            # 尝试使用配置中指定的设备
            configured_device = self.config.get('voice_recognition', 'input_device_id', fallback=None)
            if configured_device is not None:
                try:
                    configured_device = int(configured_device)
                    if configured_device in input_devices:
                        self.input_device_id = configured_device
                        logger.info(f"使用配置的录音设备: {configured_device}")
                        return
                    else:
                        logger.warning(f"配置的设备ID {configured_device} 不可用")
                except ValueError:
                    logger.warning(f"配置的设备ID格式错误: {configured_device}")
            
            # 使用默认设备
            try:
                default_device = sd.default.device
                if isinstance(default_device, tuple):
                    default_input_device = default_device[0]
                else:
                    default_input_device = default_device
                    
                if default_input_device in input_devices:
                    self.input_device_id = default_input_device
                    logger.info(f"使用默认录音设备: {default_input_device}")
                    return
            except Exception as e:
                logger.warning(f"获取默认设备失败: {e}")
            
            # 使用第一个可用的输入设备
            self.input_device_id = input_devices[0]
            logger.info(f"使用第一个可用的录音设备: {self.input_device_id}")
            
        except Exception as e:
            logger.error(f"设置音频设备失败: {e}")
            self.input_device_id = None
        
    def load_model(self):
        """加载Whisper模型"""
        try:
            # 优先使用tiny模型以提高速度
            model_name = self.config.get('voice_recognition', 'model', fallback='tiny')
            logger.info(f"正在加载Whisper模型: {model_name}")
            
            # 设置模型存储路径到项目根目录
            project_root = Path(__file__).parent.parent.parent
            models_dir = project_root / "models"
            models_dir.mkdir(exist_ok=True)
            
            # 设置WHISPER_CACHE_DIR环境变量（优先使用环境变量方式）
            os.environ['WHISPER_CACHE_DIR'] = str(models_dir)
            
            # 检查模型文件是否已存在（映射实际文件名）
            model_filename_map = {
                'tiny': 'tiny.pt',
                'base': 'base.pt', 
                'small': 'small.pt',
                'medium': 'medium.pt',
                'large': 'large-v3.pt',
                'turbo': 'large-v3-turbo.pt'
            }
            
            actual_filename = model_filename_map.get(model_name, f"{model_name}.pt")
            model_path = models_dir / actual_filename
            model_exists = model_path.exists()
            
            if model_exists:
                logger.info(f"发现已存在的模型文件: {model_path}")
                logger.info(f"正在加载本地Whisper模型: {model_name}")
            else:
                logger.info(f"模型文件不存在，开始下载到: {models_dir}")
                logger.info(f"正在下载Whisper模型: {model_name} (约800MB，请稍候...)")
            
            # 加载模型（优先使用本地文件，避免重复下载）
            if model_exists:
                # 直接从本地文件加载，避免网络检查
                self.model = whisper.load_model(str(model_path))
            else:
                # 使用download_root参数确保下载到指定目录
                self.model = whisper.load_model(model_name, download_root=str(models_dir))
            
            if model_exists:
                logger.info(f"✅ 本地Whisper模型加载成功: {model_name}")
            else:
                logger.info(f"✅ Whisper模型下载并加载成功: {model_name}")
                logger.info(f"📁 模型已保存到: {models_dir}")
            
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
            
            # 检查音频设备
            if self.input_device_id is None:
                logger.error("未配置可用的录音设备")
                return
            
            # 录音参数
            duration = self.config.get('voice_recognition', 'duration', fallback=5)
            
            # 录音
            audio_data = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.float32,
                device=self.input_device_id
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
            # 快速音频预处理
            audio_data = self._preprocess_audio_fast(audio_data)
            
            # 使用Whisper进行识别，优化参数提高速度
            result = self.model.transcribe(
                audio_data,
                language='zh',  # 中文
                task='transcribe',
                temperature=0.0,  # 降低随机性
                compression_ratio_threshold=2.0,  # 较低的压缩比阈值
                logprob_threshold=-0.8,  # 较低的概率阈值
                no_speech_threshold=0.3,  # 较低的无语音阈值
                fp16=False,  # 禁用FP16以避免某些设备的兼容性问题
                beam_size=1,  # 使用贪心搜索提高速度
                best_of=1,  # 只生成一个候选
                condition_on_previous_text=False,  # 不依赖之前的文本
                word_timestamps=False  # 不生成词级时间戳
            )
            
            text = result.get('text', '').strip()
            
            if text:
                logger.info(f"识别结果: {text}")
                return text
            else:
                logger.warning("未识别到有效文本")
                return ""
                
        except Exception as e:
            logger.error(f"音频识别失败: {e}")
            return ""
            
    def _preprocess_audio_fast(self, audio_data: np.ndarray) -> np.ndarray:
        """快速音频预处理，减少延迟"""
        
        # 检查音频有效性
        if len(audio_data) == 0 or np.all(audio_data == 0):
            logger.warning("音频数据为空或全零")
            return np.zeros(self.sample_rate, dtype=np.float32)  # 返回1秒的静音
        
        # 去除直流分量
        audio_data = audio_data - audio_data.mean()
        
        # 检查音频质量
        rms = np.sqrt(np.mean(audio_data ** 2))
        max_amplitude = np.max(np.abs(audio_data))
        
        logger.debug(f"音频预处理 - RMS: {rms:.4f}, Max: {max_amplitude:.4f}, 长度: {len(audio_data)/self.sample_rate:.2f}秒")
        
        # 归一化
        if max_amplitude > 0:
            audio_data = audio_data * (0.6 / max_amplitude)
        
        # 简单的噪声检测
        if rms < 0.001:
            logger.warning(f"音频能量过低 (RMS: {rms:.6f})，可能是静音或音量太小")
        
        # 确保数据类型为float32
        audio_data = audio_data.astype(np.float32)
        
        return audio_data

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
            
            system_prompt = """你是一个专业的中文语音识别文本优化助手。请对用户的语音识别文本进行优化，包括：
1. 纠正语音识别错误（同音字、近音字错误）
2. 添加合适的标点符号
3. 规范化表达（口语转书面语）
4. 处理数字和专业术语
5. 保持原意不变

注意：
- 优先考虑中文语境和习惯表达
- 如果原文本过于模糊或错误，保持原样
- 只返回优化后的文本，不要添加任何解释或标记"""
            
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
    
    def _add_local_punctuation(self, text: str) -> str:
        """使用本地处理器添加标点符号"""
        try:
            original_text = text
            processed_text = punctuation_processor.process(text)
            
            if processed_text != original_text:
                logger.info(f"本地标点处理: {original_text} → {processed_text}")
            else:
                logger.debug(f"本地标点处理: 文本无变化")
                
            return processed_text
            
        except Exception as e:
            logger.error(f"本地标点处理失败: {e}")
            return text
            
    def stop(self):
        """停止语音识别器"""
        self.stop_recognition()
        logger.info("语音识别器已停止")


class ContinuousVoiceRecognizer(VoiceRecognizer):
    """连续语音识别器 - 基于工作正常的基础识别器改进"""
    
    def __init__(self, config):
        super().__init__(config)
        # 保存配置引用以便热重载
        self.config = config
        self._load_continuous_params()
        
        # 状态变量
        self.is_monitoring = False
        self.is_auto_recording = False
        self.last_activity_time = 0
        self.debug_counter = 0
        
    def _load_continuous_params(self):
        """加载连续识别参数"""
        self.vad_threshold = float(self.config.get('voice_recognition', 'vad_threshold', fallback=0.020))
        self.auto_recording_duration = float(self.config.get('voice_recognition', 'auto_recording_duration', fallback=2.5))
        self.cooldown_time = float(self.config.get('voice_recognition', 'cooldown_time', fallback=0.3))
        
        # 动态录音参数
        self.dynamic_recording = self.config.get('voice_recognition', 'dynamic_recording', fallback=True)
        self.min_recording_duration = 0.5  # 最小录音时长
        self.max_recording_duration = min(self.auto_recording_duration, 10.0)  # 最大录音时长
        self.silence_duration_to_stop = 0.8  # 静音多久后停止录音
        
        logger.info(f"连续识别参数 - VAD阈值: {self.vad_threshold:.3f}, 动态录音: {self.dynamic_recording}")
        if self.dynamic_recording:
            logger.info(f"智能动态录音 - 范围: {self.min_recording_duration}-{self.max_recording_duration}秒, 静音停止: {self.silence_duration_to_stop}秒")
        else:
            logger.info(f"固定时长录音 - 时长: {self.auto_recording_duration}秒")
        
    def reload_config(self):
        """重新加载配置参数"""
        logger.info("重新加载连续识别配置...")
        self._load_continuous_params()
        logger.info("配置重载完成")
        
    def start_continuous_recognition(self):
        """开始连续监听模式"""
        if self.is_monitoring:
            logger.warning("连续监听已在运行中")
            return
            
        self.is_monitoring = True
        self.recording_thread = threading.Thread(target=self._continuous_monitor)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        logger.info("✅ 连续语音监听已启动")
        
    def stop_recognition(self):
        """停止连续监听"""
        self.is_monitoring = False
        self.is_auto_recording = False
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=1)
        logger.info("连续语音监听已停止")
        
    def _continuous_monitor(self):
        """连续监听模式"""
        chunk_size = 1024
        sample_rate = self.sample_rate
        
        def audio_callback(indata, frames, time, status):
            if status:
                return
                
            # 计算音频能量
            audio_chunk = indata[:, 0]
            energy = np.sqrt(np.mean(audio_chunk ** 2))
            
            # 定期显示监听状态
            self.debug_counter += 1
            if self.debug_counter % 100 == 0:  # 每100个chunk显示一次
                logger.debug(f"监听中... 当前能量: {energy:.4f}, 阈值: {self.vad_threshold:.4f}")
            
            # 检测语音活动
            if energy > self.vad_threshold:
                self.last_activity_time = time.inputBufferAdcTime
                
                # 如果检测到语音且当前没有录音，开始录音
                if not self.is_auto_recording and not self.is_recording:
                    self.is_auto_recording = True
                    logger.info(f"🎤 检测到语音 (能量: {energy:.4f})，开始录音...")
                    
                    # 在新线程中开始录音识别
                    threading.Thread(
                        target=self._auto_record_and_recognize,
                        daemon=True
                    ).start()
                    
        try:
            with sd.InputStream(
                callback=audio_callback,
                samplerate=sample_rate,
                channels=1,
                dtype=np.float32,
                device=self.input_device_id,
                blocksize=chunk_size
            ):
                while self.is_monitoring:
                    time.sleep(0.1)
                    
        except Exception as e:
            logger.error(f"连续监听出错: {e}")
        finally:
            self.is_monitoring = False
            
    def _auto_record_and_recognize(self):
        """智能动态录音并识别"""
        try:
            # 检查音频设备
            if self.input_device_id is None:
                logger.error("未配置可用的录音设备")
                return
            
            if self.dynamic_recording:
                # 使用动态录音
                audio_data = self._dynamic_record()
            else:
                # 使用固定时长录音（向后兼容）
                audio_data = self._fixed_duration_record()
            
            if audio_data is None or len(audio_data) == 0:
                logger.warning("录音数据为空，跳过识别")
                return
                
            if not self.is_monitoring:
                return
                
            logger.info("⚡ 录音完成，开始识别...")
            
            # 语音识别
            text = self._recognize_audio(audio_data)
            
            if text and self.callback:
                # 文本优化：大模型 > 本地标点处理器 > 原始文本
                if self.config.get('llm_optimization', 'enabled', fallback=False):
                    text = self._optimize_text_with_llm(text)
                elif LOCAL_PUNCTUATION_AVAILABLE:
                    text = self._add_local_punctuation(text)
                    
                self.callback(text)
                
        except Exception as e:
            logger.error(f"自动录音识别过程中发生错误: {e}")
        finally:
            self.is_auto_recording = False
            # 等待一小段时间再允许下次录音
            time.sleep(self.cooldown_time)
    
    def _dynamic_record(self):
        """动态时长录音：根据语音活动自动确定录音长度"""
        logger.info("🎙️ 开始动态录音...")
        
        # 录音缓冲区
        audio_buffer = []
        chunk_size = 1024
        chunk_duration = chunk_size / self.sample_rate
        
        # 状态变量
        recording_time = 0.0
        silence_time = 0.0
        
        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.float32,
                device=self.input_device_id,
                blocksize=chunk_size
            ) as stream:
                
                while recording_time < self.max_recording_duration and self.is_monitoring:
                    # 读取音频块
                    audio_chunk, overflowed = stream.read(chunk_size)
                    if overflowed:
                        logger.debug("音频缓冲区溢出")
                    
                    # 添加到缓冲区
                    audio_buffer.append(audio_chunk.flatten())
                    recording_time += chunk_duration
                    
                    # 计算当前块的能量
                    energy = np.sqrt(np.mean(audio_chunk.flatten() ** 2))
                    
                    # 判断是否为静音
                    if energy < self.vad_threshold * 0.3:  # 静音阈值更严格
                        silence_time += chunk_duration
                    else:
                        silence_time = 0.0  # 重置静音计时
                    
                    # 提前停止条件
                    if (recording_time >= self.min_recording_duration and 
                        silence_time >= self.silence_duration_to_stop):
                        logger.info(f"🔇 检测到静音 {silence_time:.1f}秒，提前结束录音")
                        break
                        
                    # 每0.5秒显示一次状态
                    if int(recording_time * 2) != int((recording_time - chunk_duration) * 2):
                        logger.debug(f"录音中... {recording_time:.1f}s, 能量: {energy:.4f}, 静音: {silence_time:.1f}s")
        
        except Exception as e:
            logger.error(f"动态录音过程中出错: {e}")
            return None
        
        # 合并音频数据
        if audio_buffer:
            audio_data = np.concatenate(audio_buffer)
            logger.info(f"✅ 动态录音完成，实际时长: {recording_time:.1f}秒")
            return audio_data
        else:
            logger.warning("录音缓冲区为空")
            return None
    
    def _fixed_duration_record(self):
        """固定时长录音：向后兼容的录音方式"""
        duration_samples = int(self.auto_recording_duration * self.sample_rate)
        logger.debug(f"固定录音 - 时长: {self.auto_recording_duration}秒, 样本数: {duration_samples}")
        
        audio_data = sd.rec(
            duration_samples,
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype=np.float32,
            device=self.input_device_id
        )
        
        # 等待录音完成
        sd.wait()
        return audio_data.flatten() 