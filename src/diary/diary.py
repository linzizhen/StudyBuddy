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


# 全局单例
_diary_instance: Optional[Diary] = None


def get_diary() -> Diary:
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
