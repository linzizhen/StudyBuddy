"""
StudyPal Web 应用入口
使用 Flask + Blueprint 架构

作者：StudyPal
创建日期：2026-04-13
重构日期：2026-04-30 v2.1（安全加固）
"""

from flask import Flask, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import os
import secrets
import logging

# 加载环境变量
load_dotenv()

logger = logging.getLogger(__name__)

# ==================== Flask 应用 ====================

app = Flask(__name__)

# 安全配置：从环境变量读取，无则自动生成
app.secret_key = os.getenv('SECRET_KEY') or secrets.token_hex(32)

# CORS 配置
cors_origins = os.getenv('CORS_ORIGINS', '*')
CORS(app, resources={r"/api/*": {"origins": cors_origins}})

# ==================== 基础路由 ====================

@app.route('/')
def index():
    """主页 - 渲染 splash 介绍页（自动跳到 /app）"""
    return render_template('index.html')


@app.route('/app')
@app.route('/dashboard')
def app_page():
    """应用主页 - 三栏 Dashboard"""
    return render_template('dashboard.html')

# ==================== Blueprint 路由注册 ====================

from routes import register_blueprints

# 注册所有 Blueprint（包含 settings_bp）
register_blueprints(app)

# ==================== 模型配置测试代理（无需登录，避免CORS）====================

@app.route('/api/model/test', methods=['POST'])
def test_model_connection():
    """接收前端表单数据，转发到AI服务商，返回真实响应"""
    from flask import request
    import requests as req_lib

    data = request.json or {}
    api_url = data.get('apiUrl', '').strip()
    api_key = data.get('apiKey', '').strip()
    model_name = data.get('modelName', '').strip()

    if not api_url or not api_key or not model_name:
        return {'error': 'API地址、API Key 和模型名称 均不能为空'}, 400

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
    }

    payload = {
        'model': model_name,
        'messages': [{'role': 'user', 'content': '你好'}],
        'max_tokens': 50,
    }

    try:
        resp = req_lib.post(
            api_url,
            json=payload,
            headers=headers,
            timeout=25,
            proxies={'http': None, 'https': None}
        )
        if resp.status_code == 200:
            result = resp.json()
            reply = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            return {'success': True, 'reply': reply}
        elif resp.status_code == 401:
            return {'error': 'API Key 无效，请检查是否正确'}, 400
        elif resp.status_code == 403:
            return {'error': 'API 拒绝访问（权限不足）'}, 400
        elif resp.status_code == 404:
            return {'error': 'API 地址不正确（404 Not Found），请检查地址是否包含完整路径'}, 400
        else:
            try:
                err = resp.json().get('error', {}).get('message', resp.text)
            except:
                err = resp.text
            return {'error': f'请求失败 ({resp.status_code}): {err}'}, 400
    except req_lib.exceptions.Timeout:
        return {'error': '请求超时，请检查网络或API地址'}, 400
    except req_lib.exceptions.ConnectionError as e:
        return {'error': f'无法连接到服务器，请检查API地址是否正确: {str(e)[:100]}'}, 400
    except Exception as e:
        return {'error': f'连接失败: {str(e)[:150]}'}, 400


@app.route('/api/persona/chat', methods=['POST'])
def persona_chat():
    """自定义搭子对话：接收前端传递的 systemPrompt + modelId，直接调用 AI 并返回结果

    请求体: { systemPrompt, modelId, modelConfig: {apiUrl,apiKey,modelName}, messages: [{role,content}..] }
    返回:   { success, reply, conversationId }
    """
    import req_lib as requests
    from flask import request

    data = request.json or {}
    system_prompt = data.get('systemPrompt', '').strip()
    model_config = data.get('modelConfig', {})
    chat_history = data.get('messages', [])

    api_url = model_config.get('apiUrl', '').strip()
    api_key = model_config.get('apiKey', '').strip()
    model_name = model_config.get('modelName', '').strip()

    if not system_prompt:
        return {'success': False, 'error': '人格设定不能为空'}, 400
    if not api_url or not api_key or not model_name:
        return {'success': False, 'error': '模型配置不完整'}, 400

    # 构建 messages：system + 历史
    messages = [{'role': 'system', 'content': system_prompt}]
    messages += [m for m in chat_history if isinstance(m, dict) and m.get('role') in ('user', 'assistant')]

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
    }
    payload = {
        'model': model_name,
        'messages': messages,
        'max_tokens': 500,
    }

    try:
        resp = requests.post(
            api_url,
            json=payload,
            headers=headers,
            timeout=25,
            proxies={'http': None, 'https': None}
        )
        if resp.status_code == 200:
            result = resp.json()
            reply = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            return {'success': True, 'reply': reply or '（无回复内容）'}
        elif resp.status_code == 401:
            return {'success': False, 'error': 'API Key 无效'}, 400
        elif resp.status_code == 403:
            return {'success': False, 'error': 'API 拒绝访问'}, 400
        elif resp.status_code == 404:
            return {'success': False, 'error': 'API 地址不正确（404）'}, 400
        else:
            try:
                err = resp.json().get('error', {}).get('message', resp.text)
            except:
                err = resp.text
            return {'success': False, 'error': f'请求失败 ({resp.status_code}): {err[:100]}'}, 400
    except requests.exceptions.Timeout:
        return {'success': False, 'error': '请求超时'}, 400
    except requests.exceptions.ConnectionError as e:
        return {'success': False, 'error': f'无法连接到服务器: {str(e)[:80]}'}, 400
    except Exception as e:
        return {'success': False, 'error': f'连接失败: {str(e)[:100]}'}, 400


# ==================== 应用启动 ====================

if __name__ == '__main__':
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('PORT', 5000))

    if debug:
        logger.warning("=" * 50)
        logger.warning("Flask running in DEBUG mode - do NOT use in production!")
        logger.warning("Set FLASK_DEBUG=False for production")
        logger.warning("=" * 50)

    app.run(debug=debug, port=port, host='0.0.0.0')
