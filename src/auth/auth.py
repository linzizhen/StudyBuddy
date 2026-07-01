"""
StudyPal 认证模块（轻量版）
不依赖 flask-sqlalchemy / pyjwt，使用内置实现

作者：StudyPal
日期：2026-05-21
"""

import json
import os
import time
import secrets
import hashlib
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, g, current_app

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')


def _ensure_data_dir():
    """确保数据目录存在"""
    os.makedirs(DATA_DIR, exist_ok=True)


def _load_users():
    """加载用户数据"""
    _ensure_data_dir()
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}


def _save_users(users):
    """保存用户数据"""
    _ensure_data_dir()
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2, default=str)


def _hash_password(password: str) -> str:
    """哈希密码"""
    return hashlib.sha256(password.encode()).hexdigest()


def _generate_token(user_id: int) -> str:
    """生成简单 Token"""
    payload = f"{user_id}:{int(time.time())}:{secrets.token_hex(8)}"
    return secrets.token_hex(16) + '.' + payload


def _verify_token(token: str):
    """验证 Token"""
    try:
        print(f"[VERIFY] token={repr(token[:60] if token else '')}")
        parts = token.split('.')
        if len(parts) < 2:
            print(f"[VERIFY] split by '.' = {len(parts)} parts, < 2 -> None")
            return None
        # 前16位hex作为签名
        payload = '.'.join(parts[1:])
        print(f"[VERIFY] payload={repr(payload[:80])}")
        user_id = int(payload.split(':')[0])
        ts = int(payload.split(':')[1])
        print(f"[VERIFY] user_id={user_id} ts={ts} (now={int(time.time())})")
        # Token 有效期 24 小时
        if time.time() - ts > 86400:
            print(f"[VERIFY] expired by {(time.time()-ts)/3600:.1f}h")
            return None
        print(f"[VERIFY] OK -> user_id={user_id}")
        return user_id
    except Exception as e:
        print(f"[VERIFY] exception: {e}")
        return None


class AuthService:
    """认证服务（轻量版）"""

    @staticmethod
    def register(email: str, password: str, nickname: str = None) -> tuple:
        email = email.lower().strip()
        if '@' not in email or '.' not in email:
            return False, '邮箱格式不正确', None
        if len(password) < 6:
            return False, '密码至少6位', None

        users = _load_users()
        if email in users:
            return False, '该邮箱已注册', None

        nickname = nickname or email.split('@')[0][:20]
        user_id = len(users) + 1

        users[email] = {
            'id': user_id,
            'email': email,
            'password_hash': _hash_password(password),
            'nickname': nickname[:50],
            'avatar': '🌸',
            'subscription_tier': 'free',
            'subscription_expires': None,
            'ai_api_calls': 0,
            'ai_api_reset_date': None,
            'theme': 'light',
            'ai_model_key': None,
            'ai_custom_config': None,
            'current_role_id': 'xiaodou',
            'custom_buddy_name': None,
            'target_school': None,
            'target_major': None,
            'target_score': 0,
            'exam_date': None,
            'daily_goal_hours': 8.0,
            'total_study_hours': 0.0,
            'total_sessions': 0,
            'current_streak': 0,
            'longest_streak': 0,
            'created_at': datetime.now().isoformat(),
            'last_active': datetime.now().isoformat(),
            'is_active': True,
            'is_admin': False,
        }
        _save_users(users)

        user = users[email].copy()
        user['token'] = _generate_token(user_id)
        return True, '注册成功', user

    @staticmethod
    def login(email: str, password: str) -> tuple:
        email = email.lower().strip()
        users = _load_users()

        if email not in users:
            return False, '邮箱或密码错误', None, None

        user = users[email]
        if user['password_hash'] != _hash_password(password):
            return False, '邮箱或密码错误', None, None

        if not user.get('is_active', True):
            return False, '账号已被禁用', None, None

        user['last_active'] = datetime.now().isoformat()
        _save_users(users)

        token = _generate_token(user['id'])
        user['token'] = token
        return True, '登录成功', user, token

    @staticmethod
    def get_user_by_id(user_id: int):
        """根据 ID 获取用户"""
        users = _load_users()
        for email, user in users.items():
            if user['id'] == user_id:
                return user
        return None

    @staticmethod
    def update_user(user_id: int, updates: dict):
        """更新用户信息"""
        users = _load_users()
        for email, user in users.items():
            if user['id'] == user_id:
                for key, value in updates.items():
                    if key not in ('id', 'email', 'password_hash'):
                        user[key] = value
                _save_users(users)
                return user
        return None

    @staticmethod
    def increment_ai_calls(user_id: int):
        """增加AI调用次数"""
        users = _load_users()
        for email, user in users.items():
            if user['id'] == user_id:
                user['ai_api_calls'] = user.get('ai_api_calls', 0) + 1
                _save_users(users)
                return
        _save_users(users)

    @staticmethod
    def get_all_users():
        """获取所有用户（管理员用）"""
        return _load_users()


def auth_required(f):
    """认证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'error': '请先登录'}), 401

        token = auth_header[7:]
        user_id = _verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'error': 'Token已过期，请重新登录'}), 401

        user = AuthService.get_user_by_id(user_id)
        if not user:
            return jsonify({'success': False, 'error': '用户不存在'}), 401
        if not user.get('is_active', True):
            return jsonify({'success': False, 'error': '账号已被禁用'}), 401

        g.current_user = user
        return f(*args, **kwargs)
    return decorated


def auth_optional(f):
    """可选认证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        g.current_user = None
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            user_id = _verify_token(token)
            if user_id:
                user = AuthService.get_user_by_id(user_id)
                if user and user.get('is_active', True):
                    g.current_user = user
        return f(*args, **kwargs)
    return decorated


def get_current_user():
    """获取当前用户"""
    return getattr(g, 'current_user', None)


def subscription_required(required_tier='pro'):
    """订阅等级装饰器"""
    def decorator(f):
        @wraps(f)
        @auth_required
        def decorated(*args, **kwargs):
            user = get_current_user()
            tier_map = {'free': 0, 'pro': 1, 'vip': 2}
            user_level = tier_map.get(user.get('subscription_tier', 'free'), 0)
            required_level = tier_map.get(required_tier, 1)
            if user_level < required_level:
                return jsonify({
                    'success': False,
                    'error': f'此功能需要 {required_tier.upper()} 会员',
                    'upgrade_url': '/subscription'
                }), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


def ai_limit_required(f):
    """AI调用限制装饰器"""
    @wraps(f)
    @auth_required
    def decorated(*args, **kwargs):
        user = get_current_user()
        tier = user.get('subscription_tier', 'free')
        limits = {'free': 100, 'pro': 1000, 'vip': 10000}
        limit = limits.get(tier, 100)
        calls = user.get('ai_api_calls', 0)
        if calls >= limit:
            return jsonify({
                'success': False,
                'error': '本月AI调用次数已用完，请升级会员',
                'upgrade_url': '/subscription'
            }), 429
        return f(*args, **kwargs)
    return decorated
