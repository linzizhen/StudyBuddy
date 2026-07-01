"""
StudyPal AI 模型配置路由
提供预设模型列表、用户自定义模型配置、模型测试等功能

作者：StudyPal
日期：2026-05-25
"""

from flask import Blueprint, jsonify, request, g
from config import MODELS_CONFIG, DEFAULT_MODEL_KEY
from src.auth.auth import AuthService
import time

ai_model_bp = Blueprint('ai_model', __name__, url_prefix='/api/ai-model')


# ---------- 内联认证工具函数 ----------
def _get_current_user():
    """从 Authorization 头解析用户，与 @auth_optional 等效"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    token = auth_header[7:]
    from src.auth.auth import _verify_token
    user_id = _verify_token(token)
    if not user_id:
        return None
    return AuthService.get_user_by_id(user_id)


def _get_or_create_guest_user():
    """获取或创建游客用户（用于无登录保存）"""
    from src.auth.auth import _load_users, _save_users
    users = _load_users()
    if users:
        for user in users.values():
            return user
    import uuid
    guest = {
        'id': int(time.time()),
        'email': 'local_guest@study',
        'password_hash': '',
        'nickname': '游客',
        'token': '',
        'ai_model_key': None,
        'ai_custom_config': None,
        'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'ai_calls': 0
    }
    users['local_guest@study'] = guest
    _save_users(users)
    return guest


# ---------- 路由定义 ----------
@ai_model_bp.route('/presets', methods=['GET'])
def get_preset_models():
    presets = []
    for key, config in MODELS_CONFIG.items():
        presets.append({
            "key": key,
            "name": config.get("name", key),
            "provider": config.get("provider", "openai"),
            "model": config.get("model", ""),
            "base_url": config.get("base_url", ""),
        })
    return jsonify({
        "success": True,
        "presets": presets,
        "default_key": DEFAULT_MODEL_KEY
    })


@ai_model_bp.route('/current', methods=['GET'])
def get_current_model():
    """获取用户当前使用的模型配置（未登录时返回第一个用户的）"""
    user = _get_current_user()
    if not user:
        users = _load_users()
        if users:
            for u in users.values():
                user = u
                break
        if not user:
            return jsonify({"success": True, "mode": "preset", "model_key": DEFAULT_MODEL_KEY}), 200

    if user and user.get('ai_custom_config'):
        return jsonify({
            "success": True,
            "mode": "custom",
            "model": {
                "name": user.get('ai_custom_config', {}).get("name", "自定义模型"),
                "base_url": user.get('ai_custom_config', {}).get("base_url", ""),
                "model": user.get('ai_custom_config', {}).get("model", ""),
                "api_key": "****" if user.get('ai_custom_config', {}).get("api_key") else "",
            },
            "model_key": user.get('ai_model_key')
        })

    model_key = user.get('ai_model_key') if user else None or DEFAULT_MODEL_KEY
    config = MODELS_CONFIG.get(model_key, MODELS_CONFIG.get(DEFAULT_MODEL_KEY, {}))

    return jsonify({
        "success": True,
        "mode": "preset",
        "model": {
            "name": config.get("name", model_key),
            "provider": config.get("provider", "openai"),
            "model": config.get("model", ""),
            "base_url": config.get("base_url", ""),
        },
        "model_key": model_key
    })


@ai_model_bp.route('/preset', methods=['POST'])
def set_preset_model():
    """切换到预设模型（未登录时写入游客用户）"""
    user = _get_current_user()
    if not user:
        user = _get_or_create_guest_user()

    data = request.json or {}
    model_key = data.get("model_key", "")

    if model_key and model_key not in MODELS_CONFIG:
        return jsonify({"success": False, "error": "无效的模型"}), 400

    AuthService.update_user(user['id'], {
        'ai_model_key': model_key or None,
        'ai_custom_config': None
    })

    return jsonify({
        "success": True,
        "message": "模型已切换",
        "model_key": model_key,
        "mode": "preset"
    })


@ai_model_bp.route('/custom', methods=['POST'])
def set_custom_model():
    """保存用户自定义模型配置（未登录时写入游客用户）"""
    user = _get_current_user()
    if not user:
        user = _get_or_create_guest_user()

    data = request.json or {}

    base_url = data.get("base_url", "").strip()
    api_key = data.get("api_key", "").strip()
    model = data.get("model", "").strip()
    name = data.get("name", "自定义模型").strip()

    if not base_url:
        return jsonify({"success": False, "error": "API 地址不能为空"}), 400
    if not model:
        return jsonify({"success": False, "error": "模型名称不能为空"}), 400

    if not base_url.startswith(("http://", "https://")):
        base_url = "https://" + base_url
    if base_url.endswith("/"):
        base_url = base_url[:-1]
    if "/v1" in base_url:
        base_url = base_url.split("/v1")[0]

    if not api_key:
        existing_cfg = user.get('ai_custom_config') or {}
        api_key = existing_cfg.get('api_key', '')

    if not api_key:
        return jsonify({"success": False, "error": "API Key 不能为空（首次保存需要输入）"}), 400

    AuthService.update_user(user['id'], {
        'ai_custom_config': {
            "name": name,
            "base_url": base_url,
            "api_key": api_key,
            "model": model,
        },
        'ai_model_key': None
    })

    return jsonify({
        "success": True,
        "message": "自定义模型已保存",
        "mode": "custom",
        "model": {
            "name": name,
            "base_url": base_url,
            "model": model,
        }
    })


@ai_model_bp.route('/custom', methods=['DELETE'])
def delete_custom_model():
    """删除用户自定义模型配置"""
    user = _get_current_user()
    if not user:
        user = _get_or_create_guest_user()

    AuthService.update_user(user['id'], {
        'ai_custom_config': None,
        'ai_model_key': DEFAULT_MODEL_KEY
    })

    return jsonify({
        "success": True,
        "message": "已恢复默认设置"
    })


@ai_model_bp.route('/test', methods=['POST'])
def test_model():
    """测试模型连接（未登录也能用：直接根据前端传入的 api_url/api_key/model 测试）"""
    import requests
    from config import AI_TIMEOUT
    import traceback

    sess = requests.Session()
    sess.trust_env = False

    try:
        data = request.json or {}
        base_url = data.get("base_url", "").strip()
        api_key = data.get("api_key", "").strip()
        model = data.get("model", "").strip()

        user = _get_current_user()
        if not api_key and user:
            existing_cfg = user.get('ai_custom_config') or {}
            if existing_cfg.get('api_key'):
                api_key = existing_cfg['api_key']
                base_url = base_url or existing_cfg.get('base_url', '')
                model = model or existing_cfg.get('model', '')

        if not base_url or not api_key or not model:
            return jsonify({"success": False, "error": "请填写完整的模型配置"}), 400

        if not base_url.startswith(("http://", "https://")):
            base_url = "https://" + base_url
        if base_url.endswith("/"):
            base_url = base_url[:-1]
        if base_url.endswith("/v1"):
            base_url = base_url[:-3]

        api_url = f"{base_url}/chat/completions"

        resp = sess.post(
            api_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": "Hi"}],
                "max_tokens": 5
            },
            timeout=AI_TIMEOUT
        )

        if resp.status_code == 200:
            return jsonify({"success": True, "message": "连接成功"})
        elif resp.status_code == 401:
            return jsonify({"success": False, "error": "认证失败，请检查 API Key"}), 401
        elif resp.status_code == 403:
            return jsonify({"success": False, "error": "访问被拒绝，可能 API Key 没有权限"}), 403
        else:
            err_msg = "未知错误"
            try:
                err_data = resp.json()
                err_msg = err_data.get('error', {}).get('message', err_data.get('error', str(resp.status_code)))
            except:
                err_msg = resp.text[:200] if resp.text else str(resp.status_code)
            return jsonify({"success": False, "error": f"请求失败 ({resp.status_code}): {err_msg}"}), 502

    except requests.exceptions.Timeout:
        return jsonify({"success": False, "error": "连接超时，请检查 API 地址和网络"}), 504
    except requests.exceptions.SSLError as e:
        return jsonify({"success": False, "error": f"SSL 证书错误: {str(e)[:100]}"}), 502
    except Exception as e:
        tb = traceback.format_exc()
        return jsonify({"success": False, "error": f"连接失败: {str(e)[:200]}"}), 500
