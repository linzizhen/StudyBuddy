"""
StudyPal 数据库服务层
统一的数据访问接口，支持 SQLite 数据库 + JSON 文件双存储

设计原则：
1. 新数据优先写入数据库
2. 旧 JSON 文件数据可迁移到数据库
3. 现有模块无需修改接口

作者：StudyPal
日期：2026-05-25
"""

import json
import os
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from flask import g, current_app
from src.models.models import db, User, StudySession, Diary, Task, BuddyMemory, Conversation, StudyPlan, Achievement, UserAchievement


class DatabaseService:
    """
    数据库服务 - 提供所有数据操作的统一接口

    使用方式：
        ds = DatabaseService()
        ds.save_study_session(user_id, subject, start_time, end_time, duration)
    """

    # ==================== 用户相关 ====================

    @staticmethod
    def get_user(user_id: int) -> Optional[Dict]:
        """获取用户信息"""
        user = User.query.get(user_id)
        return user.to_dict() if user else None

    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict]:
        """根据邮箱获取用户"""
        user = User.query.filter_by(email=email.lower()).first()
        return user.to_dict() if user else None

    @staticmethod
    def update_user(user_id: int, updates: Dict) -> Optional[Dict]:
        """更新用户信息"""
        user = User.query.get(user_id)
        if not user:
            return None

        for key, value in updates.items():
            if hasattr(user, key) and key not in ('id', 'email', 'password_hash'):
                setattr(user, key, value)

        db.session.commit()
        return user.to_dict()

    # ==================== 学习会话 ====================

    @staticmethod
    def save_study_session(
        user_id: int,
        subject: str,
        start_time: datetime,
        end_time: datetime = None,
        duration: float = 0,
        date_str: str = None,
        status: str = 'completed'
    ) -> Dict:
        """保存学习时段"""
        session = StudySession(
            user_id=user_id,
            subject=subject,
            start_time=start_time,
            end_time=end_time,
            duration_minutes=int(duration) if duration else 0,
            date=datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else start_time.date(),
            status=status
        )
        db.session.add(session)

        # 更新用户统计
        user = User.query.get(user_id)
        if user and end_time:
            user.total_study_hours += duration / 60
            user.total_sessions += 1

        db.session.commit()
        return session.to_dict()

    @staticmethod
    def get_study_sessions(user_id: int, limit: int = 100) -> List[Dict]:
        """获取学习时段列表"""
        sessions = StudySession.query.filter_by(user_id=user_id)\
            .order_by(StudySession.start_time.desc())\
            .limit(limit).all()
        return [s.to_dict() for s in sessions]

    @staticmethod
    def get_study_sessions_by_date(user_id: int, target_date: date) -> List[Dict]:
        """获取指定日期的学习时段"""
        sessions = StudySession.query.filter_by(
            user_id=user_id,
            date=target_date
        ).order_by(StudySession.start_time).all()
        return [s.to_dict() for s in sessions]

    @staticmethod
    def get_streak_days(user_id: int) -> int:
        """获取连续学习天数"""
        user = User.query.get(user_id)
        return user.current_streak if user else 0

    @staticmethod
    def update_streak(user_id: int, streak: int):
        """更新连续学习天数"""
        user = User.query.get(user_id)
        if user:
            user.current_streak = streak
            if streak > user.longest_streak:
                user.longest_streak = streak
            db.session.commit()

    # ==================== 日记 ====================

    @staticmethod
    def save_diary(
        user_id: int,
        emotion_level: int,
        emotion_label: str = None,
        study_feeling: str = None,
        biggest_event: str = None,
        words_to_buddy: str = None,
        study_hours: float = 0,
        date_str: str = None
    ) -> Dict:
        """保存日记"""
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()

        # 检查是否已存在该日期的日记
        existing = Diary.query.filter_by(user_id=user_id, date=target_date).first()

        if existing:
            existing.emotion_level = emotion_level
            existing.emotion_label = emotion_label
            existing.study_feeling = study_feeling
            existing.biggest_event = biggest_event
            existing.words_to_buddy = words_to_buddy
            existing.study_hours = study_hours
            db.session.commit()
            return existing.to_dict()

        diary = Diary(
            user_id=user_id,
            date=target_date,
            emotion_level=emotion_level,
            emotion_label=emotion_label,
            study_feeling=study_feeling,
            biggest_event=biggest_event,
            words_to_buddy=words_to_buddy,
            study_hours=study_hours
        )
        db.session.add(diary)
        db.session.commit()
        return diary.to_dict()

    @staticmethod
    def get_diary_entries(user_id: int, limit: int = 30) -> List[Dict]:
        """获取日记列表"""
        entries = Diary.query.filter_by(user_id=user_id)\
            .order_by(Diary.date.desc())\
            .limit(limit).all()
        return [e.to_dict() for e in entries]

    @staticmethod
    def get_today_diary(user_id: int) -> Optional[Dict]:
        """获取今日日记"""
        entry = Diary.query.filter_by(
            user_id=user_id,
            date=date.today()
        ).first()
        return entry.to_dict() if entry else None

    @staticmethod
    def get_emotion_curve(user_id: int, days: int = 7) -> List[Dict]:
        """获取情绪曲线"""
        from datetime import timedelta
        start_date = date.today() - timedelta(days=days)

        entries = Diary.query.filter(
            Diary.user_id == user_id,
            Diary.date >= start_date
        ).order_by(Diary.date).all()

        return [
            {
                'date': e.date.isoformat(),
                'level': e.emotion_level,
                'label': e.emotion_label or ''
            }
            for e in entries
        ]

    # ==================== 任务 ====================

    @staticmethod
    def save_task(
        user_id: int,
        title: str,
        description: str = None,
        subject: str = None,
        priority: str = 'medium',
        due_date: date = None
    ) -> Dict:
        """保存任务"""
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            subject=subject,
            priority=priority,
            due_date=due_date
        )
        db.session.add(task)
        db.session.commit()
        return task.to_dict()

    @staticmethod
    def get_tasks(user_id: int, status: str = 'all') -> List[Dict]:
        """获取任务列表"""
        query = Task.query.filter_by(user_id=user_id)
        if status == 'pending':
            query = query.filter_by(status='pending')
        elif status == 'completed':
            query = query.filter_by(status='completed')

        tasks = query.order_by(Task.created_at.desc()).all()
        return [t.to_dict() for t in tasks]

    @staticmethod
    def update_task(task_id: int, user_id: int, updates: Dict) -> Optional[Dict]:
        """更新任务"""
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()
        if not task:
            return None

        for key, value in updates.items():
            if hasattr(task, key):
                if key == 'completed' and value:
                    task.status = 'completed'
                    task.completed_at = datetime.utcnow()
                else:
                    setattr(task, key, value)

        db.session.commit()
        return task.to_dict()

    @staticmethod
    def delete_task(task_id: int, user_id: int) -> bool:
        """删除任务"""
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()
        if task:
            db.session.delete(task)
            db.session.commit()
            return True
        return False

    # ==================== 搭子记忆 ====================

    @staticmethod
    def save_buddy_memory(
        user_id: int,
        memory_type: str,
        summary: str,
        details: str = None,
        tags: List[str] = None
    ) -> Dict:
        """保存搭子记忆"""
        memory = BuddyMemory(
            user_id=user_id,
            memory_type=memory_type,
            summary=summary,
            details=details,
            tags=tags or []
        )
        db.session.add(memory)
        db.session.commit()
        return memory.to_dict()

    @staticmethod
    def get_buddy_memories(user_id: int, memory_type: str = None) -> List[Dict]:
        """获取搭子记忆"""
        query = BuddyMemory.query.filter_by(user_id=user_id)
        if memory_type:
            query = query.filter_by(memory_type=memory_type)

        memories = query.order_by(BuddyMemory.created_at.desc()).all()
        return [m.to_dict() for m in memories]

    # ==================== 对话历史 ====================

    @staticmethod
    def save_conversation(
        user_id: int,
        conversation_id: str,
        role: str,
        content: str
    ) -> Dict:
        """保存对话"""
        conv = Conversation(
            user_id=user_id,
            conversation_id=conversation_id,
            role=role,
            content=content
        )
        db.session.add(conv)
        db.session.commit()
        return conv.to_dict()

    @staticmethod
    def get_conversations(user_id: int, limit: int = 100) -> List[Dict]:
        """获取对话历史"""
        convs = Conversation.query.filter_by(user_id=user_id)\
            .order_by(Conversation.created_at.desc())\
            .limit(limit).all()
        return [c.to_dict() for c in convs]

    # ==================== 学习计划 ====================

    @staticmethod
    def save_plan(
        user_id: int,
        title: str,
        subject: str = None,
        target_date: date = None,
        daily_hours: float = 8.0,
        notes: str = None
    ) -> Dict:
        """保存学习计划"""
        plan = StudyPlan(
            user_id=user_id,
            title=title,
            subject=subject,
            target_date=target_date,
            daily_hours=daily_hours,
            notes=notes
        )
        db.session.add(plan)
        db.session.commit()
        return plan.to_dict()

    @staticmethod
    def get_plans(user_id: int, status: str = 'all') -> List[Dict]:
        """获取学习计划"""
        query = StudyPlan.query.filter_by(user_id=user_id)
        if status == 'active':
            query = query.filter_by(status='active')

        plans = query.order_by(StudyPlan.created_at.desc()).all()
        return [p.to_dict() for p in plans]

    # ==================== 成就 ====================

    @staticmethod
    def unlock_achievement(user_id: int, achievement_code: str) -> Optional[Dict]:
        """解锁成就"""
        achievement = Achievement.query.filter_by(code=achievement_code).first()
        if not achievement:
            return None

        existing = UserAchievement.query.filter_by(
            user_id=user_id,
            achievement_id=achievement.id
        ).first()

        if existing:
            return None

        ua = UserAchievement(user_id=user_id, achievement_id=achievement.id)
        db.session.add(ua)
        db.session.commit()
        return {
            'achievement': achievement.to_dict(),
            'unlocked_at': ua.unlocked_at.isoformat()
        }

    @staticmethod
    def get_user_achievements(user_id: int) -> Dict:
        """获取用户成就"""
        user_achs = UserAchievement.query.filter_by(user_id=user_id).all()
        all_achs = Achievement.query.all()

        unlocked_codes = {ua.achievement.code for ua in user_achs}
        total_points = sum(ua.achievement.points for ua in user_achs)

        return {
            'unlocked': [ua.to_dict() for ua in user_achs],
            'all': [a.to_dict() for a in all_achs],
            'unlocked_count': len(user_achs),
            'total_count': len(all_achs),
            'total_points': total_points
        }

    # ==================== 统计 ====================

    @staticmethod
    def get_user_stats(user_id: int) -> Dict:
        """获取用户统计"""
        user = User.query.get(user_id)
        if not user:
            return {}

        # 计算今日学习时长
        today_sessions = StudySession.query.filter_by(
            user_id=user_id,
            date=date.today()
        ).all()
        today_minutes = sum(s.duration_minutes for s in today_sessions)

        # 计算本周学习时长
        from datetime import timedelta
        week_start = date.today() - timedelta(days=date.today().weekday())
        week_sessions = StudySession.query.filter(
            StudySession.user_id == user_id,
            StudySession.date >= week_start
        ).all()
        week_minutes = sum(s.duration_minutes for s in week_sessions)

        # 今日是否已写日记
        has_diary = Diary.query.filter_by(
            user_id=user_id,
            date=date.today()
        ).first() is not None

        # 任务统计
        pending_tasks = Task.query.filter_by(user_id=user_id, status='pending').count()
        completed_tasks = Task.query.filter_by(user_id=user_id, status='completed').count()

        return {
            'total_study_hours': round(user.total_study_hours, 1),
            'total_sessions': user.total_sessions,
            'current_streak': user.current_streak,
            'longest_streak': user.longest_streak,
            'today_minutes': today_minutes,
            'today_hours': round(today_minutes / 60, 1),
            'week_minutes': week_minutes,
            'week_hours': round(week_minutes / 60, 1),
            'has_diary_today': has_diary,
            'pending_tasks': pending_tasks,
            'completed_tasks': completed_tasks,
            'target_school': user.target_school,
            'target_major': user.target_major,
            'target_score': user.target_score,
            'daily_goal_hours': user.daily_goal_hours,
        }


# 全局实例
_db_service = None


def get_db_service() -> DatabaseService:
    """获取数据库服务实例"""
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
    return _db_service
