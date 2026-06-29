"""
StudyPal 学习打卡路由
处理学习计时、统计相关 API
"""

from flask import Blueprint, jsonify, request

study_bp = Blueprint('study', __name__, url_prefix='/api/study')


def get_buddy():
    """获取 Buddy 实例"""
    from src.core.buddy import get_buddy
    return get_buddy()


@study_bp.route('/start', methods=['POST'])
def start_study():
    """开始学习"""
    buddy = get_buddy()
    data = request.json or {}
    subject = data.get('subject', '学习')

    success = buddy.start_study(subject)
    if success:
        return jsonify({
            'success': True,
            'message': f'开始学习 {subject}',
            'is_studying': True,
            'emotion': buddy.get_emotion(),
            'emoji': buddy.get_emoji()
        })

    return jsonify({
        'success': False,
        'message': '已经在学习中啦'
    })


@study_bp.route('/stop', methods=['POST'])
def stop_study():
    """结束学习"""
    buddy = get_buddy()
    data = request.json or {}
    subject = data.get('subject', '学习')

    duration = buddy.stop_study(subject)
    return jsonify({
        'success': True,
        'duration': duration,
        'message': f'学习了 {int(duration)} 分钟',
        'emotion': buddy.get_emotion(),
        'emoji': buddy.get_emoji()
    })


@study_bp.route('/stats', methods=['GET'])
def get_study_stats():
    """获取学习统计"""
    buddy = get_buddy()
    stats = buddy.get_study_status()

    return jsonify({
        'success': True,
        'stats': stats
    })
