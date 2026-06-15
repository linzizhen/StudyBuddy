"""
StudyPal 搭子洞察路由
处理搭子周记、情绪分析等洞察相关 API
"""

from flask import Blueprint, jsonify
from src.ai.prompt_templates import generate_weekly_insight
import concurrent.futures

insights_bp = Blueprint('insights', __name__, url_prefix='/api/insights')


def _get_buddy():
    from routes.utils import get_buddy
    return get_buddy()


@insights_bp.route('/weekly-insight', methods=['GET'])
def get_weekly_insight():
    """生成搭子周记（3 个 I/O 并行）"""
    buddy = _get_buddy()

    def _load_study():
        return buddy.study.get_stats()

    def _load_emotion():
        return buddy.diary.get_emotion_curve(7)

    def _load_memory():
        return buddy.memory.get_recent_scenes(7)

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        f1 = executor.submit(_load_study)
        f2 = executor.submit(_load_emotion)
        f3 = executor.submit(_load_memory)
        study_stats = f1.result()
        emotion_data = f2.result()
        memories = f3.result()

    insight = generate_weekly_insight(study_stats, emotion_data, memories)

    return jsonify({
        'success': True,
        'data': {
            'insight': insight,
            'study_stats': {
                'week_hours': study_stats.get('week_hours', 0),
                'streak_days': study_stats.get('streak_days', 0),
                'today_hours': study_stats.get('today_hours', 0),
            },
            'emotion_trend': emotion_data.get('labels', []),
            'memory_count': len(memories),
        }
    })


@insights_bp.route('/monthly-report', methods=['GET'])
def get_monthly_report():
    """生成月度报告（3 个 I/O 并行）"""
    buddy = _get_buddy()

    def _load_study():
        return buddy.study.get_stats()

    def _load_entries():
        return buddy.diary.get_entries(30)

    def _load_memory():
        return buddy.memory.get_recent_scenes(30)

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        f1 = executor.submit(_load_study)
        f2 = executor.submit(_load_entries)
        f3 = executor.submit(_load_memory)
        study_stats = f1.result()
        entries = f2.result()
        memories = f3.result()

    # 情绪统计
    emotion_counts = {}
    for entry in entries:
        label = entry.emotion_label
        emotion_counts[label] = emotion_counts.get(label, 0) + 1

    # 生成分析
    total_hours = study_stats.get('total_hours', 0)
    avg_daily = total_hours / 30 if total_hours > 0 else 0

    # 情绪分析
    top_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else '一般'

    report = {
        'period': datetime.now().strftime('%Y年%m月'),
        'total_hours': round(total_hours, 1),
        'avg_daily': round(avg_daily, 1),
        'top_emotion': top_emotion,
        'emotion_counts': emotion_counts,
        'diary_count': len(entries),
        'memory_count': len(memories),
        'streak_days': study_stats.get('streak_days', 0),
        'suggestions': _generate_monthly_suggestions(total_hours, top_emotion, len(memories)),
    }

    return jsonify({
        'success': True,
        'data': report
    })


def _generate_monthly_suggestions(total_hours, top_emotion, memory_count):
    """生成月度建议"""
    suggestions = []

    if total_hours < 50:
        suggestions.append("本月学习时长偏少，可以适当增加每日学习时间")
    elif total_hours > 200:
        suggestions.append("学习强度很大，注意休息和身体状态")

    if top_emotion in ['很难受', '有点丧']:
        suggestions.append("最近情绪有些低落，建议适当放松，调节心态")

    if memory_count < 3:
        suggestions.append("多和小豆聊聊，可以帮助记录更多学习记忆")

    if not suggestions:
        suggestions.append("继续保持目前的状态，你做得很好！")

    return suggestions


@insights_bp.route('/insight-summary', methods=['GET'])
def get_insight_summary():
    """获取洞察摘要（用于首页展示）"""
    buddy = _get_buddy()

    # 获取关键指标
    study = buddy.study
    stats = study.get_stats()
    diary = buddy.diary

    # 计算本周 vs 上周（一次加载，两次过滤）
    recent_sessions = study.get_recent_sessions(14)
    this_week = [s for s in recent_sessions if _is_this_week(s.get('date', ''))]
    last_week = [s for s in recent_sessions if _is_last_week(s.get('date', ''))]

    this_week_hours = sum(s.get('duration', 0) / 60 for s in this_week)
    last_week_hours = sum(s.get('duration', 0) / 60 for s in last_week)

    # 趋势判断
    trend = 'stable'
    trend_text = '和上周持平'
    if this_week_hours > last_week_hours * 1.1:
        trend = 'up'
        trend_text = f'比上周多了 {this_week_hours - last_week_hours:.1f} 小时'
    elif last_week_hours > 0 and this_week_hours < last_week_hours * 0.9:
        trend = 'down'
        trend_text = f'比上周少了 {last_week_hours - this_week_hours:.1f} 小时'

    # 获取本周情绪
    emotion_data = diary.get_emotion_curve(7)
    valid_levels = [l for l in emotion_data.get('levels', []) if l is not None]
    avg_emotion = sum(valid_levels) / len(valid_levels) if valid_levels else 3

    summary = {
        'week_hours': round(this_week_hours, 1),
        'trend': trend,
        'trend_text': trend_text,
        'emotion_avg': round(avg_emotion, 1),
        'emotion_label': (lambda idx: ['很难受', '有点丧', '一般', '还好', '很开心'][max(0, min(4, idx))] if valid_levels else '一般')(int(avg_emotion) - 1),
        'streak_days': stats.get('streak_days', 0),
        'study_summary': _get_study_summary(stats),
    }

    return jsonify({
        'success': True,
        'data': summary
    })


def _is_this_week(date_str):
    """判断日期是否在本周"""
    from datetime import datetime, timedelta
    if not date_str:
        return False
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        return date >= week_start
    except (ValueError, TypeError):
        return False


def _is_last_week(date_str):
    """判断日期是否在上周"""
    from datetime import datetime, timedelta
    if not date_str:
        return False
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        last_week_start = week_start - timedelta(days=7)
        return last_week_start <= date < week_start
    except (ValueError, TypeError):
        return False


def _get_study_summary(stats):
    """生成学习摘要文本"""
    hours = stats.get('week_hours', 0)

    if hours >= 40:
        return "本周学习强度很高，继续保持！"
    elif hours >= 20:
        return "学习状态不错，注意节奏"
    elif hours >= 5:
        return "本周学习时间较少，下周加油"
    else:
        return "还没有开始学习，今天就开始吧！"
