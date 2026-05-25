"""
StudyPal 认证路由（轻量版）

作者：StudyPal
日期：2026-05-21
"""

from flask import Blueprint, jsonify, request, g
from src.auth.auth import AuthService, get_current_user, auth_required

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def _user_to_dict(user):
    """用户转字典（移除敏感字段）"""
    if not user:
        return None
    return {
        'id': user.get('id'),
        'email': user.get('email'),
        'nickname': user.get('nickname'),
        'avatar': user.get('avatar'),
        'subscription_tier': user.get('subscription_tier'),
        'is_pro': user.get('subscription_tier') in ['pro', 'vip'],
        'is_vip': user.get('subscription_tier') == 'vip',
        'target_school': user.get('target_school'),
        'target_major': user.get('target_major'),
        'target_score': user.get('target_score'),
        'exam_date': user.get('exam_date'),
        'daily_goal_hours': user.get('daily_goal_hours'),
        'current_role_id': user.get('current_role_id'),
        'custom_buddy_name': user.get('custom_buddy_name'),
        'theme': user.get('theme'),
        'total_study_hours': user.get('total_study_hours'),
        'total_sessions': user.get('total_sessions'),
        'current_streak': user.get('current_streak'),
        'longest_streak': user.get('longest_streak'),
        'created_at': user.get('created_at'),
    }


@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.json or {}
    email = data.get('email', '').strip()
    password = data.get('password', '')
    nickname = data.get('nickname', '').strip()

    if not email or not password:
        return jsonify({'success': False, 'error': '邮箱和密码不能为空'}), 400

    success, message, user = AuthService.register(email, password, nickname)

    if success:
        return jsonify({
            'success': True,
            'message': message,
            'token': user['token'],
            'user': _user_to_dict(user)
        }), 201

    return jsonify({'success': False, 'error': message}), 400


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.json or {}
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'success': False, 'error': '邮箱和密码不能为空'}), 400

    success, message, user, token = AuthService.login(email, password)

    if success:
        return jsonify({
            'success': True,
            'message': message,
            'token': token,
            'user': _user_to_dict(user)
        })

    return jsonify({'success': False, 'error': message}), 401


@auth_required
@auth_bp.route('/me', methods=['GET'])
def get_me():
    """获取当前用户信息"""
    user = get_current_user()
    return jsonify({
        'success': True,
        'user': _user_to_dict(user)
    })


@auth_required
@auth_bp.route('/me', methods=['PUT', 'PATCH'])
def update_me():
    """更新用户信息"""
    user = get_current_user()
    data = request.json or {}

    updateable = [
        'nickname', 'avatar', 'theme', 'target_school', 'target_major',
        'target_score', 'exam_date', 'daily_goal_hours', 'current_role_id',
        'custom_buddy_name'
    ]
    updates = {}
    for field in updateable:
        if field in data:
            updates[field] = data[field]

    if updates:
        AuthService.update_user(user['id'], updates)
        user = AuthService.get_user_by_id(user['id'])

    return jsonify({
        'success': True,
        'message': '用户信息已更新',
        'user': _user_to_dict(user)
    })


@auth_required
@auth_bp.route('/subscription', methods=['GET'])
def get_subscription():
    """获取订阅信息"""
    user = get_current_user()
    tier = user.get('subscription_tier', 'free')
    limits = {'free': 100, 'pro': 1000, 'vip': 10000}

    return jsonify({
        'success': True,
        'subscription': {
            'tier': tier,
            'is_pro': tier in ['pro', 'vip'],
            'is_vip': tier == 'vip',
            'is_active': True,
            'expires': user.get('subscription_expires'),
            'ai_calls_used': user.get('ai_api_calls', 0),
            'ai_calls_limit': limits.get(tier, 100),
        }
    })


@auth_required
@auth_bp.route('/ai/stats', methods=['GET'])
def get_ai_stats():
    """获取AI使用统计"""
    user = get_current_user()
    tier = user.get('subscription_tier', 'free')
    limits = {'free': 100, 'pro': 1000, 'vip': 10000}
    used = user.get('ai_api_calls', 0)
    limit = limits.get(tier, 100)

    return jsonify({
        'success': True,
        'stats': {
            'calls_used': used,
            'calls_limit': limit,
            'calls_remaining': max(0, limit - used),
            'tier': tier,
        }
    })


# ==================== 管理员接口 ====================

@auth_required
@auth_bp.route('/admin/users', methods=['GET'])
def admin_list_users():
    """管理员：获取用户列表"""
    user = get_current_user()
    if not user.get('is_admin'):
        return jsonify({'success': False, 'error': '需要管理员权限'}), 403

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '').lower()

    all_users = AuthService.get_all_users()
    users_list = list(all_users.values())

    if search:
        users_list = [u for u in users_list if search in u.get('email', '').lower() or search in u.get('nickname', '').lower()]

    users_list.sort(key=lambda x: x.get('created_at', ''), reverse=True)

    start = (page - 1) * per_page
    end = start + per_page
    page_users = users_list[start:end]

    return jsonify({
        'success': True,
        'users': [_user_to_dict(u) for u in page_users],
        'total': len(users_list),
        'pages': (len(users_list) + per_page - 1) // per_page,
        'current_page': page
    })


@auth_required
@auth_bp.route('/admin/stats', methods=['GET'])
def admin_get_stats():
    """管理员：获取系统统计"""
    user = get_current_user()
    if not user.get('is_admin'):
        return jsonify({'success': False, 'error': '需要管理员权限'}), 403

    from datetime import datetime, timedelta
    all_users = AuthService.get_all_users()
    now = datetime.now()

    tier_counts = {'free': 0, 'pro': 0, 'vip': 0}
    for u in all_users.values():
        tier = u.get('subscription_tier', 'free')
        tier_counts[tier] = tier_counts.get(tier, 0) + 1

    active_threshold = (now - timedelta(days=1)).isoformat()
    active_count = sum(1 for u in all_users.values() if u.get('last_active', '') > active_threshold)

    return jsonify({
        'success': True,
        'stats': {
            'total_users': len(all_users),
            'active_users_today': active_count,
            'subscription_breakdown': tier_counts,
        }
    })
