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
