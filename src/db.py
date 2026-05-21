"""
StudyPal 数据库初始化和管理脚本

用法：
python -m src.db init          # 初始化数据库
python -m src.db reset        # 重置数据库
python -m src.db seed         # 填充测试数据
python -m src.db admin EMAIL  # 创建管理员账户

作者：StudyPal
日期：2026-05-21
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from flask import Flask
from src.models.models import db, User, Achievement, init_db, StudySession, Diary, Task, BuddyMemory


def create_app():
    """创建Flask应用实例"""
    app = Flask(__name__)

    # 配置
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        'sqlite:///studypal.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 初始化数据库
    init_db(app)

    return app


def init_database():
    """初始化数据库表"""
    app = create_app()
    with app.app_context():
        db.create_all()
        print("数据库表创建成功！")


def reset_database():
    """重置数据库"""
    app = create_app()
    with app.app_context():
        confirm = input("确定要重置所有数据吗？此操作不可恢复！(yes/no): ")
        if confirm.lower() == 'yes':
            db.drop_all()
            db.create_all()
            print("数据库已重置！")
        else:
            print("取消操作")


def seed_data():
    """填充测试数据"""
    app = create_app()
    with app.app_context():
        # 检查是否已有用户
        if User.query.first():
            print("数据库已有数据，跳过填充")
            return

        # 创建测试用户
        test_user = User(
            email='demo@studypal.com',
            nickname='考研战士',
            target_school='清华大学',
            target_major='计算机科学与技术',
            target_score=380,
            exam_date=datetime.now().date() + timedelta(days=180),
            daily_goal_hours=8.0,
            current_role_id='xiaodou',
            total_study_hours=52.5,
            total_sessions=23,
            current_streak=7,
            longest_streak=14,
        )
        test_user.set_password('demo123')
        db.session.add(test_user)

        # 创建学习会话记录
        today = datetime.now().date()
        for i in range(7):
            session = StudySession(
                user_id=test_user.id,
                subject=['数学', '英语', '政治', '专业课'][i % 4],
                duration_minutes=(25 + i * 5) * 60 // 60,
                start_time=datetime.now() - timedelta(days=i, hours=10),
                end_time=datetime.now() - timedelta(days=i, hours=8),
                date=today - timedelta(days=i),
                status='completed',
                pomodoro_count=3 + i % 3
            )
            db.session.add(session)

        # 创建日记
        emotions = ['很好', '还好', '一般', '不太好']
        for i in range(7):
            diary = Diary(
                user_id=test_user.id,
                date=today - timedelta(days=i),
                emotion_level=3 + (i % 2),
                emotion_label=emotions[i % 4],
                study_feeling=['充实', '疲惫', '焦虑'][i % 3],
                biggest_event=f'第{i+1}天学习总结',
                words_to_buddy='今天加油！',
                study_hours=6.0 + i * 0.5
            )
            db.session.add(diary)

        # 创建任务
        tasks_data = [
            ('完成高数第三章习题', '数学', 'high'),
            ('背单词50个', '英语', 'medium'),
            ('整理政治笔记', '政治', 'low'),
            ('刷408真题', '专业课', 'high'),
            ('复习线代公式', '数学', 'medium'),
        ]
        for title, subject, priority in tasks_data:
            task = Task(
                user_id=test_user.id,
                title=title,
                subject=subject,
                priority=priority,
                status='pending' if i > 2 else 'completed',
                due_date=today + timedelta(days=7)
            )
            db.session.add(task)

        # 创建搭子记忆
        memories_data = [
            ('用户提到数学是他的薄弱科目', 'preference', '数学确实有点难', ['数学', '薄弱']),
            ('用户说最近睡眠不好', 'event', '可能是因为压力大', ['睡眠', '压力']),
            ('用户的考研目标是清华计算机', 'topic', '非常有挑战性', ['目标', '清华']),
            ('用户喜欢用番茄工作法', 'preference', '25分钟专注模式', ['方法', '番茄']),
        ]
        for summary, mtype, details, tags in memories_data:
            memory = BuddyMemory(
                user_id=test_user.id,
                memory_type=mtype,
                summary=summary,
                details=details,
                tags=tags,
                importance=3
            )
            db.session.add(memory)

        db.session.commit()
        print(f"测试数据填充完成！")
        print(f"登录邮箱: demo@studypal.com")
        print(f"登录密码: demo123")


def create_admin(email: str):
    """创建管理员账户"""
    if not email:
        print("请提供管理员邮箱: python -m src.db admin EMAIL")
        return

    app = create_app()
    with app.app_context():
        # 检查是否已存在
        existing = User.query.filter_by(email=email.lower()).first()
        if existing:
            existing.is_admin = True
            db.session.commit()
            print(f"{email} 已设为管理员")
            return

        # 创建新管理员
        admin = User(
            email=email.lower(),
            nickname='管理员',
            is_admin=True,
            subscription_tier='vip',
            subscription_expires=datetime.now() + timedelta(days=3650)
        )
        admin.set_password('admin123')  # 临时密码
        db.session.add(admin)
        db.session.commit()

        print(f"管理员账户创建成功！")
        print(f"登录邮箱: {email}")
        print(f"登录密码: admin123")
        print("请立即修改密码！")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        print("可用命令:")
        print("  init    - 初始化数据库")
        print("  reset   - 重置数据库")
        print("  seed   - 填充测试数据")
        print("  admin  - 创建管理员账户")
    else:
        command = sys.argv[1]
        if command == 'init':
            init_database()
        elif command == 'reset':
            reset_database()
        elif command == 'seed':
            seed_data()
        elif command == 'admin':
            email = sys.argv[2] if len(sys.argv) > 2 else input("管理员邮箱: ")
            create_admin(email)
        else:
            print(f"未知命令: {command}")
