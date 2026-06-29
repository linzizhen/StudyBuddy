"""
StudyPal 路由模块
轻量版 - 不依赖 flask-sqlalchemy

作者：StudyPal
日期：2026-04-27
"""

from flask import Blueprint


def register_blueprints(app):
    """注册所有 Blueprint"""
    try:
        from routes.buddy import buddy_bp
        app.register_blueprint(buddy_bp)
    except Exception as e:
        print(f"buddy 路由注册失败: {e}")

    try:
        from routes.diary import diary_bp
        app.register_blueprint(diary_bp)
    except Exception as e:
        print(f"diary 路由注册失败: {e}")

    try:
        from routes.study import study_bp
        app.register_blueprint(study_bp)
    except Exception as e:
        print(f"study 路由注册失败: {e}")

    try:
        from routes.tasks import tasks_bp
        app.register_blueprint(tasks_bp)
    except Exception as e:
        print(f"tasks 路由注册失败: {e}")

    try:
        from routes.achievements import achievements_bp
        app.register_blueprint(achievements_bp)
    except Exception as e:
        print(f"achievements 路由注册失败: {e}")

    try:
        from routes.plans import plans_bp
        app.register_blueprint(plans_bp)
    except Exception as e:
        print(f"plans 路由注册失败: {e}")

    try:
        from routes.timeline import timeline_bp
        app.register_blueprint(timeline_bp)
    except Exception as e:
        print(f"timeline 路由注册失败: {e}")

    try:
        from routes.recommend import recommend_bp
        app.register_blueprint(recommend_bp)
    except Exception as e:
        print(f"recommend 路由注册失败: {e}")

    try:
        from routes.insights import insights_bp
        app.register_blueprint(insights_bp)
    except Exception as e:
        print(f"insights 路由注册失败: {e}")

    try:
        from routes.user import user_bp
        app.register_blueprint(user_bp)
    except Exception as e:
        print(f"user 路由注册失败: {e}")

    try:
        from routes.home import home_bp
        app.register_blueprint(home_bp)
    except Exception as e:
        print(f"home 路由注册失败: {e}")

    try:
        from routes.challenges import challenges_bp
        app.register_blueprint(challenges_bp)
    except Exception as e:
        print(f"challenges 路由注册失败: {e}")
