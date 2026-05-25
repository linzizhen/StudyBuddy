"""
StudyPal 数据模型定义
使用 dataclass 替代 SQLAlchemy，兼容现有 JSON 存储

作者：StudyPal
日期：2026-05-21
重构：2026-05-25（dataclass 重构）
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, date
from typing import Optional, List, Dict, Any


# ==================== 工具函数 ====================

def to_dict(obj) -> Dict:
    """将 dataclass 转换为字典"""
    if obj is None:
        return None
    if hasattr(obj, 'to_dict'):
        return obj.to_dict()
    if hasattr(obj, '__dataclass_fields__'):
        result = {}
        for name, f in obj.__dataclass_fields__.items():
            value = getattr(obj, name)
            if isinstance(value, datetime):
                result[name] = value.isoformat()
            elif isinstance(value, date):
                result[name] = value.isoformat()
            elif value is not None:
                result[name] = value
        return result
    return obj


# ==================== 用户模型 ====================

@dataclass
class User:
    """用户模型"""
    id: int
    email: str
    password_hash: str
    nickname: str

    subscription_tier: str = 'free'
    subscription_expires: Optional[datetime] = None
    ai_api_calls: int = 0
    ai_api_reset_date: Optional[date] = None

    avatar: str = '🌸'
    theme: str = 'light'

    ai_model_key: Optional[str] = None
    ai_custom_config: Optional[Dict] = None

    current_role_id: str = 'xiaodou'
    custom_buddy_name: Optional[str] = None

    target_school: Optional[str] = None
    target_major: Optional[str] = None
    target_score: int = 0
    exam_date: Optional[date] = None
    daily_goal_hours: float = 8.0

    total_study_hours: float = 0
    total_sessions: int = 0
    current_streak: int = 0
    longest_streak: int = 0

    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_active: Optional[datetime] = None
    is_active: bool = True
    is_admin: bool = False

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'email': self.email,
            'nickname': self.nickname,
            'avatar': self.avatar,
            'subscription_tier': self.subscription_tier,
            'is_pro': self.subscription_tier in ['pro', 'vip'],
            'is_vip': self.subscription_tier == 'vip',
            'target_school': self.target_school,
            'target_major': self.target_major,
            'target_score': self.target_score,
            'exam_date': self.exam_date.isoformat() if self.exam_date else None,
            'daily_goal_hours': self.daily_goal_hours,
            'current_role_id': self.current_role_id,
            'custom_buddy_name': self.custom_buddy_name,
            'theme': self.theme,
            'total_study_hours': self.total_study_hours,
            'total_sessions': self.total_sessions,
            'current_streak': self.current_streak,
            'longest_streak': self.longest_streak,
            'ai_model_key': self.ai_model_key,
            'ai_custom_config': self.ai_custom_config,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ==================== 学习会话 ====================

@dataclass
class StudySession:
    """学习时段"""
    id: int
    user_id: int
    subject: str
    start_time: datetime
    date: date

    duration_minutes: int = 0
    end_time: Optional[datetime] = None
    status: str = 'active'
    pomodoro_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'subject': self.subject,
            'duration_minutes': self.duration_minutes,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'date': self.date.isoformat() if self.date else None,
            'status': self.status,
            'pomodoro_count': self.pomodoro_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ==================== 日记 ====================

@dataclass
class DiaryEntry:
    """日记条目"""
    id: int
    user_id: int
    date: date
    emotion_level: int

    emotion_label: Optional[str] = None
    study_feeling: Optional[str] = None
    biggest_event: Optional[str] = None
    words_to_buddy: Optional[str] = None
    study_hours: float = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat() if self.date else None,
            'emotion_level': self.emotion_level,
            'emotion_label': self.emotion_label,
            'study_feeling': self.study_feeling,
            'biggest_event': self.biggest_event,
            'words_to_buddy': self.words_to_buddy,
            'study_hours': self.study_hours,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ==================== 任务 ====================

@dataclass
class Task:
    """任务"""
    id: int
    user_id: int
    title: str

    subject: Optional[str] = None
    priority: str = 'medium'
    status: str = 'pending'
    due_date: Optional[date] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'subject': self.subject,
            'priority': self.priority,
            'status': self.status,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ==================== 搭子记忆 ====================

@dataclass
class BuddyMemory:
    """搭子记忆"""
    id: int
    user_id: int
    summary: str

    memory_type: str = 'scene'
    details: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    importance: int = 1
    recall_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'memory_type': self.memory_type,
            'summary': self.summary,
            'details': self.details,
            'tags': self.tags or [],
            'importance': self.importance,
            'recall_count': self.recall_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ==================== 对话 ====================

@dataclass
class Conversation:
    """对话记录"""
    id: int
    user_id: int
    conversation_id: str
    role: str
    content: str
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'conversation_id': self.conversation_id,
            'role': self.role,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ==================== 学习计划 ====================

@dataclass
class StudyPlan:
    """学习计划"""
    id: int
    user_id: int
    title: str

    subject: Optional[str] = None
    target_date: Optional[date] = None
    daily_hours: float = 8.0
    status: str = 'active'
    notes: Optional[str] = None
    progress: float = 0
    completed_hours: float = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'subject': self.subject,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'daily_hours': self.daily_hours,
            'status': self.status,
            'notes': self.notes,
            'progress': self.progress,
            'completed_hours': self.completed_hours,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ==================== 成就 ====================

@dataclass
class Achievement:
    """成就定义"""
    code: str
    name: str

    id: int = 0
    description: Optional[str] = None
    icon: str = '🏆'
    category: str = 'general'
    points: int = 10
    requirement: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'category': self.category,
            'points': self.points,
            'requirement': self.requirement,
        }


@dataclass
class UserAchievement:
    """用户成就"""
    id: int
    user_id: int
    achievement_id: int
    achievement: Achievement = None
    unlocked_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'achievement_id': self.achievement_id,
            'achievement': self.achievement.to_dict() if self.achievement else None,
            'unlocked_at': self.unlocked_at.isoformat() if self.unlocked_at else None,
        }


# ==================== 预设成就数据 ====================

DEFAULT_ACHIEVEMENTS = [
    Achievement(code='first_session', name='初出茅庐', description='完成第一个学习时段', icon='🌱', category='study', points=10),
    Achievement(code='streak_3', name='三天打鱼', description='连续学习3天', icon='🐟', category='streak', points=30),
    Achievement(code='streak_7', name='一周坚持', description='连续学习7天', icon='🔥', category='streak', points=70),
    Achievement(code='streak_30', name='月度达人', description='连续学习30天', icon='💎', category='streak', points=300),
    Achievement(code='hours_10', name='十小时战士', description='累计学习10小时', icon='⏰', category='study', points=20),
    Achievement(code='hours_100', name='百小时学霸', description='累计学习100小时', icon='📚', category='study', points=100),
    Achievement(code='hours_500', name='五百小时大师', description='累计学习500小时', icon='🏆', category='study', points=500),
    Achievement(code='first_diary', name='日记新手', description='写下第一篇日记', icon='📝', category='general', points=10),
    Achievement(code='diary_7', name='连续记录', description='连续7天写日记', icon='✍️', category='general', points=50),
    Achievement(code='task_master', name='任务达人', description='完成10个任务', icon='✅', category='general', points=50),
    Achievement(code='early_bird', name='早起鸟', description='早上6点前开始学习', icon='🐦', category='milestone', points=30),
    Achievement(code='night_owl', name='夜猫子', description='学习到凌晨12点后', icon='🦉', category='milestone', points=20),
    Achievement(code='all_subjects', name='全能选手', description='四大科目都学习过', icon='🎯', category='milestone', points=50),
]
