"""
StudyPal 认证模块
用户注册、登录、JWT Token 管理

作者：StudyPal
日期：2026-05-21
"""

import jwt
import secrets
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, Tuple
from flask import request, jsonify, g, current_app

from src.models.models import db, User


class AuthService:
    """认证服务"""

    @staticmethod
    def generate_token(user_id: int, expires_hours: int = 24) -> str:
        """生成JWT Token"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(hours=expires_hours),
            'iat': datetime.utcnow(),
            'jti': secrets.token_hex(16)  # JWT ID，用于Token追踪
        }
        secret = current_app.config.get('SECRET_KEY', 'dev-secret-key')
        token = jwt.encode(payload, secret, algorithm='HS256')
        return token

    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """验证Token"""
        try:
            secret = current_app.config.get('SECRET_KEY', 'dev-secret-key')
            payload = jwt.decode(token, secret, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @staticmethod
    def register(email: str, password: str, nickname: str = None) -> Tuple[bool, str, Optional[User]]:
        """
        用户注册

        返回: (成功标志, 消息, 用户对象)
        """
        email = email.lower().strip()

        # 验证邮箱格式
        if '@' not in email or '.' not in email:
            return False, '邮箱格式不正确', None

        # 验证密码强度
        if len(password) < 6:
            return False, '密码至少6位', None

        # 检查邮箱是否已存在
        existing = User.query.filter_by(email=email).first()
        if existing:
            return False, '该邮箱已注册', None

        # 创建用户
        nickname = nickname or email.split('@')[0][:20]
        user = User(
            email=email,
            nickname=nickname[:50],
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        return True, '注册成功', user

    @staticmethod
    def login(email: str, password: str) -> Tuple[bool, str, Optional[User], Optional[str]]:
        """
        用户登录

        返回: (成功标志, 消息, 用户对象, Token)
        """
        email = email.lower().strip()

        user = User.query.filter_by(email=email).first()
        if not user:
            return False, '邮箱或密码错误', None, None

        if not user.check_password(password):
            return False, '邮箱或密码错误', None, None

        if not user.is_active:
            return False, '账号已被禁用', None, None

        # 更新最后活跃时间
        user.last_active = datetime.utcnow()
        db.session.commit()

        # 生成Token
        token = AuthService.generate_token(user.id)

        return True, '登录成功', user, token

    @staticmethod
    def change_password(user_id: int, old_password: str, new_password: str) -> Tuple[bool, str]:
        """修改密码"""
        user = User.query.get(user_id)
        if not user:
            return False, '用户不存在'

        if not user.check_password(old_password):
            return False, '原密码错误'

        if len(new_password) < 6:
            return False, '新密码至少6位'

        user.set_password(new_password)
        db.session.commit()
        return True, '密码修改成功'

    @staticmethod
    def reset_password_request(email: str) -> Tuple[bool, str]:
        """
        请求重置密码（发送验证码）

        实际项目中这里应该发送邮件
        """
        email = email.lower().strip()
        user = User.query.filter_by(email=email).first()

        if not user:
            # 为防止邮箱枚举攻击，即使不存在也返回成功
            return True, '如果邮箱存在，重置链接已发送'

        # 生成6位数字验证码
        reset_code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])

        # 实际项目中应该发送邮件
        # 这里简化为打印到日志
        current_app.logger.info(f"Password reset code for {email}: {reset_code}")

        # 存储验证码（实际项目用Redis，简化版用内存字典）
        if not hasattr(g, 'reset_codes'):
            g.reset_codes = {}
        g.reset_codes[email] = {
            'code': reset_code,
            'expires': datetime.utcnow() + timedelta(minutes=10)
        }

        return True, '验证码已发送'


def get_current_user() -> Optional[User]:
    """获取当前登录用户"""
    return getattr(g, 'current_user', None)


def auth_required(f):
    """认证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')

        if not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'error': '请先登录'}), 401

        token = auth_header[7:]
        payload = AuthService.verify_token(token)

        if not payload:
            return jsonify({'success': False, 'error': 'Token已过期，请重新登录'}), 401

        user = User.query.get(payload['user_id'])
        if not user:
            return jsonify({'success': False, 'error': '用户不存在'}), 401

        if not user.is_active:
            return jsonify({'success': False, 'error': '账号已被禁用'}), 401

        g.current_user = user
        return f(*args, **kwargs)

    return decorated


def auth_optional(f):
    """可选认证装饰器（登录用户返回用户信息，游客返回None）"""
    @wraps(f)
    def decorated(*args, **kwargs):
        g.current_user = None

        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            payload = AuthService.verify_token(token)
            if payload:
                user = User.query.get(payload['user_id'])
                if user and user.is_active:
                    g.current_user = user

        return f(*args, **kwargs)

    return decorated


def subscription_required(required_tier: str = 'pro'):
    """
    订阅等级装饰器

    required_tier: 'pro' 或 'vip'
    """
    def decorator(f):
        @wraps(f)
        @auth_required
        def decorated(*args, **kwargs):
            user = get_current_user()

            tier_hierarchy = {'free': 0, 'pro': 1, 'vip': 2}
            user_level = tier_hierarchy.get(user.subscription_tier, 0)
            required_level = tier_hierarchy.get(required_tier, 1)

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

        if not user.can_use_ai():
            return jsonify({
                'success': False,
                'error': '本月AI调用次数已用完，请升级会员或等待下月重置',
                'upgrade_url': '/subscription'
            }), 429

        return f(*args, **kwargs)
    return decorated
