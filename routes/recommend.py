"""
StudyPal 每日任务推荐路由
"""

from flask import Blueprint, jsonify
from src.modules.daily_recommender import get_daily_recommender

recommend_bp = Blueprint('recommend', __name__, url_prefix='/api/recommend')


def _init_recommender():
    """初始化推荐器并连接模块"""
    recommender = get_daily_recommender()

    try:
        from src.study.study_tracker import get_study_tracker
        from src.modules.plan_generator import get_plan_generator
        from src.modules.task_manager import get_task_manager

        recommender.set_modules(
            study_tracker=get_study_tracker(),
            plan_generator=get_plan_generator(),
            task_manager=get_task_manager()
        )
    except Exception:
        pass

    return recommender


@recommend_bp.route('/daily', methods=['GET'])
def get_daily_recommendations():
    """获取每日任务推荐"""
    recommender = _init_recommender()
    recommendations = recommender.get_daily_recommendations()

    return jsonify({
        'success': True,
        **recommendations
    })


@recommend_bp.route('/tasks', methods=['GET'])
def get_task_recommendations():
    """获取任务推荐（简化版）"""
    recommender = _init_recommender()
    data = recommender.get_daily_recommendations()

    tasks = data.get('recommendations', [])

    return jsonify({
        'success': True,
        'tasks': tasks
    })
