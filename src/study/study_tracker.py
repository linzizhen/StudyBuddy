"""
StudyPal 学习追踪器
轻量化学习数据追踪，为主动关心引擎提供数据支撑

功能：
- 记录学习时段
- 计算连续学习时长
- 统计日/周学习量
- 替代摄像头监督的行为感知

作者：StudyPal
日期：2026-04-27
重构日期：2026-04-30（文件锁保护）
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from src.utils.file_lock import atomic_read_json, atomic_write_json


class StudyTracker:
    """
    学习追踪器类

    通过打卡数据感知用户学习状态，为关心引擎提供数据
    """

    def __init__(self, data_file: str = "data/study_tracker.json"):
        self.data_file = data_file
        self.data: Dict[str, Any] = {
            "sessions": [],        # 学习时段记录
            "today_start": None,   # 今日开始学习时间
            "today_minutes": 0,    # 今日累计学习分钟
            "streak_days": 0,      # 连续学习天数
            "last_study_date": None,
            "last_active_time": None,
        }
        self._load()

    def _load(self):
        """从文件加载数据"""
        default = self._default_data()
        self.data = atomic_read_json(self.data_file, default)

    def _default_data(self) -> Dict[str, Any]:
        today = datetime.now().strftime("%Y-%m-%d")
        return {
            "sessions": [],
            "today_start": None,
            "today_minutes": 0,
            "streak_days": 0,
            "last_study_date": None,
            "last_active_time": datetime.now().isoformat()
        }

    def _save(self):
        """保存数据到文件"""
        atomic_write_json(self.data_file, self.data)

    def _check_new_day(self):
        """检查是否是新的一天，重置每日数据"""
        today = datetime.now().strftime("%Y-%m-%d")
        if self.data.get("last_study_date") != today:
            self.data["today_minutes"] = 0
            self.data["today_start"] = None
            self._update_streak()

    def _update_streak(self):
        """更新连续学习天数"""
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        last_date = self.data.get("last_study_date")

        if last_date == today:
            return
        elif last_date == yesterday:
            self.data["streak_days"] += 1
        elif last_date is None:
            self.data["streak_days"] = 1
        else:
            self.data["streak_days"] = 1

        self.data["last_study_date"] = today

    def start_session(self, subject: str = "学习") -> bool:
        """
        开始一个学习时段

        返回 True 表示开始成功，False 表示已经在学习中
        """
        if self.is_studying():
            return False

        self._check_new_day()
        self.data["today_start"] = datetime.now().isoformat()
        self.data["last_active_time"] = datetime.now().isoformat()
        self._save()
        return True

    def end_session(self, subject: str = "学习") -> float:
        """
        结束一个学习时段

        返回学习时长（分钟）
        """
        if not self.is_studying():
            return 0

        start_time = datetime.fromisoformat(self.data["today_start"])
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() / 60

        if duration >= 1:
            session = {
                "start": self.data["today_start"],
                "end": end_time.isoformat(),
                "duration": duration,
                "subject": subject,
                "date": datetime.now().strftime("%Y-%m-%d")
            }
            self.data["sessions"].insert(0, session)
            self.data["today_minutes"] += duration
            self._update_streak()

        self.data["today_start"] = None
        self.data["last_study_date"] = datetime.now().strftime("%Y-%m-%d")
        self.data["last_active_time"] = datetime.now().isoformat()
        self._save()
        return duration

    def is_studying(self) -> bool:
        """检查是否正在学习中"""
        return self.data.get("today_start") is not None

    def get_today_hours(self) -> float:
        """获取今日学习小时数"""
        self._check_new_day()
        return self.data.get("today_minutes", 0) / 60

    def get_today_minutes(self) -> float:
        """获取今日学习分钟数"""
        self._check_new_day()
        return self.data.get("today_minutes", 0)

    def get_continuous_study_minutes(self) -> float:
        """获取当前连续学习时长（分钟）"""
        if not self.is_studying():
            return 0
        start_time = datetime.fromisoformat(self.data["today_start"])
        return (datetime.now() - start_time).total_seconds() / 60

    def get_hours_since_last_session(self) -> Optional[float]:
        """
        获取距离上次学习的小时数

        返回 None 表示从未学习过
        """
        last_active = self.data.get("last_active_time")
        if not last_active:
            return None
        last_time = datetime.fromisoformat(last_active)
        return (datetime.now() - last_time).total_seconds() / 3600

    def get_last_active_minutes(self) -> Optional[float]:
        """获取距离最后活跃的分钟数"""
        last_active = self.data.get("last_active_time")
        if not last_active:
            return None
        last_time = datetime.fromisoformat(last_active)
        return (datetime.now() - last_time).total_seconds() / 60

    def record_activity(self):
        """记录用户活动（用于更新最后活跃时间）"""
        self.data["last_active_time"] = datetime.now().isoformat()
        self._save()

    def get_streak_days(self) -> int:
        """获取连续学习天数"""
        return self.data.get("streak_days", 0)

    def get_yesterday_hours(self) -> float:
        """获取昨日学习小时数"""
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        sessions = self.data.get("sessions", [])
        total = sum(
            s.get("duration", 0) / 60
            for s in sessions
            if s.get("date") == yesterday
        )
        return total

    def get_yesterday_tasks(self) -> List[str]:
        """获取昨日学习的科目"""
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        sessions = self.data.get("sessions", [])
        subjects = set(
            s.get("subject", "学习")
            for s in sessions
            if s.get("date") == yesterday
        )
        return list(subjects)

    def get_week_hours(self) -> float:
        """获取本周学习小时数"""
        now = datetime.now()
        week_start = now - timedelta(days=now.weekday())
        week_start_str = week_start.strftime("%Y-%m-%d")
        sessions = self.data.get("sessions", [])
        total = sum(
            s.get("duration", 0) / 60
            for s in sessions
            if s.get("date", "") >= week_start_str
        )
        return total

    def get_recent_sessions(self, days: int = 7) -> List[Dict[str, Any]]:
        """获取最近N天的学习记录"""
        sessions = self.data.get("sessions", [])
        cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        return [s for s in sessions if s.get("date", "") >= cutoff]

    def get_daily_goal_progress(self, daily_goal_minutes: int) -> Dict[str, Any]:
        """获取每日目标进度"""
        today_minutes = self.get_today_minutes()
        progress = min(100, (today_minutes / daily_goal_minutes) * 100)
        reached = today_minutes >= daily_goal_minutes

        return {
            "today_minutes": today_minutes,
            "goal_minutes": daily_goal_minutes,
            "progress": progress,
            "reached": reached,
            "remaining": max(0, daily_goal_minutes - today_minutes)
        }

    def get_today_sessions(self) -> List[Dict[str, Any]]:
        """获取今日学习时段"""
        today = datetime.now().strftime("%Y-%m-%d")
        sessions = self.data.get("sessions", [])
        return [s for s in sessions if s.get("date") == today]

    def get_stats(self) -> Dict[str, Any]:
        """获取学习统计"""
        sessions = self.data.get("sessions", [])

        total_minutes = sum(s.get("duration", 0) for s in sessions)
        total_sessions = len(sessions)

        return {
            "today_minutes": self.get_today_minutes(),
            "today_hours": self.get_today_hours(),
            "streak_days": self.get_streak_days(),
            "total_minutes": total_minutes,
            "total_hours": total_minutes / 60,
            "total_sessions": total_sessions,
            "week_hours": self.get_week_hours(),
            "is_studying": self.is_studying()
        }

    def reset(self):
        """重置数据"""
        self.data = self._default_data()
        self._save()


# 全局单例
_tracker_instance: Optional[StudyTracker] = None


def get_study_tracker() -> StudyTracker:
    """获取学习追踪器实例"""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = StudyTracker()
    return _tracker_instance
