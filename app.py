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
import socket
import requests

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

    if not api_url or not model_name:
        return {'error': 'API地址 和 模型名称 均不能为空'}, 400

    # 检测是否为 Ollama（端口 11434 或包含 /api）
    is_ollama = '11434' in api_url or api_url.endswith('/api')

    if is_ollama:
        # Ollama 格式
        endpoint = api_url.rstrip('/') + '/api/chat'
        headers = {'Content-Type': 'application/json'}
        payload = {
            'model': model_name,
            'messages': [{'role': 'user', 'content': '你好'}],
            'stream': False,
        }
    else:
        # OpenAI 兼容格式（如智谱、DeepSeek 等）
        if '/chat/completions' not in api_url:
            api_url = api_url.rstrip('/') + '/chat/completions'
        endpoint = api_url
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}' if api_key else '',
        }
        payload = {
            'model': model_name,
            'messages': [{'role': 'user', 'content': '你好'}],
            'max_tokens': 50,
        }

    try:
        resp = req_lib.post(
            endpoint,
            json=payload,
            headers=headers,
            timeout=60,
            proxies={'http': None, 'https': None}
        )
        if resp.status_code == 200:
            result = resp.json()
            if is_ollama:
                # Ollama 响应格式
                reply = result.get('message', {}).get('content', '')
            else:
                # OpenAI 响应格式
                reply = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            return {'success': True, 'reply': reply}
        elif resp.status_code == 401:
            return {'error': 'API Key 无效，请检查是否正确'}, 400
        elif resp.status_code == 403:
            return {'error': 'API 拒绝访问（权限不足）'}, 400
        elif resp.status_code == 400:
            try:
                err_data = resp.json()
                err = err_data.get('error', {}).get('message', err_data.get('error', resp.text))
            except:
                err = resp.text
            # 如果是模型名称错误，给出更友好的提示
            if 'model' in err.lower() or 'invalid' in err.lower():
                return {'error': f'模型名称不存在，请检查是否已在 Ollama 中安装 (ollama pull 模型名)'}, 400
            return {'error': f'请求失败 ({resp.status_code}): {err}'}, 400
        else:
            try:
                err = result.get('error', {}).get('message', resp.text) if 'result' in dir() else resp.text
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
    import logging
    logger = logging.getLogger('app')
    from flask import request

    data = request.json or {}
    system_prompt = data.get('systemPrompt', '').strip()
    model_config = data.get('modelConfig', {})
    chat_history = data.get('messages', [])

    api_url = model_config.get('apiUrl', '').strip()
    api_key = model_config.get('apiKey', '').strip()
    model_name = model_config.get('modelName', '').strip()

    # 归一化 API URL：自动补全 /chat/completions 后缀
    if api_url:
        normalized = api_url.rstrip('/')
        # 已知不需要补全的路径模式
        skip_suffixes = ('/chat/completions', '/v1/chat/completions', '/chat/completions/')
        if not any(normalized.endswith(s) for s in skip_suffixes):
            normalized += '/chat/completions'
        api_url = normalized

    logger.info(f"[persona_chat] systemPrompt长度={len(system_prompt)}, api_url={api_url}, model_name={model_name}")

    if not system_prompt:
        return {'success': False, 'error': '人格设定不能为空，请先在搭子设计器中填写'}, 400
    if not api_url or not api_key or not model_name:
        return {'success': False, 'error': '模型配置不完整，请在搭子设计器中绑定有效模型'}, 400

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
    logger.info(f"[persona_chat] 即将调用AI, messages数量={len(messages)}, 前3条: {[m.get('role')+':'+m.get('content','')[:30] for m in messages[:3]]}")

    try:
        resp = requests.post(
            api_url,
            json=payload,
            headers=headers,
            timeout=25,
            proxies={'http': None, 'https': None}
        )
        logger.info(f"[persona_chat] AI响应状态码={resp.status_code}, body前200: {resp.text[:200]}")
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

def get_lan_ip():
    """获取本机局域网IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None


def print_startup_info(host, port, debug):
    """启动时打印访问信息"""
    print("\n" + "=" * 50)
    print("  StudyPal 服务已启动")
    print("=" * 50)
    print(f"  本地访问: http://127.0.0.1:{port}")
    lan_ip = get_lan_ip()
    if lan_ip:
        print(f"  局域网访问: http://{lan_ip}:{port}")
    if debug:
        print("\n  [警告] Debug 模式已开启 - 生产环境请设置 FLASK_DEBUG=False")
    print("=" * 50 + "\n")


if __name__ == '__main__':
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('PORT', 5000))
    host = '0.0.0.0'

    print_startup_info(host, port, debug)
    app.run(debug=debug, port=port, host=host)
