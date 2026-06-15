"""
StudyPal 用户路由
处理用户设置、座右铭、AI 对话等相关 API
"""

from flask import Blueprint, jsonify, request, send_file
from datetime import datetime
import os

user_bp = Blueprint('user', __name__, url_prefix='/api')


@user_bp.route('/home', methods=['GET'])
def get_home_data():
    """获取首页数据"""
    from routes.utils import get_buddy
    buddy = get_buddy()
    status = buddy.get_full_status()

    return jsonify({
        'success': True,
        'data': status
    })


@user_bp.route('/ask', methods=['POST'])
def ask():
    """AI 问答"""
    from src.ai.ai_helper import ask_ai_with_context
    from routes.utils import get_buddy
    buddy = get_buddy()
    data = request.json or {}
    question = data.get('question', '')
    conversation_id = data.get('conversation_id')

    if not question:
        return jsonify({'error': '问题不能为空'}), 400

    buddy.update_by_action('ask')

    try:
        result = ask_ai_with_context(question, conversation_id)
        answer = result['answer']
        conv_id = result['conversation_id']
    except Exception as e:
        return jsonify({
            'error': str(e),
            'emotion': buddy.get_emotion(),
            'emoji': buddy.get_emoji()
        }), 500

    buddy.update_by_action('answer_received')

    return jsonify({
        'answer': answer,
        'conversation_id': conv_id,
        'emotion': buddy.get_emotion(),
        'emoji': buddy.get_emoji()
    })


@user_bp.route('/motto', methods=['GET'])
def get_motto():
    """获取座右铭"""
    from src.modules.data_manager import get_motto
    motto = get_motto()
    return jsonify({'success': True, 'motto': motto})


@user_bp.route('/motto', methods=['POST'])
def set_motto():
    """设置座右铭"""
    from src.modules.data_manager import set_motto
    data = request.json or {}
    motto = data.get('motto', '').strip()
    try:
        set_motto(motto)
        return jsonify({
            'success': True,
            'message': '座右铭已更新',
            'motto': motto
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@user_bp.route('/favorite_quote', methods=['GET'])
def get_favorite_quote():
    """获取喜欢的激励语录"""
    from src.modules.data_manager import get_favorite_quote
    quote = get_favorite_quote()
    return jsonify({'success': True, 'favorite_quote': quote})


@user_bp.route('/favorite_quote', methods=['POST'])
def set_favorite_quote():
    """设置激励语录"""
    from src.modules.data_manager import set_favorite_quote
    data = request.json or {}
    quote = data.get('quote', '').strip()

    if set_favorite_quote(quote):
        return jsonify({
            'success': True,
            'message': '激励语录已更新',
            'quote': quote
        })
    return jsonify({'success': False, 'error': '保存失败'}), 500


@user_bp.route('/ai/history', methods=['GET'])
def get_ai_history():
    """获取所有 AI 对话历史列表"""
    from src.ai.ai_helper import get_ai_conversations
    conversations = get_ai_conversations()
    return jsonify({
        'success': True,
        'conversations': conversations
    })


@user_bp.route('/ai/history/<conversation_id>', methods=['GET'])
def get_ai_conversation(conversation_id):
    """获取指定对话的详细消息"""
    from src.ai.ai_helper import get_conversation_messages
    messages = get_conversation_messages(conversation_id)
    return jsonify({
        'success': True,
        'conversation_id': conversation_id,
        'messages': messages
    })


@user_bp.route('/ai/history', methods=['POST'])
def create_ai_conversation():
    """创建新对话"""
    from src.ai.ai_helper import new_ai_conversation
    conv_id = new_ai_conversation()
    return jsonify({
        'success': True,
        'conversation_id': conv_id,
        'message': '新对话已创建'
    })


@user_bp.route('/ai/history/<conversation_id>', methods=['DELETE'])
def delete_ai_history(conversation_id):
    """删除指定对话"""
    from src.ai.ai_helper import delete_ai_conversation
    success = delete_ai_conversation(conversation_id)
    return jsonify({
        'success': success,
        'message': '对话已删除' if success else '对话不存在'
    })


@user_bp.route('/ai/models', methods=['GET'])
def get_ai_models():
    """获取所有可用的 AI 模型列表"""
    from src.ai.ai_helper import get_available_models
    from src.ai.ai_helper import get_current_model

    models = get_available_models()
    current = get_current_model()

    return jsonify({
        'success': True,
        'current_model': current,
        'models': [
            {
                'key': key,
                'name': config.get('name'),
                'provider': config.get('provider'),
                'model': config.get('model'),
                'has_api_key': bool(config.get('api_key'))
            }
            for key, config in models.items()
        ]
    })


@user_bp.route('/ai/models/<model_key>', methods=['PUT', 'POST'])
def switch_ai_model(model_key):
    """切换 AI 模型"""
    from src.ai.ai_helper import get_available_models, get_ai_instance

    models = get_available_models()
    if model_key not in models:
        return jsonify({
            'success': False,
            'error': f'未知的模型：{model_key}'
        }), 400

    ai = get_ai_instance()
    ai.model_key = model_key
    ai._load_model_config()

    return jsonify({
        'success': True,
        'message': f'已切换到 {models[model_key]["name"]}',
        'current_model': ai.get_current_model_info()
    })


@user_bp.route('/ai/stats', methods=['GET'])
def get_ai_stats():
    """获取 AI 使用统计"""
    from src.ai.ai_helper import get_ai_instance
    ai = get_ai_instance()
    stats = ai.get_ai_stats()
    return jsonify({
        'success': True,
        'stats': stats
    })


@user_bp.route('/notification/settings', methods=['GET'])
def get_notification_settings():
    """获取通知设置"""
    from src.modules.data_manager import get_data_manager
    dm = get_data_manager()
    data = dm.get_data()
    return jsonify({
        'success': True,
        'settings': {
            'pomodoro_complete': data.get('notification_pomodoro', True),
            'goal_reached': data.get('notification_goal', True),
            'task_reminder': data.get('notification_task', True)
        }
    })


@user_bp.route('/notification/settings', methods=['POST'])
def set_notification_settings():
    """设置通知选项"""
    from src.modules.data_manager import get_data_manager
    dm = get_data_manager()
    data = request.json or {}

    settings = {
        'notification_pomodoro': data.get('pomodoro_complete', True),
        'notification_goal': data.get('goal_reached', True),
        'notification_task': data.get('task_reminder', True)
    }

    dm.update_settings(**settings)
    return jsonify({
        'success': True,
        'message': '通知设置已更新',
        'settings': settings
    })


@user_bp.route('/data/export', methods=['GET'])
def export_data():
    """导出所有数据"""
    import zipfile
    import io

    buffer = io.BytesIO()

    try:
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            data_files = [
                'data/buddy_profile.json',
                'data/buddy_memory.json',
                'data/diary.json',
                'data/study_tracker.json',
                'data/ai_history.json',
                'data/tasks.json',
                'data/achievements.json',
            ]

            for file_path in data_files:
                if os.path.exists(file_path):
                    zipf.write(file_path, os.path.basename(file_path))

        buffer.seek(0)

        return send_file(
            buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'studypal_backup_{datetime.now().strftime("%Y%m%d")}.zip'
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@user_bp.route('/status', methods=['GET'])
def get_status():
    """获取当前会话状态"""
    from routes.utils import get_buddy
    buddy = get_buddy()

    return jsonify({
        'emotion': buddy.get_emotion(),
        'emoji': buddy.get_emoji(),
        'emotion_desc': buddy.get_emotion_desc(),
        'stats': buddy.get_study_stats()
    })
