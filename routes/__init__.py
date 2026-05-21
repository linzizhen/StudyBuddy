"""
StudyPal 路由模块
使用 Blueprint 架构组织路由

作者：StudyPal
日期：2026-04-27
"""

from flask import Blueprint


def register_blueprints(app):
    """注册所有 Blueprint"""
    # 用户相关路由（已集成认证）
    from routes.buddy import buddy_bp
    from routes.diary import diary_bp
    from routes.study import study_bp
    from routes.tasks import tasks_bp
    from routes.achievements import achievements_bp
    from routes.plans import plans_bp
    from routes.timeline import timeline_bp
    from routes.recommend import recommend_bp
    from routes.insights import insights_bp
    from routes.user import user_bp

    app.register_blueprint(buddy_bp)
    app.register_blueprint(diary_bp)
    app.register_blueprint(study_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(achievements_bp)
    app.register_blueprint(plans_bp)
    app.register_blueprint(timeline_bp)
    app.register_blueprint(recommend_bp)
    app.register_blueprint(insights_bp)
    app.register_blueprint(user_bp)
