"""
StudyPal 时间线路由
处理考研历程时间线相关 API
"""

from flask import Blueprint, jsonify, request
from typing import Dict, Any

timeline_bp = Blueprint('timeline', __name__, url_prefix='/api/timeline')


def get_timeline():
    """获取 Timeline 实例"""
    from src.modules.timeline import get_timeline
    return get_timeline()


@timeline_bp.route('', methods=['GET'])
def get_timeline_events():
    """获取时间线事件列表"""
    timeline = get_timeline()

    event_type = request.args.get('type')
    limit = request.args.get('limit', 50, type=int)
    start_date = request.args.get('start')
    end_date = request.args.get('end')

    events = timeline.get_events(
        event_type=event_type,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )

    stats = timeline.get_stats()

    return jsonify({
        'success': True,
        'events': events,
        'stats': stats
    })


@timeline_bp.route('', methods=['POST'])
def add_timeline_event():
    """添加时间线事件"""
    timeline = get_timeline()
    data = request.json or {}

    event_id = timeline.add_event(
        event_type=data.get('type', 'milestone'),
        title=data.get('title', ''),
        description=data.get('description', ''),
        emotion=data.get('emotion', ''),
        tags=data.get('tags', []),
        metadata=data.get('metadata', {}),
        date=data.get('date')
    )

    return jsonify({
        'success': True,
        'event_id': event_id
    })


@timeline_bp.route('/stats', methods=['GET'])
def get_timeline_stats():
    """获取时间线统计"""
    timeline = get_timeline()
    stats = timeline.get_stats()

    return jsonify({
        'success': True,
        'stats': stats
    })


@timeline_bp.route('/<event_id>', methods=['DELETE'])
def delete_timeline_event(event_id):
    """删除时间线事件"""
    timeline = get_timeline()
    success = timeline.delete_event(event_id)

    return jsonify({
        'success': success
    })


# ========== 便捷记录接口 ==========

@timeline_bp.route('/record/study_start', methods=['POST'])
def record_study_start():
    """记录开始学习"""
    timeline = get_timeline()
    data = request.json or {}

    event_id = timeline.record_study_start(
        subject=data.get('subject', '备考')
    )

    return jsonify({
        'success': True,
        'event_id': event_id
    })


@timeline_bp.route('/record/milestone', methods=['POST'])
def record_milestone():
    """记录里程碑"""
    timeline = get_timeline()
    data = request.json or {}

    event_id = timeline.record_milestone(
        title=data.get('title', ''),
        description=data.get('description', ''),
        emotion=data.get('emotion', '')
    )

    return jsonify({
        'success': True,
        'event_id': event_id
    })


@timeline_bp.route('/record/achievement', methods=['POST'])
def record_achievement():
    """记录成就"""
    timeline = get_timeline()
    data = request.json or {}

    event_id = timeline.record_achievement(
        achievement_name=data.get('name', ''),
        description=data.get('description', '')
    )

    return jsonify({
        'success': True,
        'event_id': event_id
    })


@timeline_bp.route('/record/struggle', methods=['POST'])
def record_struggle():
    """记录困难时刻"""
    timeline = get_timeline()
    data = request.json or {}

    event_id = timeline.record_struggle(
        title=data.get('title', ''),
        description=data.get('description', ''),
        emotion=data.get('emotion', '')
    )

    return jsonify({
        'success': True,
        'event_id': event_id
    })


@timeline_bp.route('/record/breakthrough', methods=['POST'])
def record_breakthrough():
    """记录突破"""
    timeline = get_timeline()
    data = request.json or {}

    event_id = timeline.record_breakthrough(
        title=data.get('title', ''),
        description=data.get('description', ''),
        subject=data.get('subject', '')
    )

    return jsonify({
        'success': True,
        'event_id': event_id
    })


@timeline_bp.route('/record/emotion', methods=['POST'])
def record_emotion_change():
    """记录情绪变化"""
    timeline = get_timeline()
    data = request.json or {}

    event_id = timeline.record_emotion_change(
        emotion=data.get('emotion', '3'),
        reason=data.get('reason', '')
    )

    return jsonify({
        'success': True,
        'event_id': event_id
    })
