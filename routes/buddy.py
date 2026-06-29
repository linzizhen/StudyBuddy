"""
StudyPal 搭子路由
处理搭子对话、档案、记忆相关 API
"""

from flask import Blueprint, jsonify, request
from typing import Dict, Any, Optional, List

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
    game_mode = data.get('game_mode', 'auto')

    if not message:
        return jsonify({'success': False, 'error': '消息不能为空'}), 400

    from src.buddy.buddy_conversations import get_buddy_conversations
    from src.buddy.buddy_roles import BUDDY_ROLES

    buddy = get_buddy()
    buddy_info = buddy.profile.get_buddy_info()
    role_key = buddy_info.get('role_key', 'xiaodou')
    role = BUDDY_ROLES.get(role_key, {})

    store = get_buddy_conversations()
    conv_id = conversation_id or store.get_active_id()
    if not conv_id or not store.get_by_id(conv_id):
        conv_id = store.create_new(
            buddy_role_key=role_key,
            buddy_name=buddy_info.get('name', role.get('name', '小豆')),
            buddy_emoji=buddy_info.get('emoji', role.get('emoji', '🌸')),
        )

    history_raw = store.get_messages(conv_id)
    history_messages = [
        {"role": m["role"], "content": m["content"]}
        for m in history_raw
    ]
    store.add_message(conv_id, 'user', message)

    result = buddy.chat(
        message,
        conv_id,
        game_mode=game_mode,
        history_messages=history_messages,
    )
    store.add_message(conv_id, 'assistant', result['reply'], buddy_snapshot={
        'role_key': role_key,
        'name': buddy_info.get('name', role.get('name', '小豆')),
        'emoji': buddy_info.get('emoji', role.get('emoji', '🌸')),
        'avatar_url': role.get('avatar_url', ''),
    })

    buddy_payload = {
        'name': buddy_info.get('name', role.get('name', '小豆')),
        'emoji': buddy_info.get('emoji', role.get('emoji', '🌸')),
        'avatar_url': role.get('avatar_url', ''),
        'role_key': role_key,
        'game_style': role.get('game_style', 'direct'),
    }
    print(f"返回搭子: {buddy_payload['name']}, emoji: {buddy_payload['emoji']}, role: {role_key}")

    return jsonify({
        'success': True,
        'reply': result['reply'],
        'conversation_id': conv_id,
        'emotion': result['emotion'],
        'emoji': result['emoji'],
        'emotion_desc': result.get('emotion_desc', ''),
        'suggestions': result.get('suggestions', []),
        'options': result.get('options', []),
        'option_texts': result.get('option_texts', []),
        'game_over': result.get('game_over', False),
        'game_mode': result.get('game_mode', game_mode),
        'use_gamification': result.get('use_gamification', False),
        'buddy': buddy_payload,
        'role_consistency': result.get('role_consistency'),
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
    """切换搭子角色（清空旧上下文 + 隔离对话历史）"""
    from src.buddy.buddy_roles import BuddyRoles, BUDDY_ROLES
    from src.buddy.buddy_conversations import get_buddy_conversations
    from src.buddy.buddy_profile import get_buddy_profile

    if role_key not in BUDDY_ROLES:
        return jsonify({'success': False, 'error': '角色不存在'}), 400
    role = BUDDY_ROLES[role_key]
    buddy = get_buddy()
    success = buddy.switch_role(role_key)
    if not success:
        return jsonify({'success': False, 'error': '角色切换失败'}), 400

    # 用户名（用于开场白）
    user_name = ""
    try:
        profile = get_buddy_profile()
        user_name = profile.get_user().get("name", "") or ""
    except Exception:
        pass

    # 上下文隔离：清空旧 messages + 注入新角色开场白
    store = get_buddy_conversations()
    store.update_active_buddy(role_key, role['name'], role['emoji'])
    new_conv = store.switch_role_with_isolation(
        new_role_key=role_key,
        new_role_name=role['name'],
        new_role_emoji=role['emoji'],
        new_role_avatar=role.get('avatar_url', ''),
        user_name=user_name,
    )

    return jsonify({
        'success': True,
        'role_key': role_key,
        'name': role['name'],
        'emoji': role['emoji'],
        'personality': role['personality'],
        'greeting': role['greeting'],
        'avatar_url': role.get('avatar_url', ''),
        'game_style': role.get('game_style', 'direct'),
        'history_cleared': True,
        'conversation_id': new_conv['id'] if new_conv else None,
        'messages': new_conv.get('messages', []) if new_conv else [],
        'message': f'已切换到 {role["name"]}，对话上下文已重置',
    })


@buddy_bp.route('/current-role', methods=['GET'])
def get_current_role():
    """获取当前搭子角色"""
    from src.buddy.buddy_profile import get_buddy_profile
    from src.buddy.buddy_roles import BuddyRoles, BUDDY_ROLES
    profile = get_buddy_profile()
    buddy_info = profile.get_buddy_info()
    current_role = buddy_info.get('role_key', 'xiaodou')
    role_config = BuddyRoles.get_role(current_role)
    role_full = BUDDY_ROLES.get(current_role, {})
    return jsonify({
        'success': True,
        'role': current_role,
        'name': buddy_info.get('name', '小豆'),
        'emoji': buddy_info.get('emoji', '🌸'),
        'trait': buddy_info.get('personality', '温柔陪伴型'),
        'role_key': current_role,
        'avatar_url': role_full.get('avatar_url', buddy_info.get('avatar_url', '')),
        'game_style': role_config.get('game_style', 'direct') if role_config else 'direct',
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


# ==================== 游戏化讲解测试 ====================

GAME_STYLE_TEST_QUESTION = "什么是机会成本？请给我讲解一下这个概念"


@buddy_bp.route('/game-style-test', methods=['POST'])
def test_game_styles():
    """
    测试所有搭子的游戏化讲解风格
    使用固定问题"机会成本"测试6个搭子的回复差异
    """
    from src.buddy.buddy_roles import BUDDY_ROLES
    from src.buddy.buddy_memory import get_buddy_memory
    from src.ai.prompt_templates import get_prompt_templates
    from src.ai.ai_helper import StudyPalAI

    data = request.json or {}
    model_override = data.get('model')
    test_question = data.get('question', GAME_STYLE_TEST_QUESTION)

    results = {}

    for role_key in BUDDY_ROLES.keys():
        try:
            role = BUDDY_ROLES[role_key]
            role_name = role['name']
            role_style_rules = role.get('game_style', 'direct')

            prompts = get_prompt_templates()
            memory_context = get_buddy_memory().build_context_for_ai()

            system_prompt = prompts.get_system_prompt(
                buddy_name=role_name,
                user_name="测试用户",
                study_summary="考研学习",
                memory_context=memory_context,
                current_phase="基础复习阶段"
            )

            full_rules = BuddyRoles.get_role_style_rules(role_key)
            if full_rules:
                system_prompt += "\n\n" + full_rules

            force_rules = BuddyRoles.get_game_style_force_rules(role_key)
            system_prompt += "\n\n" + force_rules
            system_prompt += "\n\n【本轮覆盖规则】用户在问知识点，必须先给A/B/C选项，禁止直接讲定义。"

            user_question = f"{force_rules}\n\n现在用户问：{test_question}\n\n[注意：必须游戏化讲解，先给A/B/C选项]"

            ai = StudyPalAI(model_override=model_override)
            result = ai.ask(
                question=user_question,
                use_history=False,
                save_to_history=False,
                system_prompt=system_prompt
            )

            results[role_key] = {
                'name': role_name,
                'game_style': role.get('game_style', 'direct'),
                'reply': result.get('answer', ''),
                'success': True
            }
        except Exception as e:
            results[role_key] = {
                'name': role.get('name', role_key),
                'game_style': role.get('game_style', 'direct'),
                'reply': f'测试失败: {str(e)}',
                'success': False
            }

    return jsonify({
        'success': True,
        'question': test_question,
        'results': results
    })


@buddy_bp.route('/game-style-test/<role_key>', methods=['POST'])
def test_single_game_style(role_key):
    """
    测试单个搭子的游戏化讲解风格
    """
    from src.buddy.buddy_roles import BUDDY_ROLES, BuddyRoles
    from src.buddy.buddy_memory import get_buddy_memory
    from src.ai.prompt_templates import get_prompt_templates
    from src.ai.ai_helper import StudyPalAI

    data = request.json or {}
    model_override = data.get('model')
    test_question = data.get('question', GAME_STYLE_TEST_QUESTION)

    role = BUDDY_ROLES.get(role_key)
    if not role:
        return jsonify({'success': False, 'error': '角色不存在'}), 400

    try:
        role_name = role['name']

        prompts = get_prompt_templates()
        memory_context = get_buddy_memory().build_context_for_ai()

        system_prompt = prompts.get_system_prompt(
            buddy_name=role_name,
            user_name="测试用户",
            study_summary="考研学习",
            memory_context=memory_context,
            current_phase="基础复习阶段"
        )

        full_rules = BuddyRoles.get_role_style_rules(role_key)
        if full_rules:
            system_prompt += "\n\n" + full_rules

        force_rules = BuddyRoles.get_game_style_force_rules(role_key)
        system_prompt += "\n\n" + force_rules
        system_prompt += "\n\n【本轮覆盖规则】用户在问知识点，必须先给A/B/C选项，禁止直接讲定义。"

        user_question = f"{force_rules}\n\n现在用户问：{test_question}\n\n[注意：必须游戏化讲解，先给A/B/C选项]"

        ai = StudyPalAI(model_override=model_override)
        result = ai.ask(
            question=user_question,
            use_history=False,
            save_to_history=False,
            system_prompt=system_prompt
        )

        return jsonify({
            'success': True,
            'question': test_question,
            'role_key': role_key,
            'name': role_name,
            'game_style': role.get('game_style', 'direct'),
            'reply': result.get('answer', ''),
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


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
