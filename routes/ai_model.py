"""
StudyPal AI 模型配置路由
提供预设模型列表、用户自定义模型配置、模型测试等功能

作者：StudyPal
日期：2026-05-25
"""

from flask import Blueprint, jsonify, request
from config import MODELS_CONFIG, DEFAULT_MODEL_KEY
from src.auth.auth import auth_required, get_current_user, AuthService

ai_model_bp = Blueprint('ai_model', __name__, url_prefix='/api/ai-model')


@ai_model_bp.route('/presets', methods=['GET'])
def get_preset_models():
    """获取所有预设模型列表（不含 API Key）"""
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


@ai_model_bp.route('/status', methods=['GET'])
@auth_required
def get_model_status():
    """
    获取模型配置状态（简化版，用于判断是否已配置可用模型）
    """
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "error": "未登录"}), 401

    has_custom = bool(user.get('ai_custom_config'))
    has_preset = bool(user.get('ai_model_key'))
    has_any_config = has_custom or has_preset

    if has_custom:
        config = user['ai_custom_config']
        return jsonify({
            "success": True,
            "configured": True,
            "mode": "custom",
            "name": config.get("name", "自定义模型"),
            "has_api_key": bool(config.get("api_key"))
        })

    if has_preset:
        config = MODELS_CONFIG.get(user['ai_model_key'], {})
        return jsonify({
            "success": True,
            "configured": True,
            "mode": "preset",
            "name": config.get("name", "预设模型"),
            "has_api_key": bool(config.get("api_key"))
        })

    return jsonify({
        "success": True,
        "configured": False,
        "mode": None,
        "message": "请先配置 AI 模型才能使用搭子功能"
    })


@ai_model_bp.route('/current', methods=['GET'])
@auth_required
def get_current_model():
    """获取用户当前使用的模型配置"""
    user = get_current_user()

    # 用户设置了自定义模型
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

    # 无自定义配置时，返回系统默认模型
    config = MODELS_CONFIG.get(DEFAULT_MODEL_KEY, {})
    return jsonify({
        "success": True,
        "mode": "default",
        "model": {
            "name": config.get("name", "系统默认模型"),
            "provider": config.get("provider", "openai"),
            "model": config.get("model", ""),
            "base_url": config.get("base_url", ""),
        },
        "model_key": DEFAULT_MODEL_KEY
    })


@ai_model_bp.route('/preset', methods=['POST'])
@auth_required
def set_preset_model():
    """切换到预设模型"""
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "error": "未登录"}), 401

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
@auth_required
def set_custom_model():
    """保存用户自定义模型配置"""
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "error": "未登录"}), 401

    data = request.json or {}

    base_url = data.get("base_url", "").strip()
    api_key = data.get("api_key", "").strip()
    model = data.get("model", "").strip()
    name = data.get("name", "自定义模型").strip()

    if not base_url:
        return jsonify({"success": False, "error": "API 地址不能为空"}), 400
    if not api_key:
        return jsonify({"success": False, "error": "API Key 不能为空"}), 400
    if not model:
        return jsonify({"success": False, "error": "模型名称不能为空"}), 400

    # 确保 base_url 格式正确
    if not base_url.startswith(("http://", "https://")):
        base_url = "http://" + base_url
    base_url = base_url.rstrip('/')
    # 去掉 /v1 后缀（如果有），保留基础地址
    if base_url.endswith('/v1'):
        base_url = base_url[:-3]

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
@auth_required
def delete_custom_model():
    """删除用户自定义模型配置"""
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "error": "未登录"}), 401

    AuthService.update_user(user['id'], {
        'ai_custom_config': None,
        'ai_model_key': DEFAULT_MODEL_KEY
    })

    return jsonify({
        "success": True,
        "message": "已恢复默认设置"
    })


@ai_model_bp.route('/test', methods=['POST'])
@auth_required
def test_model():
    """测试模型连接"""
    import requests
    from config import AI_TIMEOUT

    data = request.json or {}
    base_url = data.get("base_url", "").strip()
    api_key = data.get("api_key", "").strip()
    model = data.get("model", "").strip()

    if not base_url or not api_key or not model:
        return jsonify({"success": False, "error": "请填写完整的模型配置"}), 400

    # 格式化 base_url，去掉协议前缀和尾部斜杠
    if not base_url.startswith(("http://", "https://")):
        base_url = "http://" + base_url
    base_url = base_url.rstrip('/')

    # 去掉 /v1 或 /v1/ 后缀（如果有），保留基础地址
    if base_url.endswith('/v1'):
        base_url = base_url[:-3]

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    test_payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Hello, reply with just 'OK'. Respond in 3 words or less."}],
        "max_tokens": 20,
    }

    # 尝试多个可能的端点
    endpoints_to_try = [
        f"{base_url}/v1/chat/completions",
        f"{base_url}/chat/completions",
    ]

    tried_urls = []
    for endpoint in endpoints_to_try:
        tried_urls.append(endpoint)
        try:
            response = requests.post(
                endpoint,
                json=test_payload,
                headers=headers,
                timeout=AI_TIMEOUT
            )

            if response.status_code == 200:
                result = response.json()
                reply = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                return jsonify({
                    "success": True,
                    "message": "连接成功",
                    "endpoint": endpoint,
                    "test_reply": reply[:100]
                })
            elif response.status_code == 401:
                return jsonify({"success": False, "error": "API Key 无效，请检查"}), 400
            elif response.status_code == 403:
                return jsonify({"success": False, "error": "API 拒绝访问（权限不足）"}), 400
            elif response.status_code == 404:
                continue  # 尝试下一个端点
            else:
                try:
                    err = response.json().get("error", {}).get("message", response.text)
                except:
                    err = response.text
                return jsonify({"success": False, "error": f"请求失败 ({response.status_code}): {err}"}), 400

        except requests.exceptions.Timeout:
            continue
        except requests.exceptions.ConnectionError:
            continue
        except Exception as e:
            return jsonify({"success": False, "error": f"连接失败: {str(e)}"}), 400

    # 所有端点都失败了
    if tried_urls:
        return jsonify({
            "success": False,
            "error": f"无法连接到 API，请检查地址是否可访问（尝试过: {', '.join(tried_urls)}）"
        }), 400
    return jsonify({"success": False, "error": "连接失败"}), 400


@ai_model_bp.route('/proxy/chat', methods=['GET'])
@auth_required
def proxy_chat():
    """
    AI 代理端点：Flask 只返回模型配置，实际请求由浏览器直发。
    解决 Flask 后端无法访问内网 IP 的问题。
    """
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "error": "未登录"}), 401

    # 用户有自定义模型配置
    if user.get('ai_custom_config'):
        config = user['ai_custom_config']
        return jsonify({
            "success": True,
            "mode": "custom",
            "base_url": config.get("base_url", ""),
            "api_key": config.get("api_key", ""),
            "model": config.get("model", ""),
        })

    # 预设模型
    model_key = user.get('ai_model_key', DEFAULT_MODEL_KEY)
    config = MODELS_CONFIG.get(model_key, MODELS_CONFIG.get(DEFAULT_MODEL_KEY, {}))
    return jsonify({
        "success": True,
        "mode": "preset",
        "base_url": config.get("base_url", ""),
        "api_key": config.get("api_key", ""),
        "model": config.get("model", ""),
    })


@ai_model_bp.route('/proxy/save', methods=['POST'])
@auth_required
def proxy_save():
    """
    保存 AI 对话消息到后端历史记录。
    浏览器直调 AI 后，调用此接口保存历史。
    """
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "error": "未登录"}), 401

    data = request.json or {}
    role = data.get("role")  # "user" 或 "assistant"
    content = data.get("content", "")
    conversation_id = data.get("conversation_id")

    if role not in ("user", "assistant") or not content:
        return jsonify({"success": False, "error": "参数错误"}), 400

    from src.modules.ai_memory import get_ai_memory
    ai_memory = get_ai_memory()
    ai_memory.add_message(role, content, conversation_id)

    return jsonify({"success": True})
