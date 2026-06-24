"""搭子对话历史 API"""
from flask import Blueprint, jsonify, request

conversations_bp = Blueprint('conversations', __name__, url_prefix='/api/conversations')


def _buddy_info():
    from src.buddy.buddy_profile import get_buddy_profile
    from src.buddy.buddy_roles import BUDDY_ROLES
    profile = get_buddy_profile()
    info = profile.get_buddy_info()
    role_key = info.get('role_key', 'xiaodou')
    role = BUDDY_ROLES.get(role_key, {})
    return {
        'role_key': role_key,
        'name': info.get('name', role.get('name', '小豆')),
        'emoji': info.get('emoji', role.get('emoji', '🌸')),
    }


@conversations_bp.route('/active', methods=['GET'])
def get_active_conversation():
    from src.buddy.buddy_conversations import get_buddy_conversations
    store = get_buddy_conversations()
    active = store.get_active()
    if not active:
        return jsonify({'success': True, 'conversation': None})
    return jsonify({
        'success': True,
        'conversation': store.to_client_dict(active),
    })


@conversations_bp.route('', methods=['GET'])
def list_conversations():
    from src.buddy.buddy_conversations import get_buddy_conversations
    store = get_buddy_conversations()
    return jsonify({
        'success': True,
        'conversations': store.list_summaries(),
    })


@conversations_bp.route('', methods=['POST'])
def create_conversation():
    from src.buddy.buddy_conversations import get_buddy_conversations
    store = get_buddy_conversations()
    data = request.json or {}
    buddy = _buddy_info()
    title = data.get('title', '新对话')
    conv_id = store.create_new(
        buddy_role_key=buddy['role_key'],
        buddy_name=buddy['name'],
        buddy_emoji=buddy['emoji'],
        title=title,
    )
    conv = store.get_by_id(conv_id)
    return jsonify({
        'success': True,
        'conversation': store.to_client_dict(conv),
    })


@conversations_bp.route('/<conv_id>', methods=['GET'])
def get_conversation(conv_id):
    from src.buddy.buddy_conversations import get_buddy_conversations
    store = get_buddy_conversations()
    conv = store.get_by_id(conv_id)
    if not conv:
        return jsonify({'success': False, 'error': '对话不存在'}), 404
    store.activate(conv_id)
    return jsonify({
        'success': True,
        'conversation': store.to_client_dict(conv),
    })
