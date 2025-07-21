"""
本地标点符号处理器
为语音识别结果添加合适的标点符号
"""

import re
from typing import List, Tuple
from loguru import logger


class PunctuationProcessor:
    """标点符号处理器"""
    
    def __init__(self):
        # 停顿词和语气词规则
        self.pause_patterns = [
            (r'然后|接着|之后|后来', '，'),
            (r'但是|不过|可是|只是', '，'),
            (r'因为|由于|所以|因此', '，'),
            (r'如果|要是|假如|倘若', '，'),
            (r'虽然|尽管|即使|哪怕', '，'),
            (r'而且|并且|同时|另外', '，'),
            (r'首先|其次|最后|最终', '，'),
            (r'当然|显然|确实|的确', '，'),
        ]
        
        # 句子结束标志
        self.sentence_end_patterns = [
            (r'完了|好了|结束了|就这样', '。'),
            (r'怎么样|如何|行吗|可以吗', '？'),
            (r'真的|太好了|太棒了|很棒', '！'),
            (r'谢谢|感谢|再见|拜拜', '。'),
        ]
        
        # 数字相关规则
        self.number_patterns = [
            (r'第(\d+)', r'第\1'),
            (r'(\d+)年(\d+)月', r'\1年\2月'),
            (r'(\d+)点(\d+)分', r'\1点\2分'),
        ]
    
    def process(self, text: str) -> str:
        """处理文本，添加标点符号"""
        if not text or not text.strip():
            return text
            
        try:
            # 清理原始文本
            text = text.strip()
            
            # 移除已有的标点符号（如果有）
            text = re.sub(r'[，。！？；：]', '', text)
            
            # 应用停顿规则
            for pattern, punctuation in self.pause_patterns:
                text = re.sub(f'({pattern})', rf'\1{punctuation}', text)
            
            # 处理数字格式
            for pattern, replacement in self.number_patterns:
                text = re.sub(pattern, replacement, text)
            
            # 智能断句
            text = self._smart_sentence_break(text)
            
            # 应用句末规则
            for pattern, punctuation in self.sentence_end_patterns:
                if re.search(pattern, text):
                    if not text.endswith(('。', '！', '？')):
                        text += punctuation
                    break
            
            # 如果没有句末标点，根据长度和内容判断
            if not text.endswith(('。', '！', '？', '，')):
                text = self._add_final_punctuation(text)
            
            # 清理多余的逗号
            text = re.sub(r'，+', '，', text)
            text = re.sub(r'，([。！？])', r'\1', text)
            
            logger.debug(f"标点处理: {text}")
            return text
            
        except Exception as e:
            logger.error(f"标点符号处理失败: {e}")
            return text
    
    def _smart_sentence_break(self, text: str) -> str:
        """智能断句"""
        # 如果文本很长，在适当位置添加逗号
        if len(text) > 15:
            # 在常见的语法断点处添加逗号
            break_points = ['的时候', '的情况下', '的话', '来说', '而言']
            for point in break_points:
                if point in text:
                    text = text.replace(point, f'{point}，', 1)
                    break
        
        return text
    
    def _add_final_punctuation(self, text: str) -> str:
        """根据内容添加句末标点"""
        # 疑问句标志
        question_words = ['什么', '哪里', '怎么', '为什么', '吗', '呢', '是否']
        if any(word in text for word in question_words):
            return text + '？'
        
        # 感叹句标志  
        exclamation_words = ['太', '真', '好棒', '厉害', '赞', '哇']
        if any(word in text for word in exclamation_words):
            return text + '！'
        
        # 默认添加句号
        return text + '。'


# 全局实例
punctuation_processor = PunctuationProcessor() 