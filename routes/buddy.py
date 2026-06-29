"""
StudyPal 搭子路由
处理搭子对话、档案、记忆相关 API

作者：StudyPal
日期：2026-04-27
更新：2026-05-21 支持多用户认证
"""

from flask import Blueprint, jsonify, request, g
from typing import Dict, Any, Optional

from src.auth.auth import auth_required, auth_optional, get_current_user, ai_limit_required
from src.core.buddy import get_buddy

buddy_bp = Blueprint('buddy', __name__, url_prefix='/api/buddy')


def get_user_buddy():
    """获取当前用户的 Buddy 实例（基于用户数据）"""
    from src.core.buddy import get_buddy
    return get_buddy()


@auth_optional
@buddy_bp.route('/status', methods=['GET'])
def get_buddy_status():
    """获取搭子完整状态"""
    user = get_current_user()
    if not user:
        return jsonify({
            'success': True,
            'status': {
                'buddy': {'name': '小豆', 'emoji': '🌸'},
                'profile': {'is_setup': False},
                'message': '请先登录'
            }
        })

    buddy = get_user_buddy()
    return jsonify({
        'success': True,
        'status': buddy.get_full_status()
    })


@auth_required
@ai_limit_required
@buddy_bp.route('/chat', methods=['POST'])
def buddy_chat():
    """搭子对话"""
    user = get_current_user()

    data = request.json or {}
    message = data.get('message', '').strip()
    conversation_id = data.get('conversation_id')

    if not message:
        return jsonify({'success': False, 'error': '消息不能为空'}), 400

    buddy = get_user_buddy()
    result = buddy.chat(message, conversation_id)

    # 增加AI调用计数
    from src.auth.auth import AuthService
    AuthService.increment_ai_calls(user['id'])

    return jsonify({
        'success': True,
        'reply': result['reply'],
        'conversation_id': result.get('conversation_id'),
        'emotion': result['emotion'],
        'emoji': result['emoji'],
        'emotion_desc': result.get('emotion_desc', ''),
        'suggestions': result.get('suggestions', [])
    })


@auth_required
@buddy_bp.route('/profile', methods=['GET'])
def get_buddy_profile():
    """获取用户档案"""
    from src.buddy.buddy_profile import get_buddy_profile
    profile = get_buddy_profile()

    return jsonify({
        'success': True,
        'profile': profile.get_profile(),
        'days_remaining': profile.get_days_remaining(),
        'current_phase': profile.get_current_phase(),
        'is_setup': profile.is_setup_complete()
    })


@auth_required
@buddy_bp.route('/profile', methods=['PUT', 'POST'])
def update_buddy_profile():
    """更新用户档案"""
    from src.buddy.buddy_profile import get_buddy_profile
    profile = get_buddy_profile()
    data = request.json or {}
    profile.update_user(**data)

    return jsonify({
        'success': True,
        'message': '档案已更新',
        'profile': profile.get_profile()
    })


@auth_required
@buddy_bp.route('/memory', methods=['GET'])
def get_buddy_memory():
    """获取搭子记忆"""
    from src.buddy.buddy_memory import get_buddy_memory
    memory = get_buddy_memory()

    topic = request.args.get('topic')
    if topic:
        memories = memory.recall(topic)
        return jsonify({
            'success': True,
            'type': 'search',
            'memories': memories
        })

    stats = memory.get_memory_stats()
    recent = memory.get_recent_scenes(7)

    return jsonify({
        'success': True,
        'type': 'overview',
        'stats': stats,
        'recent_scenes': recent
    })


@auth_required
@buddy_bp.route('/memory', methods=['POST'])
def add_buddy_memory():
    """添加场景记忆"""
    from src.buddy.buddy_memory import get_buddy_memory
    memory = get_buddy_memory()
    data = request.json or {}

    scene_id = memory.add_scene(
        summary=data.get('summary', ''),
        scene_type=data.get('scene_type', 'conversation'),
        details=data.get('details', ''),
        tags=data.get('tags', [])
    )

    return jsonify({
        'success': True,
        'scene_id': scene_id
    })


@buddy_bp.route('/memory/search', methods=['GET'])
def search_buddy_memory():
    """语义搜索搭子记忆"""
    from src.buddy.buddy_memory import get_buddy_memory
    memory = get_buddy_memory()

    query = request.args.get('q', '')
    limit = request.args.get('limit', 5, type=int)

    results = memory.semantic_search(query, limit) if hasattr(memory, 'semantic_search') else memory.recall(query)[:limit]

    return jsonify({
        'success': True,
        'results': results
    })


@buddy_bp.route('/caring', methods=['GET'])
def get_caring_events():
    """获取主动关心事件"""
    from src.buddy.caring_engine import get_caring_engine
    caring = get_caring_engine()
    events = caring.check_all()

    return jsonify({
        'success': True,
        'events': [
            {
                'type': e.type,
                'message': e.message,
                'priority': e.priority
            }
            for e in events
        ]
    })


@buddy_bp.route('/achievement', methods=['POST'])
def trigger_achievement():
    """触发成就关心"""
    from src.buddy.caring_engine import get_caring_engine
    caring = get_caring_engine()
    data = request.json or {}

    event = caring.trigger_achievement(
        achievement_type=data.get('achievement_type', 'milestone'),
        sub_key=data.get('sub_key'),
        context=data.get('context', {})
    )

    if event:
        return jsonify({
            'success': True,
            'message': event.message,
            'type': event.type
        })

    return jsonify({
        'success': True,
        'message': '太棒了！你真厉害！',
        'type': 'achievement'
    })


# ========== 角色系统 API ==========

@buddy_bp.route('/roles', methods=['GET'])
def get_all_roles():
    """获取所有可选角色"""
    buddy = get_buddy()
    roles = buddy.get_all_roles()

    current_role_id = buddy.get_current_role_id()

    return jsonify({
        'success': True,
        'roles': roles,
        'current_role_id': current_role_id
    })


@buddy_bp.route('/role', methods=['GET'])
def get_current_role():
    """获取当前角色信息"""
    buddy = get_buddy()
    role = buddy.get_current_role()
    level_info = buddy.get_buddy_level_info()

    return jsonify({
        'success': True,
        'role': role,
        'level': level_info
    })


@buddy_bp.route('/role/switch', methods=['POST'])
def switch_role():
    """切换搭子角色"""
    data = request.json or {}
    role_id = data.get('role_id')

    if not role_id:
        return jsonify({'success': False, 'error': '请选择要切换的角色'}), 400

    buddy = get_buddy()
    result = buddy.switch_role(role_id)

    if result['success']:
        return jsonify({
            'success': True,
            'message': result['message'],
            'role': result['role'],
            'greeting': result['role']['greeting']
        })

    return jsonify({'success': False, 'error': result.get('message', '切换失败')}), 400


@buddy_bp.route('/role/level', methods=['GET'])
def get_buddy_level():
    """获取搭子等级信息"""
    buddy = get_buddy()
    level_info = buddy.get_buddy_level_info()

    return jsonify({
        'success': True,
        'level': level_info
    })
