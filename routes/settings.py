"""
StudyPal 设置路由
处理模型配置等 API
"""

from flask import Blueprint, jsonify, request
import os
import json

settings_bp = Blueprint('settings', __name__)

# 模型配置文件路径
MODEL_CONFIG_FILE = 'data/model_config.json'


def _load_model_config():
    """从文件加载模型配置"""
    if os.path.exists(MODEL_CONFIG_FILE):
        try:
            with open(MODEL_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {
        'provider': os.getenv('AI_PROVIDER', 'openai'),
        'model': os.getenv('AI_MODEL', 'gpt-3.5-turbo'),
        'temperature': float(os.getenv('AI_TEMPERATURE', '0.7')),
        'max_tokens': int(os.getenv('AI_MAX_TOKENS', '2000')),
    }


def _save_model_config(config):
    """保存模型配置到文件"""
    os.makedirs(os.path.dirname(MODEL_CONFIG_FILE), exist_ok=True)
    with open(MODEL_CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


@settings_bp.route('/api/model/config', methods=['GET'])
def get_model_config():
    """获取AI模型配置"""
    config = _load_model_config()
    return jsonify({
        'success': True,
        'config': {
            'provider': config.get('provider', 'openai'),
            'model': config.get('model', 'gpt-3.5-turbo'),
            'temperature': config.get('temperature', 0.7),
            'max_tokens': config.get('max_tokens', 2000),
        }
    })


@settings_bp.route('/api/model/config', methods=['POST'])
def update_model_config():
    """更新AI模型配置"""
    data = request.json or {}
    config = {
        'provider': data.get('provider', 'openai'),
        'model': data.get('model', 'gpt-3.5-turbo'),
        'temperature': float(data.get('temperature', 0.7)),
        'max_tokens': int(data.get('max_tokens', 2000)),
    }
    _save_model_config(config)
    return jsonify({'success': True, 'message': '配置已保存', 'config': config})
