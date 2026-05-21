"""
StudyPal 搭子记忆模块
管理搭子的三层记忆系统

三层记忆：
1. 用户画像（长期不变的基本信息）
2. 场景记忆（与用户相关的具体事件）
3. 对话摘要（会话中的关键信息）

作者：StudyPal
日期：2026-04-27
重构日期：2026-04-30（文件锁保护）
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from src.utils.file_lock import atomic_read_json, atomic_write_json


class BuddyMemory:
    """
    搭子记忆类
    
    管理搭子的三层记忆系统
    """

    def __init__(self, data_file: str = "data/buddy_memory.json"):
        self.data_file = data_file
        self.data: Dict[str, Any] = {
            "profile_notes": {},
            "scenes": [],
            "conversation_summaries": [],
            "preferences": {},
            "updated_at": ""
        }
        self._load()

    def _load(self):
        """从文件加载数据"""
        default = self._default_data()
        self.data = atomic_read_json(self.data_file, default)

    def _default_data(self) -> Dict[str, Any]:
        return {
            "profile_notes": {},
            "scenes": [],
            "conversation_summaries": [],
            "preferences": {},
            "updated_at": datetime.now().isoformat()
        }

    def _save(self):
        """保存数据到文件"""
        self.data["updated_at"] = datetime.now().isoformat()
        atomic_write_json(self.data_file, self.data)

    # ========== 用户画像笔记 ==========

    def set_profile_note(self, key: str, value: Any):
        """设置用户画像笔记"""
        self.data["profile_notes"][key] = {
            "value": value,
            "updated_at": datetime.now().isoformat()
        }
        self._save()

    def get_profile_note(self, key: str) -> Optional[Any]:
        """获取用户画像笔记"""
        note = self.data.get("profile_notes", {}).get(key)
        return note["value"] if note else None

    def get_all_profile_notes(self) -> Dict[str, Any]:
        """获取所有用户画像笔记"""
        notes = {}
        for key, note in self.data.get("profile_notes", {}).items():
            notes[key] = note["value"]
        return notes

    # ========== 场景记忆 ==========

    def add_scene(
        self,
        summary: str,
        scene_type: str,
        details: str = "",
        tags: List[str] = None,
        feeling: str = "",
        buddy_said: str = ""
    ) -> str:
        """
        添加场景记忆
        
        参数：
            summary: 事件摘要
            scene_type: 类型（achievement/struggle/conversation/emotion/milestone）
            details: 详细描述
            tags: 标签列表
            feeling: 用户当时的感受
            buddy_said: 搭子当时说的话
        
        返回：场景ID
        """
        scene_id = f"scene_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        scene = {
            "id": scene_id,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "type": scene_type,
            "summary": summary,
            "details": details,
            "tags": tags or [],
            "feeling": feeling,
            "buddy_said": buddy_said,
            "created_at": datetime.now().isoformat()
        }
        self.data["scenes"].insert(0, scene)
        self._save()
        return scene_id

    def get_scenes(
        self,
        scene_type: str = None,
        tags: List[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """获取场景记忆"""
        scenes = self.data.get("scenes", [])

        if scene_type:
            scenes = [s for s in scenes if s.get("type") == scene_type]

        if tags:
            scenes = [
                s for s in scenes
                if any(tag in s.get("tags", []) for tag in tags)
            ]

        return scenes[:limit]

    def get_recent_scenes(self, days: int = 7) -> List[Dict[str, Any]]:
        """获取最近N天的场景"""
        scenes = []
        cutoff = datetime.now().timestamp() - (days * 86400)

        for scene in self.data.get("scenes", []):
            try:
                created = datetime.fromisoformat(scene["created_at"]).timestamp()
                if created >= cutoff:
                    scenes.append(scene)
            except (KeyError, ValueError):
                continue

        return scenes

    def search_scenes(self, keyword: str) -> List[Dict[str, Any]]:
        """搜索场景记忆"""
        keyword = keyword.lower()
        results = []

        for scene in self.data.get("scenes", []):
            if (
                keyword in scene.get("summary", "").lower() or
                keyword in scene.get("details", "").lower() or
                any(keyword in tag.lower() for tag in scene.get("tags", []))
            ):
                results.append(scene)

        return results

    # ========== 对话摘要 ==========

    def add_conversation_summary(
        self,
        topic: str,
        key_points: List[str],
        user_feeling: str = "",
        date: str = None
    ):
        """添加对话摘要"""
        summary = {
            "id": f"conv_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "date": date or datetime.now().strftime("%Y-%m-%d"),
            "topic": topic,
            "key_points": key_points,
            "user_feeling": user_feeling,
            "created_at": datetime.now().isoformat()
        }
        self.data["conversation_summaries"].insert(0, summary)
        self._save()

    def get_conversation_summaries(
        self,
        topic_keyword: str = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """获取对话摘要"""
        summaries = self.data.get("conversation_summaries", [])

        if topic_keyword:
            keyword = topic_keyword.lower()
            summaries = [
                s for s in summaries
                if keyword in s.get("topic", "").lower()
            ]

        return summaries[:limit]

    # ========== 偏好设置 ==========

    def set_preference(self, key: str, value: Any):
        """设置用户偏好"""
        self.data["preferences"][key] = value
        self._save()

    def get_preference(self, key: str, default: Any = None) -> Any:
        """获取用户偏好"""
        return self.data.get("preferences", {}).get(key, default)

    # ========== 记忆检索与注入 ==========

    def recall(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        检索相关记忆
        
        用于在对话时注入相关记忆
        """
        results = []
        query_lower = query.lower()

        # 搜索场景记忆
        for scene in self.data.get("scenes", [])[:30]:
            score = 0
            matched_fields = []

            if query_lower in scene.get("summary", "").lower():
                score += 3
                matched_fields.append("summary")
            if query_lower in scene.get("details", "").lower():
                score += 2
                matched_fields.append("details")
            if any(query_lower in tag.lower() for tag in scene.get("tags", [])):
                score += 2
                matched_fields.append("tags")
            if query_lower in scene.get("feeling", "").lower():
                score += 1
                matched_fields.append("feeling")

            if score > 0:
                results.append({
                    "source": "scene",
                    "score": score,
                    "data": scene,
                    "matched_fields": matched_fields
                })

        # 搜索对话摘要
        for summary in self.data.get("conversation_summaries", [])[:20]:
            score = 0
            matched_fields = []

            if query_lower in summary.get("topic", "").lower():
                score += 2
                matched_fields.append("topic")
            if any(query_lower in point.lower() for point in summary.get("key_points", [])):
                score += 1
                matched_fields.append("key_points")

            if score > 0:
                results.append({
                    "source": "conversation",
                    "score": score,
                    "data": summary,
                    "matched_fields": matched_fields
                })

        # 搜索用户画像笔记
        for key, note in self.data.get("profile_notes", {}).items():
            if query_lower in key.lower() or query_lower in str(note.get("value", "")).lower():
                results.append({
                    "source": "profile",
                    "score": 1,
                    "data": {"key": key, "value": note["value"]},
                    "matched_fields": ["key", "value"]
                })

        # 按分数排序
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def build_context_for_ai(self, current_topic: str = None) -> str:
        """
        为AI对话构建上下文记忆字符串
        
        这是让搭子"有记忆"的核心方法
        """
        parts = []

        # 1. 用户画像笔记
        profile_notes = self.get_all_profile_notes()
        if profile_notes:
            notes_parts = [f"{k}：{v}" for k, v in profile_notes.items()]
            parts.append(f"【用户特征】：{'；'.join(notes_parts)}")

        # 2. 相关记忆（根据话题）
        if current_topic:
            memories = self.recall(current_topic)
            if memories:
                parts.append(f"\n【关于「{current_topic}」的记忆】：")
                for mem in memories[:3]:
                    data = mem["data"]
                    if mem["source"] == "scene":
                        parts.append(
                            f"- {data.get('date')}：{data.get('summary')}"
                        )
                    elif mem["source"] == "conversation":
                        points = "；".join(data.get("key_points", [])[:2])
                        parts.append(
                            f"- {data.get('date')} 聊过「{data.get('topic')}」，"
                            f"提到过：{points}"
                        )

        # 3. 最近的场景记忆（最近7天）
        recent_scenes = self.get_recent_scenes(7)
        if recent_scenes:
            parts.append(f"\n【最近发生的事】（共{len(recent_scenes)}条）：")
            for scene in recent_scenes[:5]:
                parts.append(
                    f"- {scene.get('date')}：{scene.get('summary')}"
                )

        # 4. 最近的对话话题
        recent_convs = self.get_conversation_summaries(limit=5)
        if recent_convs:
            topics = [f"「{c.get('topic')}」" for c in recent_convs[:3]]
            parts.append(f"【最近聊过的话题】：{', '.join(topics)}")

        return "\n".join(parts) if parts else ""

    def get_memory_stats(self) -> Dict[str, int]:
        """获取记忆统计"""
        return {
            "profile_notes": len(self.data.get("profile_notes", {})),
            "scenes": len(self.data.get("scenes", [])),
            "conversations": len(self.data.get("conversation_summaries", [])),
            "preferences": len(self.data.get("preferences", {}))
        }

    def clear(self):
        """清空所有记忆"""
        self.data = self._default_data()
        self._save()


# 全局单例
_memory_instance: Optional[BuddyMemory] = None


def get_buddy_memory() -> BuddyMemory:
    """获取搭子记忆实例"""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = BuddyMemory()
    return _memory_instance
