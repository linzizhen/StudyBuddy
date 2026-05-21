"""
StudyPal 数据库模型
使用 SQLAlchemy ORM

作者：StudyPal
日期：2026-05-21
"""

from datetime import datetime
from typing import Optional
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """用户表"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    nickname = db.Column(db.String(100), nullable=False)

    # 订阅信息
    subscription_tier = db.Column(db.String(20), default='free')  # free, pro, vip
    subscription_expires = db.Column(db.DateTime, nullable=True)
    ai_api_calls = db.Column(db.Integer, default=0)  # 本月API调用次数
    ai_api_reset_date = db.Column(db.Date, nullable=True)

    # 用户设置
    avatar = db.Column(db.String(50), default='🌸')
    theme = db.Column(db.String(20), default='light')

    # 搭子设置
    current_role_id = db.Column(db.String(20), default='xiaodou')
    custom_buddy_name = db.Column(db.String(50), nullable=True)

    # 学习目标
    target_school = db.Column(db.String(200), nullable=True)
    target_major = db.Column(db.String(200), nullable=True)
    target_score = db.Column(db.Integer, default=0)
    exam_date = db.Column(db.Date, nullable=True)
    daily_goal_hours = db.Column(db.Float, default=8.0)

    # 统计
    total_study_hours = db.Column(db.Float, default=0)
    total_sessions = db.Column(db.Integer, default=0)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)

    # 关系
    study_sessions = db.relationship('StudySession', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    diaries = db.relationship('Diary', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    tasks = db.relationship('Task', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    buddy_memories = db.relationship('BuddyMemory', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    achievements = db.relationship('UserAchievement', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    conversations = db.relationship('Conversation', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    plans = db.relationship('StudyPlan', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password: str):
        """设置密码（哈希）"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    def is_pro(self) -> bool:
        """是否为Pro会员"""
        return self.subscription_tier in ['pro', 'vip']

    def is_vip(self) -> bool:
        """是否为VIP会员"""
        return self.subscription_tier == 'vip'

    def is_subscription_active(self) -> bool:
        """订阅是否有效"""
        if self.subscription_tier == 'free':
            return True
        if not self.subscription_expires:
            return False
        return self.subscription_expires > datetime.utcnow()

    def get_ai_limit(self) -> int:
        """获取本月AI调用限制"""
        limits = {
            'free': 100,
            'pro': 1000,
            'vip': 10000
        }
        return limits.get(self.subscription_tier, 100)

    def can_use_ai(self) -> bool:
        """是否可以调用AI"""
        if not self.is_subscription_active():
            return False
        return self.ai_api_calls < self.get_ai_limit()

    def increment_ai_calls(self):
        """增加AI调用次数"""
        self.ai_api_calls += 1
        db.session.commit()

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'email': self.email,
            'nickname': self.nickname,
            'avatar': self.avatar,
            'subscription_tier': self.subscription_tier,
            'is_pro': self.is_pro(),
            'is_vip': self.is_vip(),
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
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class StudySession(db.Model):
    """学习时段表"""
    __tablename__ = 'study_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    subject = db.Column(db.String(50), nullable=False)  # 数学、英语、政治、专业课
    duration_minutes = db.Column(db.Integer, default=0)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    date = db.Column(db.Date, nullable=False, index=True)  # 用于按日期查询

    status = db.Column(db.String(20), default='active')  # active, completed, cancelled
    pomodoro_count = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'subject': self.subject,
            'duration_minutes': self.duration_minutes,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'date': self.date.isoformat() if self.date else None,
            'status': self.status,
            'pomodoro_count': self.pomodoro_count,
        }


class Diary(db.Model):
    """日记表"""
    __tablename__ = 'diaries'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    date = db.Column(db.Date, nullable=False, unique=True, index=True)
    emotion_level = db.Column(db.Integer, nullable=False)  # 1-5
    emotion_label = db.Column(db.String(20), nullable=True)  # 很好、还好、一般、不太好、很差
    study_feeling = db.Column(db.String(100), nullable=True)  # 充实、疲惫、焦虑等
    biggest_event = db.Column(db.Text, nullable=True)
    words_to_buddy = db.Column(db.Text, nullable=True)
    study_hours = db.Column(db.Float, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'emotion_level': self.emotion_level,
            'emotion_label': self.emotion_label,
            'study_feeling': self.study_feeling,
            'biggest_event': self.biggest_event,
            'words_to_buddy': self.words_to_buddy,
            'study_hours': self.study_hours,
        }


class Task(db.Model):
    """任务表"""
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    title = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(50), nullable=True)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    status = db.Column(db.String(20), default='pending')  # pending, completed, cancelled

    due_date = db.Column(db.Date, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'subject': self.subject,
            'priority': self.priority,
            'status': self.status,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class BuddyMemory(db.Model):
    """搭子记忆表"""
    __tablename__ = 'buddy_memories'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    memory_type = db.Column(db.String(50), default='scene')  # scene, preference, event, topic
    summary = db.Column(db.String(500), nullable=False)
    details = db.Column(db.Text, nullable=True)
    tags = db.Column(db.JSON, default=list)  # JSON数组存储标签

    importance = db.Column(db.Integer, default=1)  # 1-5，影响记忆持久度
    recall_count = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'memory_type': self.memory_type,
            'summary': self.summary,
            'details': self.details,
            'tags': self.tags or [],
            'importance': self.importance,
            'recall_count': self.recall_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Conversation(db.Model):
    """AI对话表"""
    __tablename__ = 'conversations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    conversation_id = db.Column(db.String(100), nullable=False, index=True)  # 前端对话ID
    role = db.Column(db.String(20), nullable=False)  # user, assistant
    content = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'role': self.role,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class StudyPlan(db.Model):
    """学习计划表"""
    __tablename__ = 'study_plans'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    title = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(50), nullable=True)
    target_date = db.Column(db.Date, nullable=True)
    daily_hours = db.Column(db.Float, default=8.0)
    status = db.Column(db.String(20), default='active')  # active, completed, cancelled
    notes = db.Column(db.Text, nullable=True)

    progress = db.Column(db.Float, default=0)  # 0-100%
    completed_hours = db.Column(db.Float, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
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


class Achievement(db.Model):
    """成就定义表"""
    __tablename__ = 'achievements'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    icon = db.Column(db.String(50), default='🏆')
    category = db.Column(db.String(50), default='general')  # general, study, streak, milestone
    points = db.Column(db.Integer, default=10)
    requirement = db.Column(db.JSON, default=dict)  # 达成条件

    def to_dict(self) -> dict:
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


class UserAchievement(db.Model):
    """用户成就表"""
    __tablename__ = 'user_achievements'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)

    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow)

    achievement = db.relationship('Achievement', backref='user_achievements')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'achievement_id', name='unique_user_achievement'),
    )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'achievement': self.achievement.to_dict() if self.achievement else None,
            'unlocked_at': self.unlocked_at.isoformat() if self.unlocked_at else None,
        }


def init_db(app):
    """初始化数据库"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        _init_default_achievements()


def _init_default_achievements():
    """初始化默认成就"""
    default_achievements = [
        {'code': 'first_session', 'name': '初出茅庐', 'description': '完成第一个学习时段', 'icon': '🌱', 'category': 'study', 'points': 10},
        {'code': 'streak_3', 'name': '三天打鱼', 'description': '连续学习3天', 'icon': '🐟', 'category': 'streak', 'points': 30},
        {'code': 'streak_7', 'name': '一周坚持', 'description': '连续学习7天', 'icon': '🔥', 'category': 'streak', 'points': 70},
        {'code': 'streak_30', 'name': '月度达人', 'description': '连续学习30天', 'icon': '💎', 'category': 'streak', 'points': 300},
        {'code': 'hours_10', 'name': '十小时战士', 'description': '累计学习10小时', 'icon': '⏰', 'category': 'study', 'points': 20},
        {'code': 'hours_100', 'name': '百小时学霸', 'description': '累计学习100小时', 'icon': '📚', 'category': 'study', 'points': 100},
        {'code': 'hours_500', 'name': '五百小时大师', 'description': '累计学习500小时', 'icon': '🏆', 'category': 'study', 'points': 500},
        {'code': 'first_diary', 'name': '日记新手', 'description': '写下第一篇日记', 'icon': '📝', 'category': 'general', 'points': 10},
        {'code': 'diary_7', 'name': '连续记录', 'description': '连续7天写日记', 'icon': '✍️', 'category': 'general', 'points': 50},
        {'code': 'task_master', 'name': '任务达人', 'description': '完成10个任务', 'icon': '✅', 'category': 'general', 'points': 50},
        {'code': 'early_bird', 'name': '早起鸟', 'description': '早上6点前开始学习', 'icon': '🐦', 'category': 'milestone', 'points': 30},
        {'code': 'night_owl', 'name': '夜猫子', 'description': '学习到凌晨12点后', 'icon': '🦉', 'category': 'milestone', 'points': 20},
        {'code': 'all_subjects', 'name': '全能选手', 'description': '四大科目都学习过', 'icon': '🎯', 'category': 'milestone', 'points': 50},
    ]

    for ach_data in default_achievements:
        existing = Achievement.query.filter_by(code=ach_data['code']).first()
        if not existing:
            ach = Achievement(**ach_data)
            db.session.add(ach)

    db.session.commit()
