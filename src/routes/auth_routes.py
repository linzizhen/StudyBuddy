"""
StudyPal 认证路由
处理注册、登录、用户信息等 API

作者：StudyPal
日期：2026-05-21
"""

from flask import Blueprint, jsonify, request, g
from src.auth.auth import (
    AuthService, get_current_user, auth_required, subscription_required, ai_limit_required
)
from src.models.models import db, User

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


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
        token = AuthService.generate_token(user.id)
        return jsonify({
            'success': True,
            'message': message,
            'token': token,
            'user': user.to_dict()
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
            'user': user.to_dict()
        })

    return jsonify({'success': False, 'error': message}), 401


@auth_bp.route('/me', methods=['GET'])
@auth_required
def get_me():
    """获取当前用户信息"""
    user = get_current_user()
    return jsonify({
        'success': True,
        'user': user.to_dict()
    })


@auth_bp.route('/me', methods=['PUT', 'PATCH'])
@auth_required
def update_me():
    """更新用户信息"""
    user = get_current_user()
    data = request.json or {}

    # 可更新的字段
    updateable_fields = [
        'nickname', 'avatar', 'theme', 'target_school', 'target_major',
        'target_score', 'exam_date', 'daily_goal_hours', 'current_role_id',
        'custom_buddy_name'
    ]

    for field in updateable_fields:
        if field in data:
            if field == 'target_score':
                setattr(user, field, int(data[field]) if data[field] else 0)
            elif field == 'daily_goal_hours':
                setattr(user, field, float(data[field]) if data[field] else 8.0)
            elif field == 'exam_date':
                if data[field]:
                    from datetime import datetime as dt
                    setattr(user, field, dt.strptime(data[field], '%Y-%m-%d').date())
                else:
                    setattr(user, field, None)
            else:
                setattr(user, field, data[field])

    db.session.commit()

    return jsonify({
        'success': True,
        'message': '用户信息已更新',
        'user': user.to_dict()
    })


@auth_bp.route('/password', methods=['PUT', 'PATCH'])
@auth_required
def change_password():
    """修改密码"""
    data = request.json or {}
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')

    if not old_password or not new_password:
        return jsonify({'success': False, 'error': '请填写完整信息'}), 400

    success, message = AuthService.change_password(
        get_current_user().id, old_password, new_password
    )

    if success:
        return jsonify({'success': True, 'message': message})

    return jsonify({'success': False, 'error': message}), 400


@auth_bp.route('/password/reset', methods=['POST'])
def request_password_reset():
    """请求密码重置"""
    data = request.json or {}
    email = data.get('email', '').strip()

    if not email:
        return jsonify({'success': False, 'error': '请输入邮箱'}), 400

    success, message = AuthService.reset_password_request(email)

    return jsonify({
        'success': success,
        'message': message
    })


@auth_bp.route('/subscription', methods=['GET'])
@auth_required
def get_subscription():
    """获取订阅信息"""
    user = get_current_user()

    return jsonify({
        'success': True,
        'subscription': {
            'tier': user.subscription_tier,
            'is_pro': user.is_pro(),
            'is_vip': user.is_vip(),
            'is_active': user.is_subscription_active(),
            'expires': user.subscription_expires.isoformat() if user.subscription_expires else None,
            'ai_calls_used': user.ai_api_calls,
            'ai_calls_limit': user.get_ai_limit(),
        }
    })


@auth_bp.route('/ai/stats', methods=['GET'])
@auth_required
def get_ai_stats():
    """获取AI使用统计"""
    user = get_current_user()

    return jsonify({
        'success': True,
        'stats': {
            'calls_used': user.ai_api_calls,
            'calls_limit': user.get_ai_limit(),
            'calls_remaining': max(0, user.get_ai_limit() - user.ai_api_calls),
            'tier': user.subscription_tier,
        }
    })


# ==================== 管理员接口 ====================

@auth_bp.route('/admin/users', methods=['GET'])
@auth_required
def admin_list_users():
    """管理员：获取用户列表"""
    user = get_current_user()
    if not user.is_admin:
        return jsonify({'success': False, 'error': '需要管理员权限'}), 403

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')

    query = User.query
    if search:
        query = query.filter(
            db.or_(
                User.email.contains(search),
                User.nickname.contains(search)
            )
        )

    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'success': True,
        'users': [u.to_dict() for u in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@auth_bp.route('/admin/users/<int:user_id>', methods=['GET'])
@auth_required
def admin_get_user(user_id):
    """管理员：获取指定用户详情"""
    user = get_current_user()
    if not user.is_admin:
        return jsonify({'success': False, 'error': '需要管理员权限'}), 403

    target_user = User.query.get_or_404(user_id)
    return jsonify({
        'success': True,
        'user': target_user.to_dict()
    })


@auth_bp.route('/admin/users/<int:user_id>/subscription', methods=['PUT'])
@auth_required
def admin_update_subscription(user_id):
    """管理员：修改用户订阅"""
    admin = get_current_user()
    if not admin.is_admin:
        return jsonify({'success': False, 'error': '需要管理员权限'}), 403

    target_user = User.query.get_or_404(user_id)
    data = request.json or {}

    tier = data.get('tier', 'free')
    expires = data.get('expires')

    target_user.subscription_tier = tier
    if expires:
        from datetime import datetime
        target_user.subscription_expires = datetime.fromisoformat(expires)
    else:
        target_user.subscription_expires = None

    db.session.commit()

    return jsonify({
        'success': True,
        'message': '订阅已更新',
        'user': target_user.to_dict()
    })


@auth_bp.route('/admin/stats', methods=['GET'])
@auth_required
def admin_get_stats():
    """管理员：获取系统统计"""
    admin = get_current_user()
    if not admin.is_admin:
        return jsonify({'success': False, 'error': '需要管理员权限'}), 403

    from src.models.models import StudySession, Diary, Task
    from sqlalchemy import func
    from datetime import datetime, timedelta

    today = datetime.utcnow().date()

    stats = {
        'total_users': User.query.count(),
        'active_users_today': User.query.filter(User.last_active >= datetime.utcnow() - timedelta(days=1)).count(),
        'total_study_hours': db.session.query(func.sum(StudySession.duration_minutes)).filter(
            StudySession.date == today
        ).scalar() or 0,
        'total_diaries_today': Diary.query.filter_by(date=today).count(),
        'total_tasks': Task.query.count(),
        'subscription_breakdown': {
            'free': User.query.filter_by(subscription_tier='free').count(),
            'pro': User.query.filter_by(subscription_tier='pro').count(),
            'vip': User.query.filter_by(subscription_tier='vip').count(),
        }
    }

    return jsonify({
        'success': True,
        'stats': stats
    })
