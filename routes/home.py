"""
StudyPal 首页路由

作者：StudyPal
日期：2026-05-21
"""

from flask import Blueprint, jsonify, g
from src.auth.auth import auth_required, auth_optional, get_current_user

home_bp = Blueprint('home', __name__, url_prefix='/api')


@home_bp.route('/home', methods=['GET'])
@auth_optional
def get_home_data():
    """获取首页数据"""
    user = get_current_user()

    # 构建基础数据
    data = {
        'buddy': {
            'name': user.get('current_role_id', '小豆') if user else '小豆',
            'emoji': '&#128150;',
            'emotion': 'happy',
            'emotion_desc': '心情不错~',
            'message': '今天想学点什么？',
        },
        'study': {
            'is_studying': False,
            'today_hours': user.get('total_study_hours', 0) if user else 0,
            'today_sessions': user.get('total_sessions', 0) if user else 0,
            'streak_days': user.get('current_streak', 0) if user else 0,
        },
        'profile': {
            'is_setup': bool(user.get('target_school')) if user else False,
            'user': {
                'name': user.get('nickname', '考研战士') if user else '游客',
                'target_school': user.get('target_school'),
                'target_major': user.get('target_major'),
                'target_score': user.get('target_score'),
            }
        },
        'diary': {
            'has_today': False,
        },
        'tasks': {
            'total': 0,
            'completed': 0,
        },
        'achievements': {
            'unlocked': 0,
            'total': 13,
        }
    }

    return jsonify({
        'success': True,
        'data': data
    })


@home_bp.route('/buddy/roles', methods=['GET'])
def get_buddy_roles():
    """获取所有搭子角色"""
    roles = [
        {
            'id': 'xiaodou',
            'name': '小豆',
            'emoji': '&#128150;',
            'tagline': '温柔闺蜜，暖暖陪伴',
            'color': '#5BBFAA',
        },
        {
            'id': 'aran',
            'name': '阿燃',
            'emoji': '&#128293;',
            'tagline': '热血兄弟，干就完了',
            'color': '#FF8C69',
        },
        {
            'id': 'senior',
            'name': '学姐',
            'emoji': '&#127891;',
            'tagline': '过来人，传授经验',
            'color': '#6BAED6',
        },
        {
            'id': 'xiaoye',
            'name': '小夜',
            'emoji': '&#127770;',
            'tagline': '深夜电台，温柔治愈',
            'color': '#B39BC8',
        },
        {
            'id': 'xj',
            'name': '戏精',
            'emoji': '&#127874;',
            'tagline': '段子手，欢乐陪学',
            'color': '#FFD166',
        },
        {
            'id': 'teacher',
            'name': '督学',
            'emoji': '&#128218;',
            'tagline': '严格监督，专注效率',
            'color': '#4ECDC4',
        },
    ]
    return jsonify({'success': True, 'roles': roles})
