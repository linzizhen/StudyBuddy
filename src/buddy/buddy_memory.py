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

    def __init__(self, data_file: str = None, user_id: str = None):
        if data_file:
            self.data_file = data_file
        elif user_id:
            self.data_file = f"data/buddy_memory_{user_id}.json"
        else:
            self.data_file = "data/buddy_memory.json"
        self.user_id = user_id
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
        buddy_said: str = "",
        importance: int = None
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
            importance: 重要性（1-4），自动推断

        返回：场景ID
        """
        # 自动推断重要性
        if importance is None:
            auto_map = {"achievement": 3, "milestone": 4, "struggle": 3, "emotion": 2, "conversation": 2}
            importance = auto_map.get(scene_type, 1)

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
            "importance": importance,
            "access_count": 0,
            "last_accessed": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat()
        }
        self.data["scenes"].insert(0, scene)
        self._auto_forget()
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

    # ========== 记忆增强：重要性评分 + 自动遗忘 ==========

    def add_scene_with_importance(
        self,
        summary: str,
        scene_type: str,
        details: str = "",
        tags: List[str] = None,
        feeling: str = "",
        buddy_said: str = "",
        importance: int = None
    ) -> str:
        """
        添加带重要性评分的场景记忆

        importance: 1=低(日常), 2=中(学习), 3=高(成就/困难), 4=极高(里程碑)
        自动推断：如果没传，根据 scene_type 自动判断
        """
        # 自动推断重要性
        if importance is None:
            auto_map = {
                "achievement": 3,
                "milestone": 4,
                "struggle": 3,
                "emotion": 2,
                "conversation": 2,
            }
            importance = auto_map.get(scene_type, 1)

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
            "importance": importance,
            "access_count": 0,
            "last_accessed": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat()
        }
        self.data["scenes"].insert(0, scene)
        self._auto_forget()
        self._save()
        return scene_id

    def _auto_forget(self, min_importance: int = 2, max_scenes: int = 100):
        """
        自动遗忘低重要性记忆

        规则：
        - 重要性 < min_importance 且访问次数为0的，优先删除
        - 总场景数超过 max_scenes 时，删除最低分的场景
        - 30天以上的低重要性记忆自动降级
        """
        import time as time_module

        scenes = self.data["scenes"]
        now_ts = datetime.now().timestamp()
        cutoff_30d = now_ts - (30 * 86400)

        # 策略1：删除从未被访问过的低重要性记忆（超过7天）
        to_remove = []
        for i, scene in enumerate(scenes):
            importance = scene.get("importance", 1)
            access_count = scene.get("access_count", 0)
            try:
                created = datetime.fromisoformat(scene["created_at"]).timestamp()
                age_days = (now_ts - created) / 86400
            except (KeyError, ValueError):
                age_days = 0

            # 30天以上 + 从未访问 + 低重要性
            if age_days > 30 and access_count == 0 and importance <= 1:
                to_remove.append(i)

        # 策略2：总数超限时，按遗忘分数排序删除
        if len(scenes) > max_scenes:
            scored = []
            for scene in scenes:
                try:
                    created = datetime.fromisoformat(scene["created_at"]).timestamp()
                    age_days = (now_ts - created) / 86400
                except (KeyError, ValueError):
                    age_days = 0

                # 遗忘分数 = age_days / importance，越高越该遗忘
                importance = scene.get("importance", 1)
                forget_score = age_days / max(importance, 1)
                scored.append((forget_score, scene))

            scored.sort(reverse=True)
            # 保留前 max_scenes 条，其余标记删除
            keep_ids = {s[1]["id"] for s in scored[:max_scenes]}
            to_remove = [i for i, s in enumerate(scenes) if s["id"] not in keep_ids]

        # 倒序删除
        for i in sorted(to_remove, reverse=True):
            scenes.pop(i)

    def smart_recall(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        智能记忆检索：综合相关性 + 重要性 + 时效性

        遗忘分数 = age_days / (importance * 0.5 + access_count)
        分数越低 = 越值得保留
        """
        results = self.recall(query, limit=20)
        now_ts = datetime.now().timestamp()

        scored_results = []
        for result in results:
            data = result["data"]
            try:
                created = datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())).timestamp()
                age_days = max(0.1, (now_ts - created) / 86400)
            except (KeyError, ValueError):
                age_days = 1

            importance = data.get("importance", 1)
            access_count = data.get("access_count", 0)

            # 综合评分 = 相关性 * 遗忘分数的反比
            relevance = result["score"]
            forget_score = age_days / max(importance * 0.5 + access_count * 0.3, 0.1)
            final_score = relevance * (1 / (1 + forget_score * 0.5))

            scored_results.append({
                **result,
                "final_score": round(final_score, 3),
                "age_days": round(age_days, 1),
                "importance": importance
            })

        scored_results.sort(key=lambda x: x["final_score"], reverse=True)
        return scored_results[:limit]

    def touch_scene(self, scene_id: str):
        """标记场景被访问过（增加访问计数，降低遗忘分数）"""
        for scene in self.data.get("scenes", []):
            if scene.get("id") == scene_id:
                scene["access_count"] = scene.get("access_count", 0) + 1
                scene["last_accessed"] = datetime.now().isoformat()
                self._save()
                break


# 全局单例（向后兼容）
_memory_instance: Optional[BuddyMemory] = None


def get_buddy_memory(user_id: str = None) -> BuddyMemory:
    """获取搭子记忆实例"""
    if user_id:
        from src.core.buddy import get_buddy_memory as _pooled
        return _pooled(user_id)
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = BuddyMemory()
    return _memory_instance
