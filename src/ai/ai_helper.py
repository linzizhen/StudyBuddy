"""
StudyPal AI 问答功能
支持本地 Ollama 模型和云端 OpenAI 兼容 API
支持对话历史持久化存储

作者：StudyPal
创建日期：2026-04-13
更新日期：2026-05-18（迁移到云端模型）
"""

import requests
import time
from functools import wraps
from typing import List, Dict, Optional
from config import (
    DEFAULT_MODEL_KEY, MODELS_CONFIG, API_KEY, AI_TIMEOUT, AI_MAX_RETRIES,
    ai_config
)


def retry_on_failure(max_retries=None, delay=1):
    """AI 请求失败重试装饰器"""
    if max_retries is None:
        max_retries = AI_MAX_RETRIES

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(delay * (attempt + 1))
        return wrapper
    return decorator


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
    - 支持本地 Ollama 和云端 OpenAI 兼容 API
    - 对话历史持久化
    - 支持用户自定义模型配置
    """

    def __init__(self, model_key: str = None, custom_config: dict = None):
        """初始化 StudyPal AI

        参数：
            model_key: 预设模型 key，如果为 None 则使用默认配置
            custom_config: 用户自定义模型配置 dict，格式：
                {
                    "base_url": "https://api.deepseek.com/v1",
                    "api_key": "sk-xxx",
                    "model": "deepseek-chat"
                }
        """
        self.model_key = model_key
        self.custom_config = custom_config
        self._load_model_config()

        self.conversation_history: List[Dict[str, str]] = []
        self.max_history_length = 20
        self.current_conversation_id: Optional[str] = None

        self._ai_memory = None

    def _load_model_config(self):
        """从配置中加载模型信息"""
        # 优先使用用户自定义配置
        if self.custom_config:
            self.provider = "openai"  # 自定义模型假定为 OpenAI 兼容格式
            self.model_name = self.custom_config.get("model", "")
            self.base_url = self.custom_config.get("base_url", "")
            self.model_api_key = self.custom_config.get("api_key", "")
        # 其次使用预设模型
        elif self.model_key and self.model_key in MODELS_CONFIG:
            config = MODELS_CONFIG[self.model_key]
            self.provider = config.get("provider", "openai")
            self.model_name = config.get("model", "llama-3.3-70b-versatile")
            self.base_url = config.get("base_url", "https://api.groq.com/openai/v1")
            self.model_api_key = config.get("api_key", "") or API_KEY
        # 最后使用系统默认配置
        else:
            self.provider = "openai"
            self.model_name = ai_config.default_model
            self.base_url = ai_config.base_url
            self.model_api_key = API_KEY

        self.timeout = AI_TIMEOUT

    def get_current_model_info(self) -> Dict[str, str]:
        """获取当前模型信息"""
        if self.custom_config:
            return {
                "key": "custom",
                "name": self.custom_config.get("name", "自定义模型"),
                "provider": self.provider,
                "model": self.model_name,
                "base_url": self.base_url,
                "is_custom": True
            }
        return {
            "key": self.model_key or DEFAULT_MODEL_KEY,
            "name": MODELS_CONFIG.get(self.model_key, {}).get("name", self.model_name),
            "provider": self.provider,
            "model": self.model_name,
            "base_url": self.base_url,
            "is_custom": False
        }

    @property
    def ai_memory(self):
        """懒加载 AI 记忆模块"""
        if self._ai_memory is None:
            from src.modules.ai_memory import get_ai_memory
            self._ai_memory = get_ai_memory()
        return self._ai_memory

    def _call_ollama(self, messages: List[Dict[str, str]]) -> str:
        """调用 Ollama API（向后兼容）"""
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model_name,
                "messages": messages,
                "stream": False
            },
            headers={"Content-Type": "application/json"},
            timeout=self.timeout
        )

        if response.status_code != 200:
            raise Exception(f"Ollama API 调用失败：{response.status_code} {response.text}")

        result = response.json()
        return result.get("message", {}).get("content", "")

    def _call_openai_compatible(self, messages: List[Dict[str, str]]) -> str:
        """调用 OpenAI 兼容 API（如 Groq、DeepSeek、智谱等）"""
        # URL 兜底：智谱等需要 /v4 后缀的模型，自动补齐
        base = (self.base_url or "").rstrip("/")
        if "bigmodel.cn" in base and not base.endswith("/v4"):
            base = base + "/v4"
        chat_url = base + "/chat/completions"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.model_api_key}"
        }

        response = requests.post(
            chat_url,
            json={
                "model": self.model_name,
                "messages": messages,
                "stream": False
            },
            headers=headers,
            timeout=self.timeout
        )

        if response.status_code != 200:
            # 解析智谱等平台的 error.message
            err_detail = ""
            try:
                ej = response.json()
                if isinstance(ej, dict):
                    err_obj = ej.get("error")
                    if isinstance(err_obj, dict):
                        err_detail = err_obj.get("message") or err_obj.get("code") or ""
                    elif isinstance(err_obj, str):
                        err_detail = err_obj
                    if not err_detail:
                        err_detail = ej.get("message") or ""
            except Exception:
                err_detail = response.text[:200]
            err_detail = (err_detail or response.text[:200])[:300]
            err_lower = err_detail.lower()

            # 按状态码分类
            if response.status_code == 401:
                raise Exception(
                    f"API_KEY_INVALID: API Key 无效或已过期，请检查设置中的 API 密钥。详情：{err_detail}"
                )
            elif response.status_code == 403:
                # 智谱 403 典型原因：key 错误 / 模型未开通 / 额度用完
                if "invalid api key" in err_lower or "authentication" in err_lower:
                    raise Exception(
                        f"AI_AUTH_403: API 密钥无效，请检查设置中的 API 密钥是否正确（注意大小写和前后空格）。详情：{err_detail}"
                    )
                elif ("quota" in err_lower or "limit" in err_lower or "exceeded" in err_lower
                      or "balance" in err_lower):
                    raise Exception(
                        f"AI_AUTH_403: API 调用额度已用完或受限，请检查智谱账户余额。详情：{err_detail}"
                    )
                elif "model" in err_lower and ("not" in err_lower or "permission" in err_lower):
                    raise Exception(
                        f"AI_AUTH_403: 模型「{self.model_name}」未开通或无权限，请在智谱官网开通后重试。详情：{err_detail}"
                    )
                else:
                    raise Exception(
                        f"AI_AUTH_403: 权限被拒绝（可能：密钥错误 / 模型未开通 / 账户异常）。详情：{err_detail}"
                    )
            elif response.status_code == 429:
                raise Exception(
                    f"AI_RATE_LIMIT: 请求过于频繁（HTTP 429），请稍后再试。详情：{err_detail}"
                )
            elif response.status_code == 404:
                raise Exception(
                    f"AI_NOT_FOUND: API 地址或模型不存在（HTTP 404），请检查配置。当前 URL：{chat_url}"
                )
            elif response.status_code >= 500:
                raise Exception(
                    f"AI_SERVER_ERROR: AI 服务端错误（HTTP {response.status_code}），请稍后重试。详情：{err_detail}"
                )
            else:
                raise Exception(
                    f"API 调用失败（HTTP {response.status_code}）：{err_detail}"
                )

        result = response.json()
        return result.get("choices", [{}])[0].get("message", {}).get("content", "")

    def ask(self, question: str, use_history: bool = True,
            conversation_id: str = None, save_to_history: bool = True,
            system_prompt: str = None) -> Dict:
        """
        向 AI 发送问题并获取回答

        参数：
            question: 用户的问题字符串
            use_history: 是否使用对话历史
            conversation_id: 指定对话 ID，不指定则使用当前对话
            save_to_history: 是否保存到历史记录
            system_prompt: 自定义系统提示词（覆盖默认）

        返回：
            包含 answer 和 conversation_id 的字典

        异常：
            Exception: 如果 API 调用失败
        """
        try:
            if conversation_id:
                self.current_conversation_id = conversation_id
            elif self.current_conversation_id is None:
                self.current_conversation_id = self.ai_memory.create_conversation()

            final_system_prompt = system_prompt if system_prompt else SYSTEM_PROMPT
            messages = [
                {"role": "system", "content": final_system_prompt}
            ]

            if use_history:
                stored_messages = self.ai_memory.get_conversation_messages(self.current_conversation_id)
                if stored_messages:
                    for msg in stored_messages[-self.max_history_length:]:
                        messages.append({"role": msg["role"], "content": msg["content"]})

            messages.append({"role": "user", "content": question})

            if self.provider == "ollama":
                answer = self._call_ollama(messages)
            else:
                answer = self._call_openai_compatible(messages)

            if save_to_history:
                self.ai_memory.add_message("user", question, self.current_conversation_id)
                self.ai_memory.add_message("assistant", answer, self.current_conversation_id)

            return {
                "answer": answer,
                "conversation_id": self.current_conversation_id
            }

        except requests.exceptions.ConnectionError:
            raise Exception(
                f"无法连接到 AI 服务：{self.base_url}\n"
                f"请检查网络连接，或确认 API 配置是否正确（当前使用：{self.model_key}）"
            )
        except requests.exceptions.Timeout:
            raise Exception(
                f"AI 服务响应超时（{self.timeout}秒）\n"
                f"当前使用模型：{self.model_name}（{self.provider}）\n"
                f"可以尝试切换到响应更快的模型，如 Groq Llama"
            )
        except Exception as e:
            raise Exception(f"AI 请求失败：{str(e)}")

    def ask_simple(self, question: str) -> str:
        """
        简单版本的 ask，返回纯文本回答（兼容旧接口）
        """
        result = self.ask(question)
        return result["answer"]

    def clear_history(self):
        """清空当前对话历史（仅清空内存）"""
        self.conversation_history = []

    def clear_persistent_history(self):
        """清空持久化的历史记录"""
        self.ai_memory.clear_all_history()
        self.current_conversation_id = None

    def switch_conversation(self, conversation_id: str) -> bool:
        """切换到指定对话"""
        return self.ai_memory.set_current_conversation(conversation_id)

    def get_conversation_history(self, conversation_id: str = None) -> List[Dict]:
        """获取对话历史"""
        conv_id = conversation_id or self.current_conversation_id
        if conv_id:
            return self.ai_memory.get_conversation_messages(conv_id)
        return []

    def new_conversation(self) -> str:
        """开始新对话"""
        self.conversation_history = []
        self.current_conversation_id = self.ai_memory.create_conversation()
        return self.current_conversation_id

    def get_all_conversations(self) -> List[Dict]:
        """获取所有对话列表"""
        return self.ai_memory.get_all_conversations()

    def delete_conversation(self, conversation_id: str) -> bool:
        """删除对话"""
        if self.current_conversation_id == conversation_id:
            self.current_conversation_id = None
        return self.ai_memory.delete_conversation(conversation_id)

    def search_conversations(self, keyword: str) -> List[Dict]:
        """搜索对话"""
        return self.ai_memory.search_conversations(keyword)

    def get_ai_stats(self) -> Dict:
        """获取 AI 使用统计"""
        return self.ai_memory.get_stats()


# ==================== 兼容旧版本的函数接口 ====================

_ai_instance: Optional[StudyPalAI] = None


def get_ai_instance(model_key: str = None) -> StudyPalAI:
    """
    获取 AI 实例（单例模式）

    参数：
        model_key: 可选的模型配置 key，不指定则使用默认模型

    返回：
        StudyPalAI 实例
    """
    global _ai_instance
    if _ai_instance is None:
        _ai_instance = StudyPalAI(model_key)
    return _ai_instance


def ask_ai(question: str, callback: callable = None,
           conversation_id: str = None) -> str:
    """
    向 AI 发送问题并获取回答（兼容旧版本接口）
    """
    ai = get_ai_instance()
    result = ai.ask(question, conversation_id=conversation_id)

    if callback:
        callback(result["answer"])

    return result["answer"]


def ask_ai_with_context(question: str, conversation_id: str = None) -> Dict:
    """
    向 AI 发送问题并获取完整上下文（新版接口）
    """
    ai = get_ai_instance()
    return ai.ask(question, conversation_id=conversation_id)


def ask_ai_sync(question: str) -> str:
    """
    同步版本的 AI 问答（简化版，直接返回结果）
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
    """开始新的 AI 对话"""
    ai = get_ai_instance()
    return ai.new_conversation()


def get_ai_conversations() -> List[Dict]:
    """获取所有 AI 对话列表"""
    ai = get_ai_instance()
    return ai.get_all_conversations()


def get_conversation_messages(conversation_id: str) -> List[Dict]:
    """获取指定对话的消息"""
    ai = get_ai_instance()
    return ai.get_conversation_history(conversation_id)


def delete_ai_conversation(conversation_id: str) -> bool:
    """删除指定对话"""
    ai = get_ai_instance()
    return ai.delete_conversation(conversation_id)


def search_ai_conversations(keyword: str) -> List[Dict]:
    """搜索 AI 对话"""
    ai = get_ai_instance()
    return ai.search_conversations(keyword)


def get_available_models() -> Dict[str, Dict]:
    """获取所有可用的模型列表"""
    return MODELS_CONFIG


def get_current_model() -> Dict[str, str]:
    """获取当前使用的模型信息"""
    return get_ai_instance().get_current_model_info()


def build_ai_from_user(user: dict) -> "StudyPalAI":
    """根据用户字典（来自 AuthService）构造 AI 实例

    优先级：ai_custom_config > ai_model_key > 环境默认
    """
    custom_config = None
    model_key = None
    if user:
        if user.get("ai_custom_config"):
            custom_config = user.get("ai_custom_config")
        else:
            model_key = user.get("ai_model_key")
    return StudyPalAI(model_key=model_key, custom_config=custom_config)


def ask_ai_for_user(user: dict, question: str, system_prompt: str = None,
                    conversation_id: str = None, save_to_history: bool = False) -> Dict:
    """使用指定用户的模型配置调用 AI

    user: AuthService 返回的用户 dict（含 ai_custom_config/ai_model_key）
    question: 用户问题
    system_prompt: 可选自定义系统提示
    conversation_id: 可选对话 ID
    save_to_history: 是否保存（讲解类场景一般不保存到聊天历史）
    """
    ai = build_ai_from_user(user)
    return ai.ask(
        question=question,
        conversation_id=conversation_id,
        system_prompt=system_prompt,
        save_to_history=save_to_history,
    )


# ==================== 测试代码 ====================

if __name__ == "__main__":
    print("=== StudyPal AI 测试 ===")
    ai = get_ai_instance()
    info = ai.get_current_model_info()
    print(f"模型：{info['name']}")
    print(f"Provider：{info['provider']}")
    print(f"API: {info['base_url']}")
    print(f"Model: {info['model']}")

    if info["provider"] != "ollama" and not info.get("base_url"):
        print("\n警告：使用云端模型但未配置 API Key！")
        print("请在 .env 文件中设置 AI_API_KEY 或在 MODELS_CONFIG 中配置")

    print("\n" + "=" * 50)

    test_questions = [
        "1+1+90=?",
        "数学公式怎么记？",
    ]

    for q in test_questions:
        print(f"\n用户：{q}")
        try:
            result = ai.ask(q)
            print(f"AI: {result['answer']}")
        except Exception as e:
            print(f"错误：{e}")
