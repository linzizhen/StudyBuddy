"""搭子对话历史持久化"""
import secrets
from datetime import datetime
from typing import Any, Dict, List, Optional

from config import BUDDY_CONVERSATIONS_FILE
from src.utils.file_lock import atomic_read_json, atomic_write_json


class BuddyConversationStore:
    """管理搭子对话：活跃对话、历史列表、消息持久化"""

    def __init__(self, data_file: str = None):
        self.data_file = data_file or BUDDY_CONVERSATIONS_FILE
        self.conversations: List[Dict[str, Any]] = []
        self._load()

    def _load(self):
        data = atomic_read_json(self.data_file, {"conversations": []})
        self.conversations = data.get("conversations", [])

    def _save(self):
        atomic_write_json(self.data_file, {
            "conversations": self.conversations,
            "last_updated": datetime.now().isoformat(),
        })

    def _gen_id(self) -> str:
        return f"conv_{datetime.now().strftime('%Y%m%d%H%M%S')}_{secrets.token_hex(3)}"

    def _deactivate_all(self):
        for conv in self.conversations:
            conv["is_active"] = False

    def get_by_id(self, conv_id: str) -> Optional[Dict[str, Any]]:
        for conv in self.conversations:
            if conv["id"] == conv_id:
                return conv
        return None

    def get_active(self) -> Optional[Dict[str, Any]]:
        for conv in self.conversations:
            if conv.get("is_active"):
                return conv
        return None

    def get_active_id(self) -> Optional[str]:
        active = self.get_active()
        return active["id"] if active else None

    def create_new(
        self,
        buddy_role_key: str,
        buddy_name: str,
        buddy_emoji: str,
        title: str = "新对话",
    ) -> str:
        self._deactivate_all()
        now = datetime.now().isoformat()
        conv_id = self._gen_id()
        conv = {
            "id": conv_id,
            "title": title,
            "buddy_role_key": buddy_role_key,
            "buddy_name": buddy_name,
            "buddy_emoji": buddy_emoji,
            "created_at": now,
            "updated_at": now,
            "is_active": True,
            "messages": [],
        }
        self.conversations.insert(0, conv)
        self._save()
        return conv_id

    def activate(self, conv_id: str) -> bool:
        conv = self.get_by_id(conv_id)
        if not conv:
            return False
        self._deactivate_all()
        conv["is_active"] = True
        conv["updated_at"] = datetime.now().isoformat()
        self._save()
        return True

    def update_active_buddy(self, buddy_role_key: str, buddy_name: str, buddy_emoji: str):
        """切换搭子时更新活跃对话的搭子信息，保留消息"""
        active = self.get_active()
        if not active:
            return
        active["buddy_role_key"] = buddy_role_key
        active["buddy_name"] = buddy_name
        active["buddy_emoji"] = buddy_emoji
        active["updated_at"] = datetime.now().isoformat()
        self._save()

    def switch_role_with_isolation(
        self,
        new_role_key: str,
        new_role_name: str,
        new_role_emoji: str,
        new_role_avatar: str = "",
        user_name: str = "",
    ) -> Optional[Dict[str, Any]]:
        """
        切换角色 + 上下文隔离

        规则：
        1. 把当前对话摘要保存到长期记忆（去角色化）
        2. 清空当前对话的 messages
        3. 注入新角色的开场白（用"我"作为 assistant 消息，但**不**标记历史来源）
        4. 更新对话的搭子元数据
        5. 新角色**不知道**之前和其他角色的对话内容

        返回: 切换后的活跃对话 dict（含新 messages）
        """
        from src.buddy.buddy_memory import get_buddy_memory

        active = self.get_active()
        if not active:
            # 没有活跃对话时新建一个
            conv_id = self.create_new(
                buddy_role_key=new_role_key,
                buddy_name=new_role_name,
                buddy_emoji=new_role_emoji,
                title="新对话",
            )
            return self.get_by_id(conv_id)

        # 1. 保存旧对话摘要到长期记忆（去角色化）
        old_messages = active.get("messages", [])
        if old_messages and len(old_messages) >= 2:
            try:
                summary_text = self._make_role_neutral_summary(old_messages)
                if summary_text:
                    memory = get_buddy_memory()
                    memory.add_scene(
                        summary=summary_text,
                        scene_type="conversation",
                        details="",
                        tags=["对话摘要"],
                    )
            except Exception:
                pass

        # 2. 物理清空 messages
        active["messages"] = []

        # 3. 更新搭子元数据
        active["buddy_role_key"] = new_role_key
        active["buddy_name"] = new_role_name
        active["buddy_emoji"] = new_role_emoji
        active["buddy_avatar_url"] = new_role_avatar
        active["updated_at"] = datetime.now().isoformat()

        # 4. 注入新角色开场白（强制 assistant 身份，不告诉用户"之前是别人"）
        greeting = self._build_role_greeting(new_role_key, new_role_name, user_name)
        if greeting:
            active["messages"].append({
                "role": "assistant",
                "content": greeting,
                "timestamp": datetime.now().isoformat(),
                "buddy_role_key": new_role_key,
                "buddy_name": new_role_name,
                "buddy_emoji": new_role_emoji,
                "buddy_avatar_url": new_role_avatar,
                "is_greeting": True,
            })

        self._save()
        return active

    @staticmethod
    def _make_role_neutral_summary(messages: List[Dict[str, Any]]) -> str:
        """
        把对话历史生成"去角色化"摘要
        不提及任何搭子名字，只记录客观事件
        """
        user_msgs = [m for m in messages if m.get("role") == "user"]
        if not user_msgs:
            return ""

        # 简单取最近 3 条用户消息拼接
        recent = user_msgs[-3:]
        topics = []
        for m in recent:
            text = (m.get("content") or "").strip()
            if text:
                # 截断
                if len(text) > 40:
                    text = text[:40] + "…"
                topics.append(text)

        if not topics:
            return ""
        return f"用户近期聊到：{'；'.join(topics)}"

    @staticmethod
    def _build_role_greeting(role_key: str, role_name: str, user_name: str = "") -> str:
        """
        构建新角色的开场白
        强调自我介绍 + 锚定身份，**不**提及之前任何角色
        """
        user_part = f"，{user_name}" if user_name else ""
        greetings = {
            "xiaodou": f"嗨~ 我是小豆呀{user_part}，从现在起陪你学习啦~ 有什么想聊的尽管跟我说哦 💕",
            "aran": f"哟！我是阿燃{user_part}！准备好了吗？给我燃起来！⚡",
            "senior": f"你好，我是学姐{user_part}。学习上有问题尽管问，学姐当年也是这么走过来的 📚",
            "xiaoye": f"夜深了... 我是小夜{user_part}。今晚有什么心事想聊吗？ 🌙",
            "xj": f"Hey！我是戏精{user_part}！今天也要快乐学习哦~ 🎭",
            "azheng": f"你好，我是阿正{user_part}。让我们用数据说话。📊",
        }
        return greetings.get(role_key, f"你好，我是{role_name}{user_part}，接下来陪你一起学习。")

    def add_message(
        self,
        conv_id: str,
        role: str,
        content: str,
        buddy_snapshot: Optional[Dict[str, str]] = None,
    ) -> bool:
        conv = self.get_by_id(conv_id)
        if not conv:
            return False
        msg: Dict[str, Any] = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }
        if role == "assistant":
            from src.buddy.buddy_roles import BUDDY_ROLES
            snap = buddy_snapshot or {}
            role_key = snap.get("role_key") or conv.get("buddy_role_key", "")
            role_cfg = BUDDY_ROLES.get(role_key, {})
            msg["buddy_role_key"] = role_key
            msg["buddy_name"] = snap.get("name") or conv.get("buddy_name", role_cfg.get("name", ""))
            msg["buddy_emoji"] = snap.get("emoji") or conv.get("buddy_emoji", role_cfg.get("emoji", ""))
            msg["buddy_avatar_url"] = snap.get("avatar_url") or role_cfg.get("avatar_url", "")
        conv.setdefault("messages", []).append(msg)
        conv["updated_at"] = datetime.now().isoformat()
        if len(conv["messages"]) == 1 and role == "user":
            conv["title"] = content[:24] + ("..." if len(content) > 24 else "")
        self._save()
        return True

    def get_messages(self, conv_id: str) -> List[Dict[str, str]]:
        conv = self.get_by_id(conv_id)
        if not conv:
            return []
        return conv.get("messages", [])

    def list_summaries(self) -> List[Dict[str, Any]]:
        summaries = []
        for conv in self.conversations:
            summaries.append({
                "id": conv["id"],
                "title": conv.get("title", "未命名对话"),
                "buddy_role_key": conv.get("buddy_role_key", ""),
                "buddy_name": conv.get("buddy_name", ""),
                "buddy_emoji": conv.get("buddy_emoji", "💬"),
                "created_at": conv.get("created_at", ""),
                "updated_at": conv.get("updated_at", ""),
                "is_active": conv.get("is_active", False),
                "message_count": len(conv.get("messages", [])),
            })
        summaries.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return summaries

    def to_client_dict(self, conv: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": conv["id"],
            "title": conv.get("title", "未命名对话"),
            "buddy_role_key": conv.get("buddy_role_key", ""),
            "buddy_name": conv.get("buddy_name", ""),
            "buddy_emoji": conv.get("buddy_emoji", "💬"),
            "created_at": conv.get("created_at", ""),
            "updated_at": conv.get("updated_at", ""),
            "is_active": conv.get("is_active", False),
            "message_count": len(conv.get("messages", [])),
            "messages": conv.get("messages", []),
        }


_store: Optional[BuddyConversationStore] = None


def get_buddy_conversations() -> BuddyConversationStore:
    global _store
    if _store is None:
        _store = BuddyConversationStore()
    return _store
