"""
StudyPal Web 应用入口 v3.0
完整版 - JSON 数据存储 + 统一服务层

作者：StudyPal
创建日期：2026-04-13
重构日期：2026-05-25 v3.1（数据层重构）
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 安全配置
app.secret_key = os.getenv('SECRET_KEY') or os.urandom(32)

# CORS 配置
cors_origins = os.getenv('CORS_ORIGINS', '*')
CORS(app, resources={r"/api/*": {"origins": cors_origins, "supports_credentials": True}})

# 确保数据目录存在
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)


# ==================== 注册蓝图 ====================

def register_blueprints(app):
    """注册所有 Blueprint"""
    try:
        from routes import register_blueprints as reg_user_routes
        reg_user_routes(app)
    except Exception as e:
        logger.warning(f"路由注册失败: {e}")

    # 认证路由
    try:
        from src.routes.auth_routes import auth_bp
        app.register_blueprint(auth_bp)
    except Exception as e:
        logger.warning(f"认证路由注册失败: {e}")

    try:
        from routes.ai_model import ai_model_bp
        app.register_blueprint(ai_model_bp)
    except Exception as e:
        logger.warning(f"AI模型路由注册失败: {e}")


# ==================== 基础路由 ====================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login_page():
    return render_template('auth/login.html')


@app.route('/register')
def register_page():
    return render_template('auth/register.html')


@app.route('/admin')
def admin_page():
    return render_template('admin/index.html')


# ==================== 健康检查 ====================

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'version': '3.0.0',
        'environment': os.getenv('FLASK_ENV', 'production')
    })


# ==================== 错误处理 ====================

@app.errorhandler(404)
def not_found(error):
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': '资源不存在'}), 404
    return render_template('index.html')


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"服务器错误: {error}")
    return jsonify({'success': False, 'error': '服务器内部错误'}), 500


@app.errorhandler(429)
def ratelimit_handler(error):
    return jsonify({'success': False, 'error': '请求过于频繁'}), 429


# ==================== 注册蓝图 ====================

register_blueprints(app)


# ==================== 应用启动 ====================

if __name__ == '__main__':
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('PORT', 5000))

    logger.info(f"=" * 50)
    logger.info(f"StudyPal v3.0 启动中...")
    logger.info(f"访问地址: http://localhost:{port}")
    logger.info(f"=" * 50)

    app.run(debug=debug, port=port, host='0.0.0.0')
