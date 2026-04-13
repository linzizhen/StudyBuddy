"""
StudyPal AI 记忆与对话历史模块
持久化存储 AI 对话记录，支持查看历史对话

作者：StudyPal
创建日期：2026-04-13
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from config import AI_HISTORY_FILE


class AIMemory:
    """
    AI 记忆类，管理对话历史和记忆
    
    功能：
    - 对话管理
    - 消息存储
    - 历史记录
    - 对话搜索
    """

    def __init__(self, data_file=None):
        """
        初始化 AI 记忆模块

        参数:
            data_file: 数据文件路径
        """
        self.data_file = data_file or AI_HISTORY_FILE
        self.conversations: List[Dict[str, Any]] = []
        self.current_conversation_id: Optional[str] = None
        self._load_history()

    def _load_history(self):
        """从文件加载历史记录"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.conversations = data.get("conversations", [])
            except (json.JSONDecodeError, IOError):
                self.conversations = []
        else:
            self.conversations = []

    def _save_history(self):
        """保存历史记录到文件"""
        data = {
            "conversations": self.conversations,
            "last_updated": datetime.now().isoformat()
        }
        dir_path = os.path.dirname(self.data_file)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def create_conversation(self, title: str = None) -> str:
        """
        创建新对话会话

        参数:
            title: 对话标题，不提供则自动生成

        返回:
            新对话的 ID
        """
        conversation_id = datetime.now().strftime("%Y%m%d%H%M%S")
        if title is None:
            title = f"对话 {len(self.conversations) + 1}"

        conversation = {
            "id": conversation_id,
            "title": title,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "messages": []
        }
        self.conversations.insert(0, conversation)
        self.current_conversation_id = conversation_id
        self._save_history()
        return conversation_id

    def add_message(self, role: str, content: str, conversation_id: str = None) -> bool:
        """
        添加消息到对话

        参数:
            role: 角色 ('user' 或 'assistant')
            content: 消息内容
            conversation_id: 对话 ID，不提供则使用当前对话

        返回:
            是否添加成功
        """
        if conversation_id is None:
            conversation_id = self.current_conversation_id

        if conversation_id is None:
            conversation_id = self.create_conversation()

        for conv in self.conversations:
            if conv["id"] == conversation_id:
                message = {
                    "role": role,
                    "content": content,
                    "timestamp": datetime.now().isoformat()
                }
                conv["messages"].append(message)
                conv["updated_at"] = datetime.now().isoformat()

                # 更新对话标题（如果是第一条用户消息）
                if len(conv["messages"]) == 1 and role == "user":
                    # 使用用户问题的前30个字符作为标题
                    title = content[:30] + "..." if len(content) > 30 else content
                    conv["title"] = title

                self._save_history()
                return True

        return False

    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定对话

        参数:
            conversation_id: 对话 ID

        返回:
            对话数据，不存在则返回 None
        """
        for conv in self.conversations:
            if conv["id"] == conversation_id:
                return conv
        return None

    def get_all_conversations(self) -> List[Dict[str, Any]]:
        """
        获取所有对话列表（不含消息内容）

        返回:
            对话列表
        """
        result = []
        for conv in self.conversations:
            result.append({
                "id": conv["id"],
                "title": conv["title"],
                "created_at": conv["created_at"],
                "updated_at": conv["updated_at"],
                "message_count": len(conv["messages"])
            })
        return result

    def get_conversation_messages(self, conversation_id: str) -> List[Dict[str, str]]:
        """
        获取对话的所有消息

        参数:
            conversation_id: 对话 ID

        返回:
            消息列表
        """
        conv = self.get_conversation(conversation_id)
        if conv:
            return conv["messages"]
        return []

    def delete_conversation(self, conversation_id: str) -> bool:
        """
        删除对话

        参数:
            conversation_id: 对话 ID

        返回:
            是否删除成功
        """
        for i, conv in enumerate(self.conversations):
            if conv["id"] == conversation_id:
                self.conversations.pop(i)
                if self.current_conversation_id == conversation_id:
                    self.current_conversation_id = None
                self._save_history()
                return True
        return False

    def set_current_conversation(self, conversation_id: str) -> bool:
        """
        设置当前对话

        参数:
            conversation_id: 对话 ID

        返回:
            是否设置成功
        """
        conv = self.get_conversation(conversation_id)
        if conv:
            self.current_conversation_id = conversation_id
            return True
        return False

    def clear_all_history(self):
        """清空所有历史记录"""
        self.conversations = []
        self.current_conversation_id = None
        self._save_history()

    def get_recent_conversations(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        获取最近的对话

        参数:
            count: 返回数量

        返回:
            对话列表
        """
        return self.get_all_conversations()[:count]

    def search_conversations(self, keyword: str) -> List[Dict[str, Any]]:
        """
        搜索包含关键词的对话

        参数:
            keyword: 搜索关键词

        返回:
            匹配的对话列表
        """
        results = []
        for conv in self.conversations:
            # 搜索标题
            if keyword.lower() in conv["title"].lower():
                results.append(conv)
                continue
            # 搜索消息内容
            for msg in conv["messages"]:
                if keyword.lower() in msg["content"].lower():
                    results.append(conv)
                    break
        return results

    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息

        返回:
            统计信息字典
        """
        total_messages = sum(len(conv["messages"]) for conv in self.conversations)
        user_messages = sum(
            sum(1 for msg in conv["messages"] if msg["role"] == "user")
            for conv in self.conversations
        )
        return {
            "total_conversations": len(self.conversations),
            "total_messages": total_messages,
            "user_messages": user_messages,
            "ai_messages": total_messages - user_messages
        }


# 全局实例
_ai_memory: Optional[AIMemory] = None


def get_ai_memory() -> AIMemory:
    """获取 AI 记忆实例（单例模式）"""
    global _ai_memory
    if _ai_memory is None:
        _ai_memory = AIMemory()
    return _ai_memory
