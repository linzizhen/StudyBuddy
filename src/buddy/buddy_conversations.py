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
