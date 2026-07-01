"""
StudyPal AI 模型配置路由
提供预设模型列表、用户自定义模型配置、模型测试等功能

作者：StudyPal
日期：2026-05-25
"""

from flask import Blueprint, jsonify, request
from config import MODELS_CONFIG, DEFAULT_MODEL_KEY
from src.auth.auth import auth_required, auth_optional, get_current_user, AuthService

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


@auth_optional
@ai_model_bp.route('/current', methods=['GET'])
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

    # 使用预设模型
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


@auth_optional
@ai_model_bp.route('/preset', methods=['POST'])
def set_preset_model():
    """切换到预设模型（未登录时仅提示，不写入）"""
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "error": "请先登录后再保存预设模型"}), 401

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


@auth_optional
@ai_model_bp.route('/custom', methods=['POST'])
def set_custom_model():
    """保存用户自定义模型配置（未登录时需要登录）"""
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "error": "请先登录后再保存自定义模型"}), 401

    data = request.json or {}

    base_url = data.get("base_url", "").strip()
    api_key = data.get("api_key", "").strip()
    model = data.get("model", "").strip()
    name = data.get("name", "自定义模型").strip()

    if not base_url:
        return jsonify({"success": False, "error": "API 地址不能为空"}), 400
    if not model:
        return jsonify({"success": False, "error": "模型名称不能为空"}), 400

    # 确保 base_url 格式正确
    if not base_url.startswith(("http://", "https://")):
        base_url = "https://" + base_url
    if base_url.endswith("/"):
        base_url = base_url[:-1]

    # 移除 /v1 后缀（如果有），保留基础地址
    if "/v1" in base_url:
        base_url = base_url.split("/v1")[0]

    # 关键修复：api_key 为空时保留旧的真实 key，避免前端误传脱敏的假 key 把真实 key 覆盖掉
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


@auth_optional
@ai_model_bp.route('/custom', methods=['DELETE'])
def delete_custom_model():
    """删除用户自定义模型配置"""
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "error": "请先登录后再操作"}), 401

    AuthService.update_user(user['id'], {
        'ai_custom_config': None,
        'ai_model_key': DEFAULT_MODEL_KEY
    })

    return jsonify({
        "success": True,
        "message": "已恢复默认设置"
    })


@auth_optional
@ai_model_bp.route('/test', methods=['POST'])
def test_model():
    """测试模型连接（未登录也能用：直接根据前端传入的 api_url/api_key/model 测试）"""
    import requests
    from config import AI_TIMEOUT
    import traceback

    print(f"\n[DEBUG] === /api/ai-model/test Start ===", flush=True)
    try:
        data = request.json or {}
        print(f"[DEBUG] raw payload keys: {list(data.keys())}", flush=True)

        base_url = data.get("base_url", "").strip()
        api_key = data.get("api_key", "").strip()
        model = data.get("model", "").strip()
        print(f"[DEBUG] base_url='{base_url}' model='{model}' key_len={len(api_key)}", flush=True)

        # 关键修复：未提供 api_key 时，若用户已登录且保存过自定义模型，使用保存的 key
        user = get_current_user()
        if not api_key and user:
            existing_cfg = user.get('ai_custom_config') or {}
            if existing_cfg.get('api_key'):
                api_key = existing_cfg['api_key']
                base_url = base_url or existing_cfg.get('base_url', '')
                model = model or existing_cfg.get('model', '')
                print(f"[DEBUG] fallback to user's saved custom config, key_len={len(api_key)}", flush=True)

        if not base_url or not api_key or not model:
            print(f"[DEBUG] missing fields: url={bool(base_url)} key={bool(api_key)} model={bool(model)}", flush=True)
            return jsonify({"success": False, "error": "请填写完整的模型配置"}), 400

        # 格式化 base_url
        if not base_url.startswith(("http://", "https://")):
            base_url = "https://" + base_url
        if base_url.endswith("/"):
            base_url = base_url[:-1]  # 移除末尾斜杠

        # 尝试确定 chat completions 端点
        endpoints_to_try = [
            f"{base_url}/chat/completions",
            f"{base_url}/v1/chat/completions",
        ]

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        test_payload = {
            "model": model,
            "messages": [{"role": "user", "content": "Hello, reply with just 'OK'. Respond in 3 words or less."}],
            "max_tokens": 20,
        }

        for endpoint in endpoints_to_try:
            try:
                print(f"[DEBUG] POST {endpoint} model={model}", flush=True)
                response = requests.post(
                    endpoint,
                    json=test_payload,
                    headers=headers,
                    timeout=AI_TIMEOUT
                )
                print(f"[DEBUG] <- {response.status_code} {response.text[:300]}", flush=True)

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
                    return jsonify({"success": False, "error": "API Key 无效或已过期，请检查设置中的 API 密钥"}), 400
                elif response.status_code == 403:
                    # 细化 403：尝试解析智谱等平台的 error.message
                    err_detail = ""
                    try:
                        err_json = response.json()
                        err_detail = (err_json.get("error", {}) or {}).get("message") or err_json.get("message") or ""
                    except Exception:
                        err_detail = response.text[:200]
                    hint = (
                        "权限被拒绝。可能原因：1) API Key 错误 2) 账户未开通该模型 3) 模型 ID 填写错误。"
                        f" 详情：{err_detail}"
                    )
                    return jsonify({"success": False, "error": hint, "status": 403}), 400
                elif response.status_code == 429:
                    return jsonify({"success": False, "error": "请求过于频繁，请稍后再试（HTTP 429）"}), 400
                elif response.status_code == 404:
                    continue  # 尝试下一个端点
                elif response.status_code >= 500:
                    return jsonify({"success": False, "error": f"AI 服务器错误（HTTP {response.status_code}），请稍后再试"}), 400
                else:
                    try:
                        err = response.json().get("error", {}).get("message", response.text)
                    except:
                        err = response.text
                    return jsonify({"success": False, "error": f"请求失败 ({response.status_code}): {err}"}), 400

            except requests.exceptions.Timeout:
                print(f"[DEBUG] timeout on {endpoint}", flush=True)
                return jsonify({"success": False, "error": "请求超时，请检查网络或更换 API 地址"}), 400
            except requests.exceptions.ConnectionError as e:
                print(f"[DEBUG] connection error on {endpoint}: {e}", flush=True)
                return jsonify({"success": False, "error": "无法连接到服务器，请检查 API 地址是否正确"}), 400
            except Exception as e:
                print(f"[DEBUG] exception on {endpoint}: {e}", flush=True)
                traceback.print_exc()
                return jsonify({"success": False, "error": f"连接失败: {str(e)}"}), 400

        print(f"[DEBUG] no endpoint matched, return 400", flush=True)
        return jsonify({"success": False, "error": "未找到有效的 API 端点，请确认 API 地址"}), 400
    except Exception as e:
        print(f"[DEBUG] outer exception: {type(e).__name__}: {e}", flush=True)
        traceback.print_exc()
        return jsonify({"success": False, "error": f"服务器错误：{str(e)}"}), 500
