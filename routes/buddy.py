"""
StudyPal 搭子路由
处理搭子对话、档案、记忆相关 API
"""

from flask import Blueprint, jsonify, request
from typing import Dict, Any, Optional

buddy_bp = Blueprint('buddy', __name__, url_prefix='/api/buddy')


def get_buddy():
    """复用 utils 的缓存版本"""
    from routes.utils import get_buddy
    return get_buddy()


@buddy_bp.route('/status', methods=['GET'])
def get_buddy_status():
    """获取搭子完整状态"""
    buddy = get_buddy()
    return jsonify({
        'success': True,
        'status': buddy.get_full_status()
    })


@buddy_bp.route('/chat', methods=['POST'])
def buddy_chat():
    """搭子对话"""
    data = request.json or {}
    message = data.get('message', '').strip()
    conversation_id = data.get('conversation_id')

    if not message:
        return jsonify({'success': False, 'error': '消息不能为空'}), 400

    buddy = get_buddy()
    result = buddy.chat(message, conversation_id)

    return jsonify({
        'success': True,
        'reply': result['reply'],
        'conversation_id': result.get('conversation_id'),
        'emotion': result['emotion'],
        'emoji': result['emoji'],
        'emotion_desc': result.get('emotion_desc', ''),
        'suggestions': result.get('suggestions', [])
    })


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


@buddy_bp.route('/roles', methods=['GET'])
def get_buddy_roles():
    """获取所有搭子角色列表"""
    from src.buddy.buddy_roles import BuddyRoles
    roles = BuddyRoles.get_all_roles()
    return jsonify({'success': True, 'roles': roles})


@buddy_bp.route('/switch/<role_key>', methods=['POST'])
def switch_buddy_role(role_key):
    """切换搭子角色"""
    buddy = get_buddy()
    success = buddy.switch_role(role_key)
    if success:
        return jsonify({'success': True, 'message': f'已切换到 {role_key}'})
    return jsonify({'success': False, 'error': '角色不存在'}), 400


@buddy_bp.route('/current-role', methods=['GET'])
def get_current_role():
    """获取当前搭子角色"""
    from src.buddy.buddy_profile import get_buddy_profile
    profile = get_buddy_profile()
    buddy_info = profile.get_buddy_info()
    current_role = buddy_info.get('role_key', 'xiaodou')
    return jsonify({
        'success': True,
        'role': current_role,
        'name': buddy_info.get('name', '小豆'),
        'emoji': buddy_info.get('emoji', '🌸'),
        'trait': buddy_info.get('personality', '温柔陪伴型'),
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


# ==================== 搭子系统测试（内部使用）====================

@buddy_bp.route('/test', methods=['POST'])
def test_buddy_system():
    """
    内部测试端点：验证搭子系统是否可用。
    使用当前 active 学习搭子角色，绑定用户配置的模型，
    发送固定测试问题，返回真实 AI 响应。
    """
    data = request.json or {}
    # 可选：外部传入模型配置（来自 localStorage）
    model_override = data.get('model')

    TEST_QUESTION = "我今天不想学习，怎么办？"

    try:
        # 获取当前搭子角色
        from src.buddy.buddy_profile import get_buddy_profile
        from src.buddy.buddy_roles import BuddyRoles
        from src.ai.ai_helper import StudyPalAI
        from src.buddy.buddy_memory import get_buddy_memory
        from src.ai.prompt_templates import get_prompt_templates

        profile = get_buddy_profile()
        buddy_info = profile.get_buddy_info()
        role_key = buddy_info.get('role_key', 'xiaodou')
        role_name = buddy_info.get('name', '小豆')

        # 获取角色风格规则（核心人格设定）
        role_style_rules = BuddyRoles.get_role_style_rules(role_key)

        # 构建系统提示词
        prompts = get_prompt_templates()
        memory_context = get_buddy_memory().build_context_for_ai()
        current_phase = profile.get_current_phase()
        user_profile = profile.get_user()
        study_summary = profile.get_study_summary()

        system_prompt = prompts.get_system_prompt(
            buddy_name=role_name,
            user_name=user_profile.get('name', ''),
            study_summary=study_summary,
            memory_context=memory_context,
            current_phase=current_phase
        )
        # 拼接角色风格规则
        if role_style_rules:
            system_prompt += "\n\n" + role_style_rules

        # 使用模型（优先外部配置，否则用 config.py 默认）
        ai = StudyPalAI(model_override=model_override)

        # 调用 AI
        result = ai.ask(
            question=TEST_QUESTION,
            use_history=False,
            save_to_history=False,
            system_prompt=system_prompt
        )

        return jsonify({
            'success': True,
            'role_key': role_key,
            'role_name': role_name,
            'model_used': ai.model_name,
            'question': TEST_QUESTION,
            'reply': result.get('answer', ''),
            'conversation_id': result.get('conversation_id', ''),
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
