"""
StudyPal 考研日记模块
管理用户的情绪记录和日记

功能：
- 每日情绪打卡
- 日记记录
- 情绪曲线计算
- 搭子回复存储

作者：StudyPal
日期：2026-04-27
重构日期：2026-04-30（文件锁保护）
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from src.utils.file_lock import atomic_read_json, atomic_write_json


class DiaryEntry:
    """
    日记条目类
    """

    EMOTION_LABELS = {
        1: "很难受",
        2: "有点丧",
        3: "一般",
        4: "还好",
        5: "很开心"
    }

    STUDY_FEELINGS = ["充实", "疲惫", "焦虑", "麻木", "充实+疲惫"]

    def __init__(self, data: Dict[str, Any] = None):
        if data:
            self.from_dict(data)
        else:
            self.id = datetime.now().strftime("%Y%m%d")
            self.date = datetime.now().strftime("%Y-%m-%d")
            self.emotion_level = 3
            self.emotion_label = self.EMOTION_LABELS[3]
            self.study_feeling = ""
            self.study_hours = 0
            self.biggest_event = ""
            self.words_to_buddy = ""
            self.buddy_response = ""
            self.weather = ""
            self.tasks_completed: List[str] = []
            self.created_at = datetime.now().isoformat()

    def from_dict(self, data: Dict[str, Any]):
        """从字典加载"""
        self.id = data.get("id", datetime.now().strftime("%Y%m%d"))
        self.date = data.get("date", datetime.now().strftime("%Y-%m-%d"))
        self.emotion_level = data.get("emotion_level", 3)
        self.emotion_label = data.get("emotion_label", self.EMOTION_LABELS.get(self.emotion_level, "一般"))
        self.study_feeling = data.get("study_feeling", "")
        self.study_hours = data.get("study_hours", 0)
        self.biggest_event = data.get("biggest_event", "")
        self.words_to_buddy = data.get("words_to_buddy", "")
        self.buddy_response = data.get("buddy_response", "")
        self.weather = data.get("weather", "")
        self.tasks_completed = data.get("tasks_completed", [])
        self.created_at = data.get("created_at", datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """转为字典"""
        return {
            "id": self.id,
            "date": self.date,
            "emotion_level": self.emotion_level,
            "emotion_label": self.emotion_label,
            "study_feeling": self.study_feeling,
            "study_hours": self.study_hours,
            "biggest_event": self.biggest_event,
            "words_to_buddy": self.words_to_buddy,
            "buddy_response": self.buddy_response,
            "weather": self.weather,
            "tasks_completed": self.tasks_completed,
            "created_at": self.created_at
        }


class Diary:
    """
    考研日记类

    管理用户的情绪记录和日记
    """

    def __init__(self, data_file: str = "data/diary.json"):
        self.data_file = data_file
        self.entries: List[Dict[str, Any]] = []
        self._load()

    def _load(self):
        """从文件加载数据"""
        data = atomic_read_json(self.data_file, {"entries": []})
        self.entries = data.get("entries", [])

    def _save(self):
        """保存数据到文件"""
        atomic_write_json(self.data_file, {"entries": self.entries})

    def add_entry(
        self,
        emotion_level: int,
        study_feeling: str = "",
        study_hours: float = 0,
        biggest_event: str = "",
        words_to_buddy: str = "",
        weather: str = "",
        tasks_completed: List[str] = None
    ) -> DiaryEntry:
        """添加日记条目"""
        entry_data = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "emotion_level": emotion_level,
            "emotion_label": DiaryEntry.EMOTION_LABELS.get(emotion_level, "一般"),
            "study_feeling": study_feeling,
            "study_hours": study_hours,
            "biggest_event": biggest_event,
            "words_to_buddy": words_to_buddy,
            "buddy_response": "",
            "weather": weather,
            "tasks_completed": tasks_completed or [],
            "created_at": datetime.now().isoformat()
        }
        self.entries.insert(0, entry_data)
        self._save()
        entry = DiaryEntry()
        entry.from_dict(entry_data)
        return entry

    def update_entry(self, entry_id: str, **kwargs) -> bool:
        """更新日记条目"""
        for i, entry in enumerate(self.entries):
            if entry.get("id") == entry_id:
                for key, value in kwargs.items():
                    if key in [
                        "emotion_level", "study_feeling", "study_hours",
                        "biggest_event", "words_to_buddy", "buddy_response",
                        "weather", "tasks_completed"
                    ]:
                        if key == "emotion_level":
                            entry["emotion_label"] = DiaryEntry.EMOTION_LABELS.get(value, "一般")
                        entry[key] = value
                self._save()
                return True
        return False

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

    def get_entries(self, limit: int = 30) -> List[DiaryEntry]:
        """获取日记列表"""
        result = []
        for entry in self.entries[:limit]:
            e = DiaryEntry()
            e.from_dict(entry)
            result.append(e)
        return result

    def get_entries_by_emotion(
        self,
        emotion_level: int = None,
        emotion_range: tuple = None
    ) -> List[DiaryEntry]:
        """按情绪筛选日记"""
        result = []
        for entry in self.entries:
            if emotion_level is not None:
                if entry.get("emotion_level") == emotion_level:
                    e = DiaryEntry()
                    e.from_dict(entry)
                    result.append(e)
            elif emotion_range:
                low, high = emotion_range
                level = entry.get("emotion_level", 3)
                if low <= level <= high:
                    e = DiaryEntry()
                    e.from_dict(entry)
                    result.append(e)
        return result

    def get_emotion_curve(self, days: int = 7) -> Dict[str, Any]:
        """
        获取情绪曲线数据

        返回：
        {
            "dates": ["4/21", "4/22", ...],
            "levels": [3, 2, 4, 3, 3, 4, 4],
            "labels": ["一般", "有点丧", ...],
            "events": {"4/22": "做了第一套模拟卷"},
            "analysis": "这周情绪整体不错..."
        }
        """
        today = datetime.now()
        dates = []
        levels = []
        labels = []
        events = {}

        for i in range(days - 1, -1, -1):
            day = today - timedelta(days=i)
            date_str = day.strftime("%Y-%m-%d")
            short_date = day.strftime("%m/%d")

            entry = None
            for e in self.entries:
                if e.get("date") == date_str:
                    entry = e
                    break

            dates.append(short_date)
            if entry:
                levels.append(entry.get("emotion_level", 3))
                labels.append(entry.get("emotion_label", "一般"))
                if entry.get("biggest_event"):
                    events[short_date] = entry.get("biggest_event")
            else:
                levels.append(None)
                labels.append(None)

        analysis = self._analyze_emotion_curve(levels, events, days)

        return {
            "dates": dates,
            "levels": levels,
            "labels": labels,
            "events": events,
            "analysis": analysis
        }

    def _analyze_emotion_curve(
        self,
        levels: List[int],
        events: Dict[str, str],
        days: int = 7
    ) -> str:
        """分析情绪曲线"""
        valid_levels = [l for l in levels if l is not None]
        if not valid_levels:
            return "还没有情绪记录，从今天开始记录吧~"

        avg = sum(valid_levels) / len(valid_levels)
        recent = valid_levels[-3:] if len(valid_levels) >= 3 else valid_levels
        recent_avg = sum(recent) / len(recent)

        if avg >= 4:
            mood = "整体心情不错"
        elif avg >= 3:
            mood = "整体心情一般"
        else:
            mood = "最近心情有些低落"

        if recent_avg > avg:
            trend = "在回升"
        elif recent_avg < avg:
            trend = "有些波动"
        else:
            trend = "比较稳定"

        return f"这{days}天你{mood}，情绪{trend}。"


class EmotionTracker:
    """
    情绪追踪器

    为关心引擎提供情绪数据
    """

    def __init__(self, diary: Diary = None):
        self._diary = diary

    def set_diary(self, diary: Diary):
        """设置日记实例"""
        self._diary = diary

    def has_today(self) -> bool:
        """检查今日是否有情绪记录"""
        if not self._diary:
            return False
        return self._diary.has_today()

    def get_today_emotion(self) -> Optional[Dict[str, Any]]:
        """获取今日情绪"""
        if not self._diary:
            return None
        entry = self._diary.get_today()
        if entry:
            return {
                "level": entry.emotion_level,
                "label": entry.emotion_label,
                "feeling": entry.study_feeling
            }
        return None

    def is_emotion_low(self, threshold: int = 2) -> bool:
        """检查情绪是否偏低"""
        emotion = self.get_today_emotion()
        if not emotion:
            return False
        return emotion.get("level", 3) <= threshold

    def get_recent_emotions(self, days: int = 7) -> Dict[str, Any]:
        """获取最近情绪数据"""
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
            "average": sum(levels) / len(levels) if levels else 0,
            "events": curve.get("events", {})
        }


# 全局单例
_diary_instance: Optional[Diary] = None


def get_diary() -> Diary:
    """获取日记实例"""
    global _diary_instance
    if _diary_instance is None:
        _diary_instance = Diary()
    return _diary_instance


def get_emotion_tracker() -> EmotionTracker:
    """获取情绪追踪器实例"""
    return EmotionTracker(get_diary())
