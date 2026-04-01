"""
StudyBuddy AI 问答功能
参考 AgriSense 的 API 调用模式进行优化

功能改进：
1. 支持多模型配置（Ollama 和 OpenAI 兼容 API）
2. 服务可用性检测
3. 降级策略：专用库 → requests 直接调用 → 模拟模式
4. 支持多轮对话历史
"""

import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime

# 尝试导入常用库
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️  requests 库不可用")

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("⚠️  ollama 库不可用，将使用 requests 直接调用")

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️  openai 库不可用")

# 导入配置
from config import API_BASE, MODEL_NAME, API_KEY, MODELS_CONFIG, DEFAULT_MODEL_KEY

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# 系统提示词：让 AI 回答简短可爱，符合学习搭子身份
SYSTEM_PROMPT = """你叫 StudyBuddy，是一个可爱的学习搭子 AI 宠物。
你的任务是帮助大学生解决学习问题。

回答要求：
1. 语气温暖鼓励，像朋友一样
2. 可以用 emoji 增加亲和力
3. 遇到不会的问题，鼓励用户一起探索
4. 给出具体可执行的建议，不要只说空话
5. 针对学习的问题，提供实用的解题思路或学习方法
6. 如果问题是具体的学科问题，尝试给出关键提示或步骤

示例回答风格：
- 数学问题："先画图理解题意，找出已知条件和要求的量~ 📐"
- 英语问题："多读多听是关键！试试每天听 10 分钟英语播客 🎧"
- 编程问题："debug 时先打印变量值，一步步排查~ 🐛"
- 学习动力："今天先定个小目标，完成就奖励自己！💪"
"""

# 模拟回答库（API 不可用时使用）
MOCK_RESPONSES = {
    "default": "嗯...让我想想~ 这个问题很有趣呢！🤔",
    "math": "数学问题可以这样想：先画图理解题意，找出已知条件和要求的量~ 一步步来，你一定能行！📐✨",
    "english": "英语学习最重要的是坚持！试试每天听 10 分钟英语播客，多读多练~ 🎧📚",
    "programming": "编程遇到 bug 别着急！先打印变量值，一步步排查，或者把问题拆开看~ 🐛💻",
    "sleepy": "困了的话，起来活动一下，喝杯温水，做几个深呼吸~ 然后继续加油！💪☕",
    "thanks": "不客气呀！能帮到你我很开心~ 有什么问题随时找我哦！😊💕",
    "memory": "记忆的话，试试间隔重复法！早上记一遍，晚上再复习，效果超好~ 🧠✨",
    "exam": "考试前不要紧张，提前复习重点，保持好心态~ 相信自己，你一定可以的！📝💪",
    "focus": "专注的话，试试番茄工作法！25 分钟专注 +5 分钟休息，循环进行~ 🍅⏰",
    "writing": "写作先列提纲，确定结构再填充内容~ 多读范文，模仿好的表达方式！✍️📖"
}


class StudyBuddyAI:
    """StudyBuddy AI 助手类"""
    
    def __init__(
        self,
        model_name: str = None,
        api_key: str = None,
        base_url: str = None,
        models_config: dict = None
    ):
        """
        初始化 StudyBuddy AI
        
        Args:
            model_name: 模型配置 key（默认使用 DEFAULT_MODEL_KEY）
            api_key: API 密钥（可选，覆盖配置）
            base_url: API 基础 URL（可选，覆盖配置）
            models_config: 多模型配置字典（可选，默认使用 MODELS_CONFIG）
        """
        # 使用默认配置或传入的参数
        self.models_config = models_config or MODELS_CONFIG
        
        # 如果没有指定模型 key，使用默认配置
        if model_name is None:
            self.current_model_key = DEFAULT_MODEL_KEY
        else:
            self.current_model_key = model_name
        
        # 如果传入单个配置参数，添加到 models_config
        if api_key or base_url:
            if self.current_model_key not in self.models_config:
                self.models_config[self.current_model_key] = {}
            if api_key:
                self.models_config[self.current_model_key]['api_key'] = api_key
            if base_url:
                self.models_config[self.current_model_key]['base_url'] = base_url
        
        # 获取当前模型配置
        self._update_current_model()
        
        # 对话历史
        self.conversation_history: List[Dict[str, str]] = []
        self.max_history_length = 10  # 保留最近 10 轮对话
        
        # 客户端
        self.client = None
        self.use_simulation = False
        self._init_client()
    
    def _update_current_model(self):
        """更新当前模型配置"""
        if self.models_config:
            model_config = self.models_config.get(self.current_model_key, {})
            self.model_name = model_config.get('model', self.current_model_key)
            self.api_key = model_config.get('api_key', '')
            self.base_url = model_config.get('base_url', 'http://localhost:11434')
            self.provider = model_config.get('provider', 'ollama')
            self.model_display_name = model_config.get('name', self.model_name)
        else:
            # 使用简单配置
            self.model_name = MODEL_NAME
            self.api_key = API_KEY
            self.base_url = API_BASE
            # 根据 URL 判断 provider
            if 'ollama' in self.base_url.lower() or 'localhost:11434' in self.base_url:
                self.provider = 'ollama'
            else:
                self.provider = 'openai'
            self.model_display_name = self.model_name
    
    def _init_client(self):
        """初始化 LLM 客户端"""
        try:
            # 根据 provider 类型选择客户端
            if self.provider == 'ollama':
                # 尝试使用 Ollama，但先检测服务是否可用
                if OLLAMA_AVAILABLE and REQUESTS_AVAILABLE:
                    # 检测 Ollama 服务是否运行
                    try:
                        test_response = requests.get(f"{self.base_url}/api/tags", timeout=2)
                        if test_response.status_code == 200:
                            self.client = ollama
                            logger.info("✅ Ollama 客户端已初始化")
                            return
                        else:
                            logger.warning(f"⚠️  Ollama 服务不可用 (状态码：{test_response.status_code})，使用 requests 直接调用")
                    except Exception as e:
                        logger.warning(f"⚠️  Ollama 服务未运行：{e}，使用 requests 直接调用")
                    
                    # Ollama 服务不可用，使用 requests
                    logger.info("📡 使用 requests 调用 Ollama API")
                    return
                
                # Ollama 库不可用，使用 requests
                if REQUESTS_AVAILABLE:
                    logger.info("📡 使用 requests 调用 Ollama API")
                    return
                
            elif self.provider == 'openai':
                # 尝试使用 OpenAI 兼容 API
                if OPENAI_AVAILABLE and self.api_key:
                    # 检测 OpenAI 服务是否可用
                    try:
                        test_response = requests.get(f"{self.base_url}/models", timeout=2)
                        if test_response.status_code == 200:
                            self.client = OpenAI(
                                api_key=self.api_key,
                                base_url=self.base_url
                            )
                            logger.info("✅ OpenAI 客户端已初始化")
                            return
                        else:
                            logger.warning(f"⚠️  OpenAI 服务不可用 (状态码：{test_response.status_code})，使用 requests 直接调用")
                    except Exception as e:
                        logger.warning(f"⚠️  OpenAI 服务检测失败：{e}，使用 requests 直接调用")
                    
                    # 使用 requests
                    logger.info("📡 使用 requests 调用 OpenAI API")
                    return
                
                # OpenAI 库不可用，使用 requests
                if REQUESTS_AVAILABLE:
                    logger.info("📡 使用 requests 调用 OpenAI API")
                    return
            
            logger.warning("⚠️  无法初始化 LLM 客户端，使用模拟模式")
            self.use_simulation = True
            
        except Exception as e:
            logger.error(f"❌ 初始化 LLM 客户端失败：{e}")
            self.use_simulation = True
    
    def get_model_info(self) -> dict:
        """获取当前模型信息"""
        return {
            'key': self.current_model_key,
            'name': self.model_display_name,
            'model': self.model_name,
            'provider': self.provider,
            'base_url': self.base_url,
            'simulation_mode': self.use_simulation
        }
    
    def switch_model(self, model_key: str) -> bool:
        """
        切换模型
        
        Args:
            model_key: 模型配置 key
            
        Returns:
            是否切换成功
        """
        if model_key not in self.models_config:
            return False
        
        self.current_model_key = model_key
        self._update_current_model()
        self._init_client()
        
        logger.info(f"🔄 模型已切换到：{self.model_display_name} ({self.model_name})")
        return True
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
        logger.info("🗑️ 对话历史已清空")
    
    def ask(self, question: str, use_history: bool = True) -> str:
        """
        向 AI 发送问题并获取回答
        
        Args:
            question: 用户的问题字符串
            use_history: 是否使用对话历史
            
        Returns:
            AI 的回答字符串
        """
        if self.use_simulation:
            return self._mock_ask(question)
        
        try:
            # 构建消息列表
            messages = [
                {'role': 'system', 'content': SYSTEM_PROMPT}
            ]
            
            # 添加对话历史
            if use_history and self.conversation_history:
                messages.extend(self.conversation_history[-self.max_history_length:])
            
            # 添加当前问题
            messages.append({'role': 'user', 'content': question})
            
            # 调用 LLM
            if OLLAMA_AVAILABLE and self.client:
                response = self.client.chat(
                    model=self.model_name,
                    messages=messages
                )
                answer = response['message']['content']
            
            elif OPENAI_AVAILABLE and self.client:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages
                )
                answer = response.choices[0].message.content
            
            else:
                # 使用 requests 调用
                answer = self._call_chat_api(messages)
            
            # 更新对话历史
            if use_history:
                self.conversation_history.append({'role': 'user', 'content': question})
                self.conversation_history.append({'role': 'assistant', 'content': answer})
            
            return answer
            
        except Exception as e:
            logger.error(f"❌ AI 请求出错：{e}")
            return self._mock_ask(question)
    
    def _call_chat_api(self, messages: List[Dict[str, str]]) -> str:
        """调用聊天 API"""
        try:
            # 根据 provider 类型选择正确的 API 端点
            if self.provider == 'ollama':
                # Ollama 使用 /api/generate 端点，需要转换消息格式
                return self._call_ollama_api(messages)
            else:
                # OpenAI 兼容 API 使用 /v1/chat/completions 端点
                return self._call_openai_api(messages)
        except Exception as e:
            logger.error(f"❌ 聊天 API 调用失败：{e}")
            raise
    
    def _call_ollama_api(self, messages: List[Dict[str, str]]) -> str:
        """调用 Ollama API"""
        # 将消息列表合并为单个 prompt
        full_prompt = ""
        system_prompt = ""
        
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            if role == 'system':
                system_prompt = content
            elif role == 'user':
                full_prompt += f"用户：{content}\n"
            elif role == 'assistant':
                full_prompt += f"助手：{content}\n"
        
        # 只保留最后一个用户问题，避免上下文过长
        # 提取最后一个用户问题
        last_user_question = ""
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                last_user_question = msg.get('content', '')
                break
        
        logger.info(f"📡 调用 Ollama API: {self.base_url}/api/generate, 模型：{self.model_name}")
        logger.info(f"📝 问题：{last_user_question[:50]}...")
        
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model_name,
                "prompt": last_user_question,
                "system": system_prompt,
                "stream": False
            },
            headers={"Content-Type": "application/json"},
            timeout=120  # 增加到 120 秒
        )
        
        if response.status_code != 200:
            logger.error(f"⚠️  API 响应状态码：{response.status_code}")
            logger.error(f"⚠️  API 响应内容：{response.text[:200]}")
            raise Exception(f"API 调用失败：{response.status_code} {response.text}")
        
        result = response.json()
        answer = result.get('response', '')
        logger.info(f"✅ 收到回答：{answer[:50]}...")
        return answer
    
    def _call_openai_api(self, messages: List[Dict[str, str]]) -> str:
        """调用 OpenAI 兼容 API"""
        url = f"{self.base_url}/chat/completions"
        logger.info(f"📡 调用 OpenAI API: {url}, 模型：{self.model_name}")
        
        response = requests.post(
            url,
            json={
                "model": self.model_name,
                "messages": messages
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            },
            timeout=120
        )
        
        # 详细错误日志
        if response.status_code != 200:
            logger.error(f"⚠️  API 响应状态码：{response.status_code}")
            logger.error(f"⚠️  API 响应内容：{response.text[:200]}")
            raise Exception(f"API 调用失败：{response.status_code} {response.text}")
        
        data = response.json()
        return data['choices'][0]['message']['content']
    
    def _mock_ask(self, question: str) -> str:
        """
        模拟 AI 回答（当 API 不可用时使用）
        
        Args:
            question: 用户的问题
            
        Returns:
            预设的可爱回答字符串
        """
        question_lower = question.lower()
        
        # 根据关键词返回对应的回答
        if "数学" in question_lower or "高数" in question_lower or "math" in question_lower or "公式" in question_lower:
            return MOCK_RESPONSES["math"]
        elif "英语" in question_lower or "english" in question_lower or "单词" in question_lower or "口语" in question_lower:
            return MOCK_RESPONSES["english"]
        elif "编程" in question_lower or "代码" in question_lower or "python" in question_lower or "bug" in question_lower or "程序" in question_lower:
            return MOCK_RESPONSES["programming"]
        elif "困" in question_lower or "累" in question_lower or "sleep" in question_lower or "休息" in question_lower:
            return MOCK_RESPONSES["sleepy"]
        elif "谢谢" in question_lower or "thank" in question_lower:
            return MOCK_RESPONSES["thanks"]
        elif "记忆" in question_lower or "背诵" in question_lower or "记不住" in question_lower:
            return MOCK_RESPONSES["memory"]
        elif "考试" in question_lower or "测验" in question_lower or "quiz" in question_lower:
            return MOCK_RESPONSES["exam"]
        elif "专注" in question_lower or "分心" in question_lower or "注意力" in question_lower or "番茄" in question_lower:
            return MOCK_RESPONSES["focus"]
        elif "写作" in question_lower or "论文" in question_lower or "作文" in question_lower:
            return MOCK_RESPONSES["writing"]
        else:
            return MOCK_RESPONSES["default"]


# 兼容旧版本的函数接口
_ai_instance: Optional[StudyBuddyAI] = None

def get_ai_instance() -> StudyBuddyAI:
    """获取 AI 实例（单例模式）"""
    global _ai_instance
    if _ai_instance is None:
        _ai_instance = StudyBuddyAI()
    return _ai_instance


def ask_ai(question: str, callback: callable = None, timeout: int = 60) -> str:
    """
    向 AI 发送问题并获取回答（兼容旧版本接口）
    
    参数:
        question: 用户的问题字符串
        callback: 可选的回调函数，用于接收回答
        timeout: 请求超时时间（秒），此参数保留但不再使用
    
    返回:
        AI 的回答字符串，如果失败则返回模拟回答
    """
    ai = get_ai_instance()
    answer = ai.ask(question)
    
    if callback:
        callback(answer)
    
    return answer


def ask_ai_sync(question: str) -> str:
    """
    同步版本的 AI 问答（简化版，直接返回结果）
    
    参数:
        question: 用户的问题字符串
    
    返回:
        AI 的回答字符串
    """
    return ask_ai(question)


def clear_ai_history():
    """清空 AI 对话历史"""
    ai = get_ai_instance()
    ai.clear_history()


# 测试代码
if __name__ == "__main__":
    print("=== StudyBuddy AI 测试 ===")
    
    # 测试 AI 实例
    ai = get_ai_instance()
    print(f"模型信息：{ai.get_model_info()}")
    
    # 测试问答
    test_questions = [
        "数学公式怎么记？",
        "编程遇到 bug 怎么办？",
        "今天好困啊...",
        "谢谢你的帮助！"
    ]
    
    for q in test_questions:
        print(f"\n用户：{q}")
        answer = ai.ask(q)
        print(f"AI: {answer}")
