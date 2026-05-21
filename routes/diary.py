"""
StudyPal 日记路由
处理考研日记、情绪记录相关 API
"""

from flask import Blueprint, jsonify, request

diary_bp = Blueprint('diary', __name__, url_prefix='/api/diary')


def get_diary():
    """获取 Diary 实例"""
    from src.diary.diary import get_diary
    return get_diary()


def get_buddy():
    """获取 Buddy 实例"""
    from src.core.buddy import get_buddy
    return get_buddy()


@diary_bp.route('', methods=['GET'])
def get_diary_entries():
    """获取日记列表"""
    diary = get_diary()
    limit = request.args.get('limit', 30, type=int)

    entries = diary.get_entries(limit)
    return jsonify({
        'success': True,
        'entries': [e.to_dict() for e in entries]
    })


@diary_bp.route('/today', methods=['GET'])
def get_today_diary():
    """获取今日日记"""
    diary = get_diary()
    entry = diary.get_today()

    return jsonify({
        'success': True,
        'entry': entry.to_dict() if entry else None
    })


@diary_bp.route('', methods=['POST'])
def add_diary_entry():
    """添加日记"""
    from src.diary.diary import DiaryEntry
    diary = get_diary()
    data = request.json or {}

    emotion_level = data.get('emotion_level', 3)
    # 验证情绪等级范围
    if not isinstance(emotion_level, int) or not (1 <= emotion_level <= 5):
        return jsonify({
            'success': False,
            'error': '情绪等级必须在 1 到 5 之间'
        }), 400

    entry = diary.add_entry(
        emotion_level=emotion_level,
        study_feeling=data.get('study_feeling', ''),
        biggest_event=data.get('biggest_event', ''),
        words_to_buddy=data.get('words_to_buddy', '')
    )

    response = {'success': True, 'entry': entry.to_dict()}

    # 如果情绪低，触发关心
    if emotion_level <= 2:
        buddy = get_buddy()
        caring = buddy.trigger_emotion_support(
            DiaryEntry.EMOTION_LABELS.get(emotion_level, ''),
            emotion_level
        )
        response['buddy_caring'] = caring.message

    return jsonify(response)


@diary_bp.route('/emotions', methods=['GET'])
def get_emotion_curve():
    """获取情绪曲线"""
    diary = get_diary()
    days = request.args.get('days', 7, type=int)

    curve = diary.get_emotion_curve(days)
    return jsonify({
        'success': True,
        'curve': curve
    })


@diary_bp.route('/review', methods=['GET'])
def get_diary_review():
    """获取日记回顾"""
    diary = get_diary()

    emotion_filter = request.args.get('emotion')  # 可选：按情绪筛选
    days = request.args.get('days', 30, type=int)

    entries = diary.get_entries(limit=days)

    # 如果有情绪筛选
    if emotion_filter:
        emotion_map = {
            'happy': [4, 5],
            'neutral': [3],
            'sad': [1, 2]
        }
        target_levels = emotion_map.get(emotion_filter, [])
        if target_levels:
            entries = [e for e in entries if e.emotion_level in target_levels]

    # 生成回顾分析
    analysis = _analyze_diary_entries(entries)

    return jsonify({
        'success': True,
        'entries': [e.to_dict() for e in entries],
        'analysis': analysis
    })


def _analyze_diary_entries(entries):
    """分析日记条目，生成回顾分析"""
    if not entries:
        return {
            'summary': '暂无日记记录',
            'emotion_trend': 'stable',
            'top_emotions': [],
            'average_level': 0,
            'total_entries': 0
        }

    # 统计情绪分布
    emotion_counts = {}
    for entry in entries:
        label = entry.emotion_label or '未知'
        emotion_counts[label] = emotion_counts.get(label, 0) + 1

    # 计算平均情绪
    avg_level = sum(e.emotion_level for e in entries) / len(entries)

    # 分析趋势（最近7天 vs 更早）
    recent = entries[:7] if len(entries) >= 7 else entries
    earlier = entries[7:] if len(entries) > 7 else []

    trend = 'stable'
    if recent and earlier:
        recent_avg = sum(e.emotion_level for e in recent) / len(recent)
        earlier_avg = sum(e.emotion_level for e in earlier) / len(earlier)
        if recent_avg > earlier_avg + 0.3:
            trend = 'improving'
        elif recent_avg < earlier_avg - 0.3:
            trend = 'declining'

    # 情绪趋势描述
    trend_descriptions = {
        'improving': '你这段时间情绪在好转，继续保持！',
        'declining': '最近情绪有点低落，要注意调节哦~',
        'stable': '情绪整体比较稳定，不错！'
    }

    # 生成总结
    top_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:3]

    if avg_level >= 4:
        summary = '整体状态很不错，继续加油！'
    elif avg_level >= 3:
        summary = '整体状态一般，可以适当放松一下。'
    else:
        summary = '最近压力有点大，要多注意休息和调节情绪。'

    return {
        'summary': summary,
        'emotion_trend': trend,
        'trend_description': trend_descriptions.get(trend, ''),
        'top_emotions': [{'label': k, 'count': v} for k, v in top_emotions],
        'average_level': round(avg_level, 1),
        'total_entries': len(entries),
        'emotion_counts': emotion_counts
    }
