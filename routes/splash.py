"""
StudyPal Splash 页面路由
开屏动效页面，在用户进入应用页之前展示

作者：StudyPal
日期：2026-05-28
"""

from flask import Blueprint, render_template

splash_bp = Blueprint('splash', __name__)


@splash_bp.route('/splash')
def splash():
    """开屏动效页面"""
    return render_template('splash.html')
