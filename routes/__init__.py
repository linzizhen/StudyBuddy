"""
StudyPal 路由模块
使用 Blueprint 架构组织路由
"""

from flask import Blueprint

from .buddy import buddy_bp
from .diary import diary_bp
from .study import study_bp
from .tasks import tasks_bp
from .achievements import achievements_bp
from .plans import plans_bp
from .user import user_bp
from .timeline import timeline_bp
from .recommend import recommend_bp
from .insights import insights_bp
from .settings import settings_bp
from .ai_model import ai_model_bp
from .conversations import conversations_bp


def register_blueprints(app):
    """注册所有 Blueprint"""
    app.register_blueprint(buddy_bp)
    app.register_blueprint(conversations_bp)
    app.register_blueprint(diary_bp)
    app.register_blueprint(study_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(achievements_bp)
    app.register_blueprint(plans_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(timeline_bp)
    app.register_blueprint(recommend_bp)
    app.register_blueprint(insights_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(ai_model_bp)
