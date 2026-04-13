"""
StudyPal AI 问答功能
使用本地 Ollama 模型 qwen3.5:9b
支持对话历史持久化存储

作者：StudyPal
创建日期：2026-04-13
"""

import requests
from typing import List, Dict, Optional
from datetime import datetime

# 本地模型配置
MODEL_NAME = "qwen3.5:9b"
API_BASE = "http://localhost:11434"

# 系统提示词
SYSTEM_PROMPT = """你叫 StudyPal，是一个可爱的学习搭子 AI 宠物。
你的任务是帮助大学生解决学习问题。

回答要求：
1. 语气温暖鼓励，像朋友一样
2. 可以用 emoji 增加亲和力
3. 遇到不会的问题，鼓励用户一起探索
4. 给出具体可执行的建议，不要只说空话
5. 针对学习的问题，提供实用的解题思路或学习方法
6. 如果问题是具体的学科问题，尝试给出关键提示或步骤
7. 记住之前的对话内容，保持上下文连贯性
"""


class StudyPalAI:
    """
    StudyPal AI 助手类
    
    功能：
    - 提供 AI 问答功能
    - 支持对话上下文
    - 集成外部 AI API
    - 对话历史持久化
    """

    def __init__(self):
        """初始化 StudyPal AI"""
        self.model_name = MODEL_NAME
        self.base_url = API_BASE
        self.conversation_history: List[Dict[str, str]] = []
        self.max_history_length = 20  # 历史消息最大长度
        self.current_conversation_id: Optional[str] = None

        # 延迟导入，避免循环引用
        self._ai_memory = None

    @property
    def ai_memory(self):
        """懒加载 AI 记忆模块"""
        if self._ai_memory is None:
            from src.modules.ai_memory import get_ai_memory
            self._ai_memory = get_ai_memory()
        return self._ai_memory

    def ask(self, question: str, use_history: bool = True,
            conversation_id: str = None, save_to_history: bool = True) -> Dict:
        """
        向 AI 发送问题并获取回答

        参数：
            question: 用户的问题字符串
            use_history: 是否使用对话历史
            conversation_id: 指定对话 ID，不指定则使用当前对话
            save_to_history: 是否保存到历史记录

        返回：
            包含 answer 和 conversation_id 的字典

        异常：
            Exception: 如果 API 调用失败
        """
        try:
            # 确定使用哪个对话 ID
            if conversation_id:
                self.current_conversation_id = conversation_id
            elif self.current_conversation_id is None:
                # 创建新对话
                self.current_conversation_id = self.ai_memory.create_conversation()

            # 构建消息列表
            messages = [
                {'role': 'system', 'content': SYSTEM_PROMPT}
            ]

            # 如果使用历史，尝试从持久化存储加载
            if use_history:
                stored_messages = self.ai_memory.get_conversation_messages(self.current_conversation_id)
                if stored_messages:
                    # 转换格式并添加到消息列表
                    for msg in stored_messages[-self.max_history_length:]:
                        messages.append({'role': msg['role'], 'content': msg['content']})

            # 添加当前问题
            messages.append({'role': 'user', 'content': question})

            # 调用 Ollama API
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "stream": False
                },
                headers={"Content-Type": "application/json"},
                timeout=120  # 默认超时时间（秒）
            )

            if response.status_code != 200:
                raise Exception(f"API 调用失败：{response.status_code} {response.text}")

            result = response.json()
            answer = result.get('message', {}).get('content', '')

            # 保存到历史记录
            if save_to_history:
                self.ai_memory.add_message('user', question, self.current_conversation_id)
                self.ai_memory.add_message('assistant', answer, self.current_conversation_id)

            return {
                'answer': answer,
                'conversation_id': self.current_conversation_id
            }

        except requests.exceptions.ConnectionError:
            raise Exception(f"无法连接到 Ollama 服务：{self.base_url}，请确保 Ollama 正在运行")
        except requests.exceptions.Timeout:
            raise Exception(f"Ollama 服务响应超时，请检查模型 {self.model_name} 是否已下载")
        except Exception as e:
            raise Exception(f"AI 请求失败：{str(e)}")

    def ask_simple(self, question: str) -> str:
        """
        简单版本的 ask，返回纯文本回答（兼容旧接口）

        参数：
            question: 用户的问题

        返回：
            AI 的回答字符串
        """
        result = self.ask(question)
        return result['answer']

    def clear_history(self):
        """清空当前对话历史（仅清空内存）"""
        self.conversation_history = []

    def clear_persistent_history(self):
        """清空持久化的历史记录"""
        self.ai_memory.clear_all_history()
        self.current_conversation_id = None

    def switch_conversation(self, conversation_id: str) -> bool:
        """
        切换到指定对话

        参数：
            conversation_id: 对话 ID

        返回：
            是否切换成功
        """
        return self.ai_memory.set_current_conversation(conversation_id)

    def get_conversation_history(self, conversation_id: str = None) -> List[Dict]:
        """
        获取对话历史

        参数：
            conversation_id: 对话 ID，不指定则使用当前对话

        返回：
            消息列表
        """
        conv_id = conversation_id or self.current_conversation_id
        if conv_id:
            return self.ai_memory.get_conversation_messages(conv_id)
        return []

    def new_conversation(self) -> str:
        """
        开始新对话

        返回：
            新对话 ID
        """
        self.conversation_history = []
        self.current_conversation_id = self.ai_memory.create_conversation()
        return self.current_conversation_id

    def get_all_conversations(self) -> List[Dict]:
        """
        获取所有对话列表

        返回：
            对话列表
        """
        return self.ai_memory.get_all_conversations()

    def delete_conversation(self, conversation_id: str) -> bool:
        """
        删除对话

        参数：
            conversation_id: 对话 ID

        返回：
            是否删除成功
        """
        if self.current_conversation_id == conversation_id:
            self.current_conversation_id = None
        return self.ai_memory.delete_conversation(conversation_id)

    def search_conversations(self, keyword: str) -> List[Dict]:
        """
        搜索对话

        参数：
            keyword: 搜索关键词

        返回：
            匹配的对话列表
        """
        return self.ai_memory.search_conversations(keyword)

    def get_ai_stats(self) -> Dict:
        """
        获取 AI 使用统计

        返回：
            统计信息
        """
        return self.ai_memory.get_stats()


# ==================== 兼容旧版本的函数接口 ====================

_ai_instance: Optional[StudyPalAI] = None


def get_ai_instance() -> StudyPalAI:
    """
    获取 AI 实例（单例模式）

    返回：
        StudyPalAI 实例
    """
    global _ai_instance
    if _ai_instance is None:
        _ai_instance = StudyPalAI()
    return _ai_instance


def ask_ai(question: str, callback: callable = None,
           conversation_id: str = None) -> str:
    """
    向 AI 发送问题并获取回答（兼容旧版本接口）

    参数：
        question: 用户的问题字符串
        callback: 可选的回调函数，用于接收回答
        conversation_id: 指定对话 ID

    返回：
        AI 的回答字符串

    异常：
        Exception: 如果 API 调用失败
    """
    ai = get_ai_instance()
    result = ai.ask(question, conversation_id=conversation_id)

    if callback:
        callback(result['answer'])

    return result['answer']


def ask_ai_with_context(question: str, conversation_id: str = None) -> Dict:
    """
    向 AI 发送问题并获取完整上下文（新版接口）

    参数：
        question: 用户的问题
        conversation_id: 指定对话 ID

    返回：
        包含 answer 和 conversation_id 的字典
    """
    ai = get_ai_instance()
    return ai.ask(question, conversation_id=conversation_id)


def ask_ai_sync(question: str) -> str:
    """
    同步版本的 AI 问答（简化版，直接返回结果）

    参数：
        question: 用户的问题字符串

    返回：
        AI 的回答字符串

    异常：
        Exception: 如果 API 调用失败
    """
    ai = get_ai_instance()
    return ai.ask_simple(question)


def clear_ai_history():
    """清空 AI 对话历史"""
    ai = get_ai_instance()
    ai.clear_history()


def clear_persistent_history():
    """清空持久化的 AI 历史记录"""
    ai = get_ai_instance()
    ai.clear_persistent_history()


def new_ai_conversation() -> str:
    """
    开始新的 AI 对话

    返回：
        新对话 ID
    """
    ai = get_ai_instance()
    return ai.new_conversation()


def get_ai_conversations() -> List[Dict]:
    """
    获取所有 AI 对话列表

    返回：
        对话列表
    """
    ai = get_ai_instance()
    return ai.get_all_conversations()


def get_conversation_messages(conversation_id: str) -> List[Dict]:
    """
    获取指定对话的消息

    参数：
        conversation_id: 对话 ID

    返回：
        消息列表
    """
    ai = get_ai_instance()
    return ai.get_conversation_history(conversation_id)


def delete_ai_conversation(conversation_id: str) -> bool:
    """
    删除指定对话

    参数：
        conversation_id: 对话 ID

    返回：
        是否删除成功
    """
    ai = get_ai_instance()
    return ai.delete_conversation(conversation_id)


def search_ai_conversations(keyword: str) -> List[Dict]:
    """
    搜索 AI 对话

    参数：
        keyword: 搜索关键词

    返回：
        匹配的对话列表
    """
    ai = get_ai_instance()
    return ai.search_conversations(keyword)


# ==================== 测试代码 ====================

if __name__ == "__main__":
    print("=== StudyPal AI 测试 ===")
    print(f"模型：{MODEL_NAME}")
    print(f"API: {API_BASE}")

    ai = get_ai_instance()

    test_questions = [
        "1+1+90=?",
        "数学公式怎么记？",
        "编程遇到 bug 怎么办？"
    ]

    for q in test_questions:
        print(f"\n用户：{q}")
        try:
            result = ai.ask(q)
            print(f"AI: {result['answer']}")
            print(f"对话 ID: {result['conversation_id']}")
        except Exception as e:
            print(f"错误：{e}")
