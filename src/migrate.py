"""
StudyPal 数据迁移脚本
从 JSON 文件迁移数据到 SQLite 数据库

用法：
    python -m src.migrate

作者：StudyPal
日期：2026-05-25
"""

import sys
import os
import json
from datetime import datetime, date

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask


def create_app():
    """创建 Flask 应用"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'studypal.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    from src.models.models import db, init_db, _init_default_achievements
    db.init_app(app)

    return app, db


def load_json(filename):
    """加载 JSON 文件"""
    filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', filename)
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"  加载 {filename} 失败: {e}")
        return {}


def migrate_users(app, db):
    """迁移用户数据"""
    print("\n[1/7] 迁移用户数据...")

    from src.models.models import User

    with app.app_context():
        # 检查是否已有用户
        existing_count = User.query.count()
        if existing_count > 0:
            print(f"  数据库已有 {existing_count} 个用户，跳过用户迁移")
            return

        # 从 users.json 迁移
        users_data = load_json('users.json')
        if not users_data:
            # 从 user_settings.json 迁移
            settings = load_json('user_settings.json')
            if settings:
                user = User(
                    email='migrated@local',
                    nickname=settings.get('motto', '用户')[:50],
                    motto=settings.get('motto', ''),
                    theme=settings.get('theme', 'light'),
                    daily_goal=120
                )
                user.set_password('migrated123')
                db.session.add(user)
                db.session.commit()
                print(f"  从 user_settings.json 迁移了 1 个用户")
        else:
            for email, data in users_data.items():
                user = User(
                    email=email,
                    nickname=data.get('nickname', email.split('@')[0])[:50],
                    password_hash=data.get('password_hash', ''),
                    avatar=data.get('avatar', '🌸'),
                    theme=data.get('theme', 'light'),
                    subscription_tier=data.get('subscription_tier', 'free'),
                    current_role_id=data.get('current_role_id', 'xiaodou'),
                    custom_buddy_name=data.get('custom_buddy_name'),
                    target_school=data.get('target_school'),
                    target_major=data.get('target_major'),
                    target_score=data.get('target_score', 0),
                    daily_goal_hours=data.get('daily_goal_hours', 8.0),
                    total_study_hours=data.get('total_study_hours', 0),
                    total_sessions=data.get('total_sessions', 0),
                    current_streak=data.get('current_streak', 0),
                    longest_streak=data.get('longest_streak', 0),
                    ai_model_key=data.get('ai_model_key'),
                    ai_custom_config=data.get('ai_custom_config'),
                )
                # 手动设置密码哈希
                from werkzeug.security import generate_password_hash
                if not data.get('password_hash'):
                    user.password_hash = generate_password_hash('migrated123')
                db.session.add(user)

            db.session.commit()
            print(f"  迁移了 {len(users_data)} 个用户")


def migrate_study_sessions(app, db):
    """迁移学习时段数据"""
    print("\n[2/7] 迁移学习时段数据...")

    from src.models.models import StudySession

    with app.app_context():
        existing_count = StudySession.query.count()
        if existing_count > 0:
            print(f"  数据库已有 {existing_count} 条记录，跳过")
            return

        data = load_json('study_tracker.json')
        sessions = data.get('sessions', [])

        migrated = 0
        for s in sessions:
            try:
                session = StudySession(
                    subject=s.get('subject', '学习'),
                    duration_minutes=int(float(s.get('duration', 0))),
                    start_time=datetime.fromisoformat(s['start']),
                    end_time=datetime.fromisoformat(s['end']) if s.get('end') else None,
                    date=datetime.strptime(s['date'], '%Y-%m-%d').date(),
                    status='completed'
                )
                db.session.add(session)
                migrated += 1
            except Exception as e:
                print(f"  跳过无效记录: {e}")

        db.session.commit()
        print(f"  迁移了 {migrated} 条学习记录")


def migrate_diaries(app, db):
    """迁移日记数据"""
    print("\n[3/7] 迁移日记数据...")

    from src.models.models import Diary

    with app.app_context():
        existing_count = Diary.query.count()
        if existing_count > 0:
            print(f"  数据库已有 {existing_count} 条记录，跳过")
            return

        data = load_json('diary.json')
        entries = data.get('entries', [])

        migrated = 0
        for e in entries:
            try:
                diary = Diary(
                    date=datetime.strptime(e['date'], '%Y-%m-%d').date(),
                    emotion_level=e.get('emotion_level', 3),
                    emotion_label=e.get('emotion_label'),
                    study_feeling=e.get('study_feeling'),
                    biggest_event=e.get('biggest_event'),
                    words_to_buddy=e.get('words_to_buddy'),
                    study_hours=e.get('study_hours', 0)
                )
                db.session.add(diary)
                migrated += 1
            except Exception as e:
                print(f"  跳过无效记录: {e}")

        db.session.commit()
        print(f"  迁移了 {migrated} 条日记")


def migrate_tasks(app, db):
    """迁移任务数据"""
    print("\n[4/7] 迁移任务数据...")

    from src.models.models import Task

    with app.app_context():
        existing_count = Task.query.count()
        if existing_count > 0:
            print(f"  数据库已有 {existing_count} 条记录，跳过")
            return

        data = load_json('tasks.json')
        tasks = data.get('tasks', [])

        migrated = 0
        for t in tasks:
            try:
                task = Task(
                    title=t.get('title', ''),
                    subject=t.get('subject'),
                    priority=t.get('priority', 'medium'),
                    status=t.get('status', 'pending'),
                    due_date=datetime.strptime(t['due_date'], '%Y-%m-%d').date() if t.get('due_date') else None,
                )
                if t.get('completed_at'):
                    task.completed_at = datetime.fromisoformat(t['completed_at'])
                db.session.add(task)
                migrated += 1
            except Exception as e:
                print(f"  跳过无效记录: {e}")

        db.session.commit()
        print(f"  迁移了 {migrated} 条任务")


def migrate_buddy_memory(app, db):
    """迁移搭子记忆"""
    print("\n[5/7] 迁移搭子记忆...")

    from src.models.models import BuddyMemory

    with app.app_context():
        existing_count = BuddyMemory.query.count()
        if existing_count > 0:
            print(f"  数据库已有 {existing_count} 条记录，跳过")
            return

        data = load_json('buddy_memory.json')
        scenes = data.get('scenes', [])

        migrated = 0
        for s in scenes:
            try:
                memory = BuddyMemory(
                    memory_type=s.get('type', 'scene'),
                    summary=s.get('summary', ''),
                    details=s.get('details'),
                    tags=s.get('tags', [])
                )
                db.session.add(memory)
                migrated += 1
            except Exception as e:
                print(f"  跳过无效记录: {e}")

        db.session.commit()
        print(f"  迁移了 {migrated} 条记忆")


def migrate_conversations(app, db):
    """迁移对话历史"""
    print("\n[6/7] 迁移对话历史...")

    from src.models.models import Conversation

    with app.app_context():
        existing_count = Conversation.query.count()
        if existing_count > 0:
            print(f"  数据库已有 {existing_count} 条记录，跳过")
            return

        data = load_json('ai_history.json')
        messages = data.get('messages', [])

        migrated = 0
        for m in messages:
            try:
                conv = Conversation(
                    conversation_id=m.get('conversation_id', 'default'),
                    role=m.get('role', 'user'),
                    content=m.get('content', '')
                )
                db.session.add(conv)
                migrated += 1
            except Exception as e:
                print(f"  跳过无效记录: {e}")

        db.session.commit()
        print(f"  迁移了 {migrated} 条对话")


def migrate_timeline(app, db):
    """迁移时间线数据"""
    print("\n[7/7] 迁移时间线数据...")

    from src.models.models import StudyPlan

    with app.app_context():
        existing_count = StudyPlan.query.count()
        if existing_count > 0:
            print(f"  数据库已有 {existing_count} 条记录，跳过")
            return

        data = load_json('timeline.json')
        if not data:
            print("  没有时间线数据")
            return

        # 时间线数据可能需要根据实际格式调整
        print(f"  时间线数据需要手动迁移（格式待定）")


def main():
    """执行迁移"""
    print("=" * 50)
    print("StudyPal 数据迁移工具")
    print("=" * 50)

    app, db = create_app()

    # 创建数据库表
    print("\n[0/7] 创建数据库表...")
    with app.app_context():
        db.create_all()
        print("  数据库表创建完成")

    # 执行迁移
    migrate_users(app, db)
    migrate_study_sessions(app, db)
    migrate_diaries(app, db)
    migrate_tasks(app, db)
    migrate_buddy_memory(app, db)
    migrate_conversations(app, db)
    migrate_timeline(app, db)

    print("\n" + "=" * 50)
    print("迁移完成！")
    print("=" * 50)
    print("\n提示：")
    print("  1. JSON 文件已保留，原件在 data/ 目录")
    print("  2. 如果迁移有问题，可以删除 studypal.db 重新迁移")
    print("  3. 建议：迁移成功后备份 JSON 文件，然后可以删除")


if __name__ == '__main__':
    main()
