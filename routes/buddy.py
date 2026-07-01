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


@buddy_bp.route('/chat', methods=['POST'])
def buddy_chat():
    """搭子对话（无需登录，用用户配置或默认配置）"""
    user = get_current_user()

    data = request.json or {}
    message = data.get('message', '').strip()
    conversation_id = data.get('conversation_id')

    if not message:
        return jsonify({'success': False, 'error': '消息不能为空'}), 400

    buddy = get_user_buddy()
    # 已登录则增加 AI 调用计数（轻量防护）
    if user is not None and hasattr(user, 'increment_ai_calls'):
        try:
            user.increment_ai_calls()
        except Exception:
            pass

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


# ========== 搭子轻量聊天（无需登录，读取当前用户的 AI 配置） ==========

BUDDY_QUICK_SYSTEM = {
    "xiaodou": (
        "你是「小豆」，温柔陪伴型学习搭子。语气温暖、可爱、像邻家妹妹，"
        "常用 🌸🌱✨ 等花朵类 emoji。回答前先共情，再给建议。"
        "回复尽量在 200 字以内。"
    ),
    "aran": (
        "你是「阿燃」，热血激励型学习搭子。语气激情、像运动队长，"
        "常用 ⚡🔥💪 等战斗 emoji，常用「冲」「干」「就完事了」等口头禅。"
        "回复尽量在 200 字以内。"
    ),
    "senior": (
        "你是「学姐」，学霸导师型学习搭子。冷静理性、结构化输出、"
        "考试导向。可使用 1./2./3. 等编号，常用 📚✅🧪 等学术 emoji。"
        "回复尽量在 200 字以内。"
    ),
    "xiaoye": (
        "你是「小夜」，深夜倾听型学习搭子。温柔安静、治愈不 push、"
        "循序渐进、情绪安抚优先。常用 🌙⭐🌌 等夜空 emoji。"
        "回复尽量在 200 字以内。"
    ),
    # 前端会用 xuejie 作为 key
    "xuejie": (
        "你是「学姐」，学霸导师型学习搭子。冷静理性、结构化输出、"
        "考试导向。可使用 1./2./3. 等编号，常用 📚✅🧪 等学术 emoji。"
        "回复尽量在 200 字以内。"
    ),
}


@buddy_bp.route('/quick-chat', methods=['POST'])
def buddy_quick_chat():
    """搭子轻量聊天（无需登录），读取当前用户已配置的 AI 模型。

    请求: { "buddy_id": "xiaodou", "message": "...", "explain_mode": "auto|game|speed" }
    返回: { "success": true, "reply": "...", "buddy_id", "buddy_name", "used_model" }
    """
    from src.ai.ai_helper import build_ai_from_user
    from src.buddy.buddy_roles import BUDDY_ROLES

    user = get_current_user()
    data = request.json or {}
    buddy_id = (data.get('buddy_id') or 'xiaodou').strip()
    message = (data.get('message') or '').strip()
    explain_mode = (data.get('explain_mode') or 'auto').strip()

    if not message:
        return jsonify({'success': False, 'error': '消息不能为空'}), 400

    system_prompt = BUDDY_QUICK_SYSTEM.get(buddy_id) or BUDDY_QUICK_SYSTEM['xiaodou']

    # 根据讲解模式追加系统提示
    if explain_mode == 'game':
        system_prompt += "\n\n【当前模式：冒险探索】请用游戏化的方式回应：可以先抛出一个互动小问题，再给出鼓励。"
    elif explain_mode == 'speed':
        system_prompt += "\n\n【当前模式：学霸速读】请直接、高效、结构化地回答，少寒暄多干货。"

    role = BUDDY_ROLES.get(buddy_id) or BUDDY_ROLES.get('xiaodou') or {}
    buddy_name = role.get('name', '小豆')

    try:
        import traceback as _tb
        print(f"\n[DEBUG] === /api/buddy/quick-chat Start ===", flush=True)
        print(f"[DEBUG] user={bool(user)} buddy_id={buddy_id} explain_mode={explain_mode} msg_len={len(message)}", flush=True)

        ai = build_ai_from_user(user or {})
        info = ai.get_current_model_info()
        print(f"[DEBUG] resolved model: key={info.get('key')} name={info.get('name')} url={info.get('base_url')} key_len={len(ai.model_api_key)} provider={ai.provider}", flush=True)

        result = ai.ask(
            question=message,
            system_prompt=system_prompt,
            save_to_history=False,
        )
        reply = (result.get('answer') or '').strip()
        return jsonify({
            'success': True,
            'reply': reply[:4000],
            'buddy_id': buddy_id,
            'buddy_name': buddy_name,
            'used_model': ai.get_current_model_info().get('name', ''),
        })
    except Exception as e:
        import traceback as _tb
        print(f"[DEBUG-QUICK-CHAT] exception: {type(e).__name__}: {e}", flush=True)
        _tb.print_exc()
        return jsonify({
            'success': False,
            'error': f'AI 调用失败：{str(e)}',
            'tip': '请检查「设置 → AI 配置」中的 API 地址、密钥、模型名是否正确'
        }), 500


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


# ========== 知识点讲解 ==========

@buddy_bp.route('/explain', methods=['POST'])
def buddy_explain():
    """知识点讲解：基于当前搭子角色调用 AI 模型"""
    from src.ai.prompt_templates import get_buddy_explain_prompt, parse_explain_response
    from src.ai.ai_helper import build_ai_from_user
    from src.buddy.buddy_roles import BUDDY_ROLES

    data = request.json or {}
    topic = (data.get('topic') or '').strip()
    role_id = (data.get('buddy_id') or 'xiaodou').strip()

    if not topic:
        return jsonify({'success': False, 'error': '请输入要讲解的知识点'}), 400

    # 兼容前端会传的 xuejie → senior
    role_alias = {
        'xuejie': 'senior',
        'xiaodou': 'xiaodou',
        'aran': 'aran',
        'xiaoye': 'xiaoye',
    }
    role_id = role_alias.get(role_id, role_id)

    # 获取当前用户（如果登录了）
    user = get_current_user()

    # 获取角色信息（默认给一个）
    role = BUDDY_ROLES.get(role_id) or BUDDY_ROLES.get('xiaodou') or {}
    role_name = role.get('name', '小豆')
    role_emoji = role.get('emoji', '🌸')

    # 取系统提示词
    system_prompt = get_buddy_explain_prompt(role_id)

    # 用户问题
    user_question = f"请帮我讲解这个知识点：{topic}\n（请严格按照 ---GAME_START---/---GAME_END---/---EXPLAIN_START---/---EXPLAIN_END--- 标记输出）"

    try:
        # 关键：用用户的 ai_custom_config / ai_model_key，无登录则用默认
        ai = build_ai_from_user(user or {})
        result = ai.ask(
            question=user_question,
            system_prompt=system_prompt,
            save_to_history=False,
        )
        raw = (result.get('answer') or '').strip()
        parsed = parse_explain_response(raw)

        # 限制长度（避免前端爆栈）
        parsed["game"] = (parsed.get("game") or "")[:4000]
        parsed["explain"] = (parsed.get("explain") or "")[:4000]

        return jsonify({
            'success': True,
            'buddy_id': role_id,
            'buddy_name': role_name,
            'buddy_emoji': role_emoji,
            'topic': topic,
            'game': parsed.get('game', ''),
            'explain': parsed.get('explain', ''),
            'used_model': ai.get_current_model_info().get('name', ''),
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'AI 调用失败：{str(e)}',
            'tip': '请检查「设置 → AI 配置」中的 API 地址、密钥、模型名是否正确'
        }), 500


# ========== 历史对话（需登录） ==========

def _ensure_history_list(user: dict):
    if not isinstance(user, dict):
        return []
    hist = user.get('buddy_conversations_history')
    if not isinstance(hist, list):
        hist = []
        user['buddy_conversations_history'] = hist
    return hist


@buddy_bp.route('/conversations', methods=['GET'])
@auth_required
def list_conversations():
    """获取当前用户的历史对话列表"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'error': '请先登录'}), 401

    hist = _ensure_history_list(user)
    hist_sorted = sorted(hist, key=lambda x: x.get('updated_at', ''), reverse=True)
    return jsonify({'success': True, 'conversations': hist_sorted})


@buddy_bp.route('/conversation', methods=['POST'])
@auth_required
def save_conversation():
    """保存当前对话到历史（追加到末尾，只保留最近 20 条）"""
    import uuid
    from datetime import datetime
    from src.auth.auth import _load_users, _save_users

    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'error': '请先登录'}), 401

    data = request.json or {}
    buddy_id = (data.get('buddy_id') or '').strip()
    messages = data.get('messages') or []

    if not buddy_id:
        return jsonify({'success': False, 'error': 'buddy_id 不能为空'}), 400
    if not isinstance(messages, list) or len(messages) < 2:
        return jsonify({'success': False, 'error': '对话内容太少，无需保存'}), 400

    users = _load_users()
    user_dict = None
    for v in users.values():
        if v.get('id') == user.get('id'):
            user_dict = v
            break
    if not user_dict:
        return jsonify({'success': False, 'error': '用户不存在'}), 404

    hist = _ensure_history_list(user_dict)

    preview = ''
    for m in messages:
        if m.get('sender') == 'user':
            preview = (m.get('text') or '')[:30]
            break
    if not preview:
        preview = '新对话'

    from src.buddy.buddy_roles import BUDDY_ROLES
    role = BUDDY_ROLES.get(buddy_id) or {}

    conv = {
        'id': 'conv_' + uuid.uuid4().hex[:10],
        'buddy_id': buddy_id,
        'buddy_name': role.get('name', buddy_id),
        'buddy_avatar': role.get('emoji', '🤖'),
        'preview': preview,
        'message_count': len(messages),
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'messages': messages,
    }
    hist.append(conv)
    if len(hist) > 20:
        hist[:] = hist[-20:]
    _save_users(users)

    return jsonify({'success': True, 'conversation': conv})


@buddy_bp.route('/conversation/<conv_id>', methods=['GET'])
@auth_required
def get_conversation(conv_id):
    """获取某条历史对话详情"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'error': '请先登录'}), 401

    hist = _ensure_history_list(user)
    conv = next((c for c in hist if c.get('id') == conv_id), None)
    if not conv:
        return jsonify({'success': False, 'error': '对话不存在'}), 404
    return jsonify({'success': True, 'conversation': conv})


@buddy_bp.route('/conversation/<conv_id>', methods=['DELETE'])
@auth_required
def delete_conversation(conv_id):
    """删除某条历史对话"""
    from src.auth.auth import _load_users, _save_users

    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'error': '请先登录'}), 401

    users = _load_users()
    user_dict = None
    for v in users.values():
        if v.get('id') == user.get('id'):
            user_dict = v
            break
    if not user_dict:
        return jsonify({'success': False, 'error': '用户不存在'}), 404

    hist = _ensure_history_list(user_dict)
    before = len(hist)
    user_dict['buddy_conversations_history'] = [c for c in hist if c.get('id') != conv_id]
    if len(user_dict['buddy_conversations_history']) == before:
        return jsonify({'success': False, 'error': '对话不存在'}), 404
    _save_users(users)
    return jsonify({'success': True, 'message': '已删除'})
