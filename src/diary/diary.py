"""
StudyPal 日记模块 v5 - 完整重构
功能：
- 每日情绪打卡（10种情绪）
- 日记记录（标题、正文、多图）
- 标签系统
- 天气记录
- 连续记录天数统计
- 情绪曲线计算
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from src.utils.file_lock import atomic_read_json, atomic_write_json


class DiaryEntry:
    """日记条目类"""
    
    # 情绪配置
    EMOTIONS = [
        {"level": 1, "emoji": "😢", "label": "难过", "color": "#FF6B6B"},
        {"level": 2, "emoji": "😔", "label": "低落", "color": "#FFA07A"},
        {"level": 3, "emoji": "😌", "label": "平静", "color": "#98D8C8"},
        {"level": 4, "emoji": "🤔", "label": "思考", "color": "#A29BFE"},
        {"level": 5, "emoji": "😊", "label": "愉快", "color": "#4ECDC4"},
        {"level": 6, "emoji": "😀", "label": "开心", "color": "#00D9B1"},
        {"level": 7, "emoji": "🥳", "label": "兴奋", "color": "#FFD93D"},
        {"level": 8, "emoji": "❤️", "label": "感恩", "color": "#FF6B9D"},
        {"level": 9, "emoji": "🌈", "label": "希望", "color": "#9B59B6"},
        {"level": 10, "emoji": "😴", "label": "疲惫", "color": "#8B949E"},
    ]
    
    WEATHER_OPTIONS = ["☀️ 晴", "🌤️ 多云", "☁️ 阴", "🌧️ 雨", "❄️ 雪", "🌪️ 台风"]
    
    DEFAULT_TAGS = ["学习", "生活", "运动", "旅行", "工作", "朋友", "家庭", "健康", "娱乐", "其他"]
    
    def __init__(self, data: Dict[str, Any] = None):
        if data:
            self.from_dict(data)
        else:
            self.id = datetime.now().strftime("%Y%m%d%H%M%S")
            self.date = datetime.now().strftime("%Y-%m-%d")
            self.emotion_level = 5
            self.emotion_emoji = "😊"
            self.emotion_label = "愉快"
            self.title = ""
            self.content = ""
            self.images: List[str] = []
            self.tags: List[str] = []
            self.weather = ""
            self.created_at = datetime.now().isoformat()
            self.updated_at = datetime.now().isoformat()

    def from_dict(self, data: Dict[str, Any]):
        """从字典加载"""
        self.id = data.get("id", datetime.now().strftime("%Y%m%d%H%M%S"))
        self.date = data.get("date", datetime.now().strftime("%Y-%m-%d"))
        self.emotion_level = data.get("emotion_level", 5)
        self.emotion_emoji = data.get("emotion_emoji", "😊")
        self.emotion_label = data.get("emotion_label", "愉快")
        self.title = data.get("title", "")
        self.content = data.get("content", "")
        self.images = data.get("images", [])
        self.tags = data.get("tags", [])
        self.weather = data.get("weather", "")
        self.created_at = data.get("created_at", datetime.now().isoformat())
        self.updated_at = data.get("updated_at", datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """转为字典"""
        return {
            "id": self.id,
            "date": self.date,
            "emotion_level": self.emotion_level,
            "emotion_emoji": self.emotion_emoji,
            "emotion_label": self.emotion_label,
            "title": self.title,
            "content": self.content,
            "images": self.images,
            "tags": self.tags,
            "weather": self.weather,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def get_emotion_by_level(cls, level: int) -> Dict[str, Any]:
        """获取情绪配置"""
        for emotion in cls.EMOTIONS:
            if emotion["level"] == level:
                return emotion
        return cls.EMOTIONS[4]  # 默认返回愉快


class Diary:
    """考研日记类 - 管理用户的情绪记录和日记"""
    
    def __init__(self, data_file: str = "data/diary.json"):
        self.data_file = data_file
        self.entries: List[Dict[str, Any]] = []
        self._load()

    def _load(self):
        """从文件加载数据"""
        data = atomic_read_json(self.data_file, {"entries": [], "tags": []})
        self.entries = data.get("entries", [])
        self.user_tags = data.get("tags", DiaryEntry.DEFAULT_TAGS)

    def _save(self):
        """保存数据到文件"""
        atomic_write_json(self.data_file, {
            "entries": self.entries,
            "tags": getattr(self, "user_tags", DiaryEntry.DEFAULT_TAGS)
        })

    def add_entry(
        self,
        emotion_level: int,
        title: str = "",
        content: str = "",
        images: List[str] = None,
        tags: List[str] = None,
        weather: str = ""
    ) -> DiaryEntry:
        """添加日记条目"""
        emotion = DiaryEntry.get_emotion_by_level(emotion_level)
        entry_data = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "emotion_level": emotion_level,
            "emotion_emoji": emotion["emoji"],
            "emotion_label": emotion["label"],
            "title": title,
            "content": content,
            "images": images or [],
            "tags": tags or [],
            "weather": weather,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        self.entries.insert(0, entry_data)
        self._save()
        entry = DiaryEntry()
        entry.from_dict(entry_data)
        return entry

    def update_entry(
        self,
        entry_id: str,
        emotion_level: int = None,
        title: str = None,
        content: str = None,
        images: List[str] = None,
        tags: List[str] = None,
        weather: str = None
    ) -> Optional[DiaryEntry]:
        """更新日记条目"""
        for i, entry in enumerate(self.entries):
            if entry.get("id") == entry_id:
                if emotion_level is not None:
                    emotion = DiaryEntry.get_emotion_by_level(emotion_level)
                    entry["emotion_level"] = emotion_level
                    entry["emotion_emoji"] = emotion["emoji"]
                    entry["emotion_label"] = emotion["label"]
                if title is not None:
                    entry["title"] = title
                if content is not None:
                    entry["content"] = content
                if images is not None:
                    entry["images"] = images
                if tags is not None:
                    entry["tags"] = tags
                if weather is not None:
                    entry["weather"] = weather
                entry["updated_at"] = datetime.now().isoformat()
                self._save()
                e = DiaryEntry()
                e.from_dict(entry)
                return e
        return None

    def get_today(self) -> Optional[DiaryEntry]:
        """获取今日日记"""
        today = datetime.now().strftime("%Y-%m-%d")
        for entry in self.entries:
            if entry.get("date") == today:
                e = DiaryEntry()
                e.from_dict(entry)
                return e
        return None

    def has_today(self) -> bool:
        """检查今日是否有日记"""
        return self.get_today() is not None

    def get_entry(self, entry_id: str) -> Optional[DiaryEntry]:
        """获取指定日记"""
        for entry in self.entries:
            if entry.get("id") == entry_id:
                e = DiaryEntry()
                e.from_dict(entry)
                return e
        return None

    def get_entries(self, limit: int = 50, offset: int = 0) -> List[DiaryEntry]:
        """获取日记列表"""
        result = []
        for entry in self.entries[offset:offset + limit]:
            e = DiaryEntry()
            e.from_dict(entry)
            result.append(e)
        return result

    def get_entries_filtered(
        self,
        keyword: str = None,
        emotion_level: int = None,
        tag: str = None,
        date_from: str = None,
        date_to: str = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[DiaryEntry]:
        """按条件筛选日记"""
        result = []
        for entry in self.entries:
            # 关键词筛选
            if keyword:
                kw = keyword.lower()
                if not (kw in entry.get("title", "").lower() or kw in entry.get("content", "").lower()):
                    continue
            
            # 情绪筛选
            if emotion_level is not None and entry.get("emotion_level") != emotion_level:
                continue
            
            # 标签筛选
            if tag and tag not in entry.get("tags", []):
                continue
            
            # 日期筛选
            if date_from and entry.get("date", "") < date_from:
                continue
            if date_to and entry.get("date", "") > date_to:
                continue
            
            e = DiaryEntry()
            e.from_dict(entry)
            result.append(e)
        
        return result[offset:offset + limit]

    def delete_entry(self, entry_id: str) -> bool:
        """删除日记"""
        for i, entry in enumerate(self.entries):
            if entry.get("id") == entry_id:
                self.entries.pop(i)
                self._save()
                return True
        return False

    def count(self) -> int:
        """返回条目总数（无需遍历创建 DiaryEntry 对象）"""
        return len(self.entries)

    def get_streak(self) -> int:
        """获取连续记录天数"""
        if not self.entries:
            return 0
        
        today = datetime.now().date()
        streak = 0
        check_date = today
        
        # 按日期分组（只取每天第一条）
        dates_with_entries = set()
        for entry in self.entries:
            if entry.get("date"):
                dates_with_entries.add(entry["date"])
        
        # 计算连续天数
        while True:
            date_str = check_date.strftime("%Y-%m-%d")
            if date_str in dates_with_entries:
                streak += 1
                check_date -= timedelta(days=1)
            else:
                # 今天没有也算连续
                if check_date == today:
                    check_date -= timedelta(days=1)
                    continue
                break
        
        return streak

    def get_emotion_curve(self, days: int = 30) -> Dict[str, Any]:
        """获取情绪曲线数据"""
        today = datetime.now()
        dates = []
        levels = []
        labels = []
        
        for i in range(days - 1, -1, -1):
            day = today - timedelta(days=i)
            date_str = day.strftime("%Y-%m-%d")
            
            entry = None
            for e in self.entries:
                if e.get("date") == date_str:
                    entry = e
                    break
            
            dates.append(day.strftime("%m/%d"))
            if entry:
                levels.append(entry.get("emotion_level", 3))
                labels.append(entry.get("emotion_label", "一般"))
            else:
                levels.append(None)
                labels.append(None)
        
        return {
            "dates": dates,
            "levels": levels,
            "labels": labels,
            "analysis": self._analyze_emotion_curve(levels, days)
        }

    def _analyze_emotion_curve(self, levels: List[int], days: int) -> str:
        """分析情绪曲线"""
        valid_levels = [l for l in levels if l is not None]
        if not valid_levels:
            return "还没有情绪记录，从今天开始记录吧~"
        
        avg = sum(valid_levels) / len(valid_levels)
        if avg >= 7:
            mood = "心情非常好"
        elif avg >= 5:
            mood = "心情不错"
        elif avg >= 3:
            mood = "心情一般"
        else:
            mood = "心情有些低落"
        
        return f"这{days}天你{mood}，平均情绪指数 {avg:.1f}/10。"

    def get_user_tags(self) -> List[str]:
        """获取用户标签"""
        return getattr(self, "user_tags", DiaryEntry.DEFAULT_TAGS)

    def add_user_tag(self, tag: str) -> bool:
        """添加用户标签"""
        tags = self.get_user_tags()
        if tag and tag not in tags:
            tags.append(tag)
            self.user_tags = tags
            self._save()
            return True
        return False

    def remove_user_tag(self, tag: str) -> bool:
        """删除用户标签"""
        tags = self.get_user_tags()
        if tag in tags:
            tags.remove(tag)
            self.user_tags = tags
            self._save()
            return True
        return False


"""
StudyPal 心情选择器存储
- 固定 8 个槽位：5 预设 + 3 自定义
- LRU 淘汰（自定义满 3 个时，淘汰最久未用）
- 选择心情时同步更新 last_used
- 用户数据隔离（data/user_moods.json）
"""

import json
import os
import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from src.utils.file_lock import atomic_read_json, atomic_write_json


PRESET_MOODS: List[Dict[str, Any]] = [
    {"id": "preset_happy",   "emoji": "😄", "label": "很开心", "value": 9},
    {"id": "preset_ok",      "emoji": "🙂", "label": "还不错", "value": 7},
    {"id": "preset_normal",  "emoji": "😐", "label": "一般般", "value": 5},
    {"id": "preset_sad",     "emoji": "😔", "label": "有点丧", "value": 3},
    {"id": "preset_cry",     "emoji": "😭", "label": "很难过", "value": 2},
]

PRESET_IDS = {m["id"] for m in PRESET_MOODS}
MAX_SLOTS = 8
MAX_CUSTOM = 3


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _validate_emoji(s: str) -> bool:
    """宽松校验：1-2 个码点即视为合法 emoji"""
    if not s:
        return False
    # 去除组合字符后检查码点数
    stripped = re.sub(r"[\u200D\uFE0F]", "", s)
    if len(stripped) == 0 or len(stripped) > 4:
        return False
    # 至少含一个非 ASCII 字符
    return any(ord(c) > 127 for c in s)


class MoodStore:
    """
    单用户心情 LRU 存储
    数据文件：data/user_moods.json
    结构：{
        "users": {
            "<user_id>": {
                "user_id": "...",
                "mood_slots": [ ...8 个槽位... ],
                "history": [ ...归档的自定义心情... ]
            }
        }
    }
    """

    def __init__(self, data_file: str = "data/user_moods.json"):
        self.data_file = data_file
        self._data: Dict[str, Any] = {}
        self._load()

    def _load(self):
        raw = atomic_read_json(self.data_file, {"users": {}})
        if not isinstance(raw, dict):
            raw = {"users": {}}
        self._data = raw
        self._data.setdefault("users", {})

    def _save(self):
        atomic_write_json(self.data_file, self._data)

    # ---------- 用户档 ----------

    def _get_user(self, user_id: str) -> Dict[str, Any]:
        users = self._data.setdefault("users", {})
        user = users.get(user_id)
        if not user:
            user = self._init_user(user_id)
            users[user_id] = user
            self._save()
        return user

    def _init_user(self, user_id: str) -> Dict[str, Any]:
        now = _now_iso()
        return {
            "user_id": user_id,
            "mood_slots": [
                {**m, "is_custom": False, "last_used": now}
                for m in PRESET_MOODS
            ],
            "history": [],
        }

    def _persist_user(self, user: Dict[str, Any]):
        self._data["users"][user["user_id"]] = user
        self._save()

    # ---------- 对外查询 ----------

    def get_mood_slots(self, user_id: str) -> List[Dict[str, Any]]:
        """返回按 last_used 降序排列的 8 个槽位"""
        user = self._get_user(user_id)
        slots = self._normalize_slots(user)
        slots.sort(key=lambda m: m.get("last_used") or "", reverse=True)
        return slots

    def get_mood_by_id(self, user_id: str, mood_id: str) -> Optional[Dict[str, Any]]:
        for m in self.get_mood_slots(user_id):
            if m["id"] == mood_id:
                return m
        return None

    def get_mood_by_label(self, user_id: str, label: str) -> Optional[Dict[str, Any]]:
        if not label:
            return None
        for m in self.get_mood_slots(user_id):
            if m["label"] == label:
                return m
        return None

    def get_mood_by_value(self, user_id: str, value: int) -> Optional[Dict[str, Any]]:
        """按情绪等级查找（兼容旧 diary.emotion_level 用法）"""
        try:
            v = int(value)
        except (TypeError, ValueError):
            return None
        for m in self.get_mood_slots(user_id):
            if m.get("value") == v:
                return m
        return None

    # ---------- 选择心情（更新 LRU）----------

    def touch_mood(self, user_id: str, mood_id: str) -> Optional[Dict[str, Any]]:
        """选择某个心情：更新 last_used 并重排"""
        user = self._get_user(user_id)
        self._normalize_slots(user)  # 先清理脏数据
        target = None
        for m in user["mood_slots"]:
            if m["id"] == mood_id:
                target = m
                break
        if not target:
            return None
        target["last_used"] = _now_iso()
        self._persist_user(user)
        return target

    # ---------- 添加自定义心情 ----------

    def add_custom_mood(
        self, user_id: str, emoji: str, label: str, value: int
    ) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        添加自定义心情
        返回: (added_mood, evicted_mood, slots)
            - added_mood: 新增或被刷新的心情对象
            - evicted_mood: 被淘汰的旧自定义心情（如有）
            - slots: 最新 8 个槽位（按 last_used 降序）
        """
        # 参数校验
        label = (label or "").strip()
        if not label or len(label) > 4:
            return None, None, self.get_mood_slots(user_id)
        if not _validate_emoji(emoji or ""):
            return None, None, self.get_mood_slots(user_id)
        try:
            value = int(value)
        except (TypeError, ValueError):
            return None, None, self.get_mood_slots(user_id)
        if not (1 <= value <= 10):
            return None, None, self.get_mood_slots(user_id)

        user = self._get_user(user_id)
        slots = self._normalize_slots(user)

        # 1) label 重复：刷新 last_used 并返回
        for m in slots:
            if m.get("is_custom") and m["label"] == label:
                m["emoji"] = emoji
                m["value"] = value
                m["last_used"] = _now_iso()
                user["mood_slots"] = slots
                self._persist_user(user)
                return m, None, self.get_mood_slots(user_id)

        custom_slots = [m for m in slots if m.get("is_custom")]
        evicted: Optional[Dict[str, Any]] = None

        if len(custom_slots) >= MAX_CUSTOM:
            # 2) 已满：淘汰最久未用
            victim = min(custom_slots, key=lambda m: m.get("last_used") or "")
            # 归档到 history
            history = user.setdefault("history", [])
            history.append({
                **victim,
                "archived_at": _now_iso(),
            })
            # 限制历史长度，防止无限增长
            if len(history) > 200:
                history[:] = history[-200:]
            # 在原位置替换
            for i, m in enumerate(slots):
                if m["id"] == victim["id"]:
                    new_mood = {
                        "id": f"custom_{uuid.uuid4().hex[:8]}",
                        "emoji": emoji,
                        "label": label,
                        "value": value,
                        "is_custom": True,
                        "last_used": _now_iso(),
                    }
                    slots[i] = new_mood
                    evicted = victim
                    added = new_mood
                    break
        else:
            # 3) 未满：填充到第一个空闲槽
            for i, m in enumerate(slots):
                if m.get("is_placeholder"):
                    new_mood = {
                        "id": f"custom_{uuid.uuid4().hex[:8]}",
                        "emoji": emoji,
                        "label": label,
                        "value": value,
                        "is_custom": True,
                        "last_used": _now_iso(),
                    }
                    slots[i] = new_mood
                    added = new_mood
                    break
            else:
                # 兜底：append 后裁剪
                new_mood = {
                    "id": f"custom_{uuid.uuid4().hex[:8]}",
                    "emoji": emoji,
                    "label": label,
                    "value": value,
                    "is_custom": True,
                    "last_used": _now_iso(),
                }
                slots.append(new_mood)
                # 确保预设都在
                preset_ids_in = {m["id"] for m in slots if not m.get("is_custom")}
                for p in PRESET_MOODS:
                    if p["id"] not in preset_ids_in:
                        slots.insert(0, {**p, "is_custom": False, "last_used": _now_iso()})
                slots = slots[:MAX_SLOTS]
                added = new_mood

        user["mood_slots"] = slots
        self._normalize_slots(user)  # 确保只保留 8 个，写入前规整
        self._persist_user(user)
        return added, evicted, self.get_mood_slots(user_id)

    # ---------- 槽位规整 ----------

    def _normalize_slots(self, user: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        把用户的 mood_slots 规整成正好 8 个槽位：
        - 确保 5 个预设齐全（缺失则补回）
        - 已有自定义保留
        - 不足 8 个时补占位符
        - 多余的自定义裁掉最早的（写入 history）
        """
        slots = list(user.get("mood_slots") or [])
        history = user.setdefault("history", [])

        # 分离预设/自定义
        preset_map: Dict[str, Dict[str, Any]] = {}
        customs: List[Dict[str, Any]] = []
        for m in slots:
            mid = m.get("id")
            if mid in PRESET_IDS:
                preset_map[mid] = m
            elif m.get("is_custom"):
                customs.append(m)

        # 1) 重建预设：保持 last_used
        now = _now_iso()
        new_slots: List[Dict[str, Any]] = []
        for p in PRESET_MOODS:
            existing = preset_map.get(p["id"])
            if existing:
                new_slots.append({**p, **existing, "is_custom": False})
            else:
                new_slots.append({**p, "is_custom": False, "last_used": now})

        # 2) 补足预设丢失的槽位（如果历史被裁掉）
        #    这里只处理预设 5 个齐全的情况

        # 3) 处理自定义：按 last_used 降序（最新的在前），淘汰最旧的
        customs.sort(key=lambda m: m.get("last_used") or "", reverse=True)

        if len(customs) > MAX_CUSTOM:
            archived = customs[:len(customs) - MAX_CUSTOM]
            for a in archived:
                history.append({**a, "archived_at": now})
            customs = customs[-MAX_CUSTOM:]

        new_slots.extend(customs)

        # 4) 占位符填充
        while len(new_slots) < MAX_SLOTS:
            new_slots.append({
                "id": f"placeholder_{len(new_slots)}",
                "emoji": "",
                "label": "",
                "value": 0,
                "is_custom": False,
                "is_placeholder": True,
                "last_used": "",
            })

        # 5) 裁剪（保留前 8 个，预设 5 个 + 最近的 3 个自定义）
        new_slots = new_slots[:MAX_SLOTS]

        # 6) 写回
        user["mood_slots"] = new_slots
        return new_slots


# 全局单例
_diary_instance: Optional["Diary"] = None
_mood_store_instance: Optional[MoodStore] = None


def get_mood_store() -> MoodStore:
    global _mood_store_instance
    if _mood_store_instance is None:
        _mood_store_instance = MoodStore()
    return _mood_store_instance


def get_diary() -> "Diary":
    """获取日记实例"""
    global _diary_instance
    if _diary_instance is None:
        _diary_instance = Diary()
    return _diary_instance


def get_emotion_tracker():
    """获取情绪追踪器"""
    from src.diary.diary import EmotionTracker
    return EmotionTracker(get_diary())


class EmotionTracker:
    """情绪追踪器"""
    
    def __init__(self, diary: Diary = None):
        self._diary = diary

    def set_diary(self, diary: Diary):
        self._diary = diary

    def has_today(self) -> bool:
        if not self._diary:
            return False
        return self._diary.has_today()

    def get_today_emotion(self) -> Optional[Dict[str, Any]]:
        if not self._diary:
            return None
        entry = self._diary.get_today()
        if entry:
            return {
                "level": entry.emotion_level,
                "emoji": entry.emotion_emoji,
                "label": entry.emotion_label
            }
        return None

    def is_emotion_low(self, threshold: int = 3) -> bool:
        emotion = self.get_today_emotion()
        if not emotion:
            return False
        return emotion.get("level", 5) <= threshold

    def get_recent_emotions(self, days: int = 7) -> Dict[str, Any]:
        if not self._diary:
            return {"levels": [], "trend": "unknown"}
        
        curve = self._diary.get_emotion_curve(days)
        levels = [l for l in curve["levels"] if l is not None]
        
        if len(levels) < 2:
            trend = "unknown"
        else:
            recent_avg = sum(levels[-3:]) / min(3, len(levels))
            early_avg = sum(levels[:3]) / min(3, len(levels))
            if recent_avg > early_avg:
                trend = "rising"
            elif recent_avg < early_avg:
                trend = "declining"
            else:
                trend = "stable"
        
        return {
            "levels": levels,
            "trend": trend,
            "average": sum(levels) / len(levels) if levels else 0
        }
