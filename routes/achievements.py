"""
StudyPal 成就路由
处理成就徽章相关 API
"""

from flask import Blueprint, jsonify, request

achievements_bp = Blueprint('achievements', __name__, url_prefix='/api/achievements')


@achievements_bp.route('', methods=['GET'])
def get_achievements():
    """获取用户成就"""
    from src.modules.achievements import get_achievements_data
    data = get_achievements_data()
    return jsonify({
        'success': True,
        **data
    })


@achievements_bp.route('/unlock', methods=['POST'])
def unlock_achievement():
    """解锁成就"""
    from src.modules.achievements import unlock_achievement as do_unlock
    data = request.json or {}
    achievement_id = data.get('achievement_id')

    if not achievement_id:
        return jsonify({'success': False, 'error': '成就ID不能为空'}), 400

    if do_unlock(achievement_id):
        return jsonify({'success': True, 'message': '成就解锁！'})
    return jsonify({'success': False, 'message': '成就已存在'}), 400
