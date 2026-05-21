"""
StudyPal 考研历程时间线模块
记录考研路上的里程碑事件

里程碑类型：
- start: 开始备考
- milestone: 重要节点
- achievement: 成就解锁
- struggle: 困难时刻
- breakthrough: 突破时刻
- emotion: 情绪变化
- exam: 考试相关

作者：StudyPal
日期：2026-04-27
重构日期：2026-04-30（文件锁保护）
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from src.utils.file_lock import atomic_read_json, atomic_write_json


class TimelineEvent:
    """时间线事件类"""

    def __init__(
        self,
        event_id: str,
        date: str,
        event_type: str,
        title: str,
        description: str = "",
        emotion: str = "",
        tags: List[str] = None,
        metadata: Dict[str, Any] = None
    ):
        self.id = event_id
        self.date = date
        self.type = event_type
        self.title = title
        self.description = description
        self.emotion = emotion
        self.tags = tags or []
        self.metadata = metadata or {}
        self.created_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "date": self.date,
            "type": self.type,
            "title": self.title,
            "description": self.description,
            "emotion": self.emotion,
            "tags": self.tags,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimelineEvent':
        event = cls(
            event_id=data.get("id", ""),
            date=data.get("date", ""),
            event_type=data.get("type", "milestone"),
            title=data.get("title", ""),
            description=data.get("description", ""),
            emotion=data.get("emotion", ""),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {})
        )
        if "created_at" in data:
            try:
                event.created_at = datetime.fromisoformat(data["created_at"])
            except (ValueError, TypeError):
                pass
        return event


class Timeline:
    """
    考研历程时间线

    记录考研路上的每一个重要时刻
    """

    def __init__(self, data_file: str = "data/timeline.json"):
        self.data_file = data_file
        self.events: List[Dict[str, Any]] = []
        self._load()

    def _load(self):
        """从文件加载数据"""
        data = atomic_read_json(self.data_file, {"events": []})
        self.events = data.get("events", [])

    def _save(self):
        """保存数据到文件"""
        atomic_write_json(self.data_file, {"events": self.events})

    def add_event(
        self,
        event_type: str,
        title: str,
        description: str = "",
        emotion: str = "",
        tags: List[str] = None,
        metadata: Dict[str, Any] = None,
        date: str = None
    ) -> str:
        """
        添加时间线事件

        参数：
            event_type: 事件类型
            title: 事件标题
            description: 事件描述
            emotion: 当时的情绪
            tags: 标签列表
            metadata: 附加数据
            date: 事件日期（默认今天）

        返回：事件ID
        """
        event_id = f"evt_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        event = TimelineEvent(
            event_id=event_id,
            date=date or datetime.now().strftime("%Y-%m-%d"),
            event_type=event_type,
            title=title,
            description=description,
            emotion=emotion,
            tags=tags,
            metadata=metadata
        )
        self.events.insert(0, event.to_dict())
        self._save()
        return event_id

    def get_events(
        self,
        event_type: str = None,
        start_date: str = None,
        end_date: str = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """获取时间线事件"""
        events = self.events

        if event_type:
            events = [e for e in events if e.get("type") == event_type]

        if start_date:
            events = [e for e in events if e.get("date", "") >= start_date]

        if end_date:
            events = [e for e in events if e.get("date", "") <= end_date]

        return events[:limit]

    def get_timeline(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取时间线（按日期排序）

        返回的事件按日期倒序排列
        """
        return self.get_events(limit=limit)

    def get_stats(self) -> Dict[str, Any]:
        """获取时间线统计"""
        type_count = {}
        for event in self.events:
            t = event.get("type", "other")
            type_count[t] = type_count.get(t, 0) + 1

        return {
            "total": len(self.events),
            "by_type": type_count,
            "first_date": self.events[-1].get("date") if self.events else None,
            "latest_date": self.events[0].get("date") if self.events else None
        }

    def delete_event(self, event_id: str) -> bool:
        """删除事件"""
        for i, event in enumerate(self.events):
            if event.get("id") == event_id:
                self.events.pop(i)
                self._save()
                return True
        return False

    def clear(self):
        """清空时间线"""
        self.events = []
        self._save()

    # ========== 自动检测里程碑 ==========

    MILESTONE_TYPES = [
        'study_start',      # 开始备考
        'first_complete',   # 首次完成某事
        'streak_record',    # 连续记录
        'score_break',      # 成绩突破
        'phase_complete',   # 阶段完成
        'exam_day',         # 考试当天
        'result_day',       # 出成绩
    ]

    # 里程碑检测记录（避免重复记录）
    _milestone_cache: Dict[str, str] = {}

    def auto_check_milestones(self, user_stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        自动检测并添加里程碑

        参数:
            user_stats: 用户统计数据

        返回:
            新增的里程碑列表
        """
        new_milestones = []

        # 检查开始备考
        if self._check_milestone('study_start', user_stats):
            evt = self._add_milestone(
                event_type='start',
                title='开始考研备考之旅',
                description='迈出了考研的第一步',
                emotion='期待',
                tags=['start', 'milestone']
            )
            if evt:
                new_milestones.append(evt)

        # 检查连续学习里程碑
        streak = user_stats.get('streak_days', 0)
        streak_milestones = {3: '三天坚持', 7: '一周坚持', 14: '双周坚持', 30: '月度坚持', 100: '百日坚持'}
        for days, label in streak_milestones.items():
            if streak >= days:
                key = f'streak_{days}'
                if self._check_milestone(key, user_stats):
                    evt = self._add_milestone(
                        event_type='milestone',
                        title=f'连续学习{days}天达成！',
                        description=f'坚持了{days}天，非常了不起',
                        emotion='骄傲',
                        tags=['streak', 'milestone']
                    )
                    if evt:
                        new_milestones.append(evt)

        # 检查首次日记记录
        if user_stats.get('diary_count', 0) >= 1:
            if self._check_milestone('first_diary', user_stats):
                evt = self._add_milestone(
                    event_type='milestone',
                    title='写下第一篇日记',
                    description='开始记录考研生活',
                    emotion='满足',
                    tags=['diary', 'milestone']
                )
                if evt:
                    new_milestones.append(evt)

        # 检查连续日记里程碑
        diary_streak = user_stats.get('diary_streak', 0)
        diary_milestones = {7: '一周日记', 30: '月度日记'}
        for days, label in diary_milestones.items():
            if diary_streak >= days:
                key = f'diary_streak_{days}'
                if self._check_milestone(key, user_stats):
                    evt = self._add_milestone(
                        event_type='milestone',
                        title=f'连续记录{days}天日记',
                        description='坚持记录每一天的情绪变化',
                        emotion='满足',
                        tags=['diary', 'milestone']
                    )
                    if evt:
                        new_milestones.append(evt)

        return new_milestones

    def _check_milestone(self, key: str, user_stats: Dict[str, Any]) -> bool:
        """检查里程碑是否已记录"""
        if key not in self._milestone_cache:
            # 从现有事件中检查
            for event in self.events:
                if key in event.get('tags', []):
                    self._milestone_cache[key] = event.get('id', '')
                    return False
            self._milestone_cache[key] = 'checked'
            return True
        return self._milestone_cache.get(key) == 'checked'

    def _add_milestone(
        self,
        event_type: str,
        title: str,
        description: str = "",
        emotion: str = "满足",
        tags: List[str] = None
    ) -> Optional[Dict[str, Any]]:
        """添加里程碑并返回"""
        event_id = self.add_event(
            event_type=event_type,
            title=title,
            description=description,
            emotion=emotion,
            tags=tags or ['milestone']
        )
        # 找到刚添加的事件
        for event in self.events:
            if event.get('id') == event_id:
                return event
        return None

    # ========== 自动记录 ==========

    def record_study_start(self, subject: str = "开始备考") -> str:
        """记录开始学习"""
        return self.add_event(
            event_type="start",
            title=f"开始了 {subject} 之旅",
            description="迈出考研的第一步",
            emotion="期待",
            tags=["start", subject]
        )

    def record_milestone(
        self,
        title: str,
        description: str = "",
        emotion: str = "满足"
    ) -> str:
        """记录里程碑"""
        return self.add_event(
            event_type="milestone",
            title=title,
            description=description,
            emotion=emotion,
            tags=["milestone"]
        )

    def record_achievement(
        self,
        achievement_name: str,
        description: str = ""
    ) -> str:
        """记录成就解锁"""
        return self.add_event(
            event_type="achievement",
            title=f"解锁成就：{achievement_name}",
            description=description,
            emotion="兴奋",
            tags=["achievement"]
        )

    def record_struggle(
        self,
        title: str,
        description: str = "",
        emotion: str = "沮丧"
    ) -> str:
        """记录困难时刻"""
        return self.add_event(
            event_type="struggle",
            title=title,
            description=description,
            emotion=emotion,
            tags=["struggle", "challenge"]
        )

    def record_breakthrough(
        self,
        title: str,
        description: str = "",
        subject: str = ""
    ) -> str:
        """记录突破时刻"""
        return self.add_event(
            event_type="breakthrough",
            title=title,
            description=description,
            emotion="开心",
            tags=["breakthrough", subject] if subject else ["breakthrough"]
        )

    def record_emotion_change(
        self,
        emotion: str,
        reason: str = ""
    ) -> str:
        """记录情绪变化"""
        emotion_labels = {
            "1": "崩溃",
            "2": "难过",
            "3": "一般",
            "4": "不错",
            "5": "开心"
        }
        return self.add_event(
            event_type="emotion",
            title=f"今天心情：{emotion_labels.get(str(emotion), emotion)}",
            description=reason,
            emotion=emotion,
            tags=["emotion"]
        )


# 全局单例
_timeline_instance: Optional[Timeline] = None


def get_timeline() -> Timeline:
    """获取时间线实例"""
    global _timeline_instance
    if _timeline_instance is None:
        _timeline_instance = Timeline()
    return _timeline_instance
