"""
StudyPal Web 应用入口 v3.0
使用 Flask + SQLAlchemy + JWT 认证

作者：StudyPal
创建日期：2026-04-13
重构日期：2026-05-21 v3.0（商业化版本）
"""

from flask import Flask, render_template, jsonify
from flask_cors import CORS
from flask_login import LoginManager
from dotenv import load_dotenv
import os
import logging

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== Flask 应用 ====================

app = Flask(__name__)

# 安全配置
app.secret_key = os.getenv('SECRET_KEY') or os.urandom(32)

# 数据库配置
database_url = os.getenv('DATABASE_URL', 'sqlite:///studypal.db')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,  # 连接前测试
    'pool_recycle': 300,   # 5分钟回收连接
}

# JWT 配置
app.config['JWT_EXPIRATION_HOURS'] = int(os.getenv('JWT_EXPIRATION_HOURS', 24))

# CORS 配置
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000')
CORS(app, resources={
    r"/api/*": {
        "origins": cors_origins.split(','),
        "supports_credentials": True
    }
})

# 初始化扩展
from src.models.models import db, init_db
db.init_app(app)

# 初始化 Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    from src.models.models import User
    return User.query.get(int(user_id))

# ==================== 注册蓝图 ====================

def register_blueprints(app):
    """注册所有蓝图"""
    # 认证路由
    from src.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp)

    # 用户路由
    from routes import register_blueprints as reg_user_routes
    reg_user_routes(app)

# ==================== 基础路由 ====================

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/login')
def login_page():
    """登录页"""
    return render_template('auth/login.html')


@app.route('/register')
def register_page():
    """注册页"""
    return render_template('auth/register.html')


@app.route('/admin')
def admin_page():
    """管理后台"""
    return render_template('admin/index.html')


# ==================== 健康检查 ====================

@app.route('/api/health')
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'version': '3.0.0',
        'environment': os.getenv('FLASK_ENV', 'production')
    })


# ==================== 错误处理 ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': '资源不存在'}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"服务器错误: {error}")
    return jsonify({'success': False, 'error': '服务器内部错误'}), 500


@app.errorhandler(429)
def ratelimit_handler(error):
    return jsonify({'success': False, 'error': '请求过于频繁，请稍后再试'}), 429


# ==================== 应用启动 ====================

def init_app():
    """初始化应用"""
    with app.app_context():
        # 初始化数据库
        db.create_all()

        # 创建测试数据
        from src.models.models import User
        if not User.query.first():
            logger.info("创建初始数据...")

        logger.info("应用初始化完成")


if __name__ == '__main__':
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    # 初始化数据库
    init_app()

    if debug:
        logger.warning("=" * 50)
        logger.warning("Flask running in DEBUG mode")
        logger.warning("=" * 50)

    port = int(os.getenv('PORT', 5000))
    app.run(debug=debug, port=port, host='0.0.0.0')
