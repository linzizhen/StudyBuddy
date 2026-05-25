"""
StudyPal 数据洞察 API
提供学习数据统计和可视化接口

作者：StudyPal
日期：2026-05-25
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, date, timedelta
from collections import defaultdict
import json
import os

insights_bp = Blueprint('insights', __name__, url_prefix='/api/insights')


def get_data_dir():
    """获取数据目录"""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')


def load_json(filename, default=None):
    """加载 JSON 文件"""
    filepath = os.path.join(get_data_dir(), filename)
    if not os.path.exists(filepath):
        return default or {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return default or {}


def save_json(filename, data):
    """保存 JSON 文件"""
    filepath = os.path.join(get_data_dir(), filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


@insights_bp.route('/overview', methods=['GET'])
def get_overview():
    """获取数据概览"""
    days = request.args.get('days', 30, type=int)

    study_data = load_json('study_tracker.json', {'sessions': []})
    diary_data = load_json('diary.json', {'entries': []})
    task_data = load_json('tasks.json', {'tasks': []})

    sessions = study_data.get('sessions', [])
    entries = diary_data.get('entries', [])
    tasks = task_data.get('tasks', [])

    # 计算日期范围
    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    # 过滤日期范围内的数据
    recent_sessions = [
        s for s in sessions
        if s.get('date') and start_date <= date.fromisoformat(s['date']) <= end_date
    ]
    recent_entries = [
        e for e in entries
        if e.get('date') and start_date <= date.fromisoformat(e['date']) <= end_date
    ]

    # 计算统计数据
    total_minutes = sum(s.get('duration', 0) for s in recent_sessions)
    total_hours = round(total_minutes / 60, 1)

    # 科目分布
    subject_dist = defaultdict(int)
    for s in recent_sessions:
        subject_dist[s.get('subject', '其他')] += s.get('duration', 0)

    # 日均学习
    diary_dates = set(e['date'] for e in recent_entries)
    active_days = len(diary_dates) or 1
    daily_avg = round(total_minutes / active_days / 60, 1) if active_days > 0 else 0

    # 情绪统计
    emotion_counts = defaultdict(int)
    for e in recent_entries:
        emotion_counts[e.get('emotion_label', '一般')] += 1

    # 任务统计
    pending = sum(1 for t in tasks if t.get('status') == 'pending')
    completed = sum(1 for t in tasks if t.get('status') == 'completed')

    return jsonify({
        'success': True,
        'overview': {
            'total_hours': total_hours,
            'total_sessions': len(recent_sessions),
            'total_entries': len(recent_entries),
            'daily_average': daily_avg,
            'subject_distribution': dict(subject_dist),
            'emotion_distribution': dict(emotion_counts),
            'pending_tasks': pending,
            'completed_tasks': completed,
            'period_days': days
        }
    })


@insights_bp.route('/study-chart', methods=['GET'])
def get_study_chart():
    """获取学习曲线数据（用于图表）"""
    days = request.args.get('days', 30, type=int)

    study_data = load_json('study_tracker.json', {'sessions': []})
    sessions = study_data.get('sessions', [])

    # 生成日期序列
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)

    # 按日期聚合学习时长
    daily_hours = defaultdict(float)
    daily_sessions = defaultdict(int)

    for s in sessions:
        try:
            session_date = date.fromisoformat(s['date'])
            if start_date <= session_date <= end_date:
                daily_hours[session_date.isoformat()] += s.get('duration', 0) / 60
                daily_sessions[session_date.isoformat()] += 1
        except:
            continue

    # 填充缺失日期
    chart_data = []
    current = start_date
    while current <= end_date:
        date_str = current.isoformat()
        chart_data.append({
            'date': date_str,
            'hours': round(daily_hours.get(date_str, 0), 2),
            'sessions': daily_sessions.get(date_str, 0)
        })
        current += timedelta(days=1)

    return jsonify({
        'success': True,
        'chart_data': chart_data,
        'period_days': days
    })


@insights_bp.route('/emotion-chart', methods=['GET'])
def get_emotion_chart():
    """获取情绪曲线数据"""
    days = request.args.get('days', 30, type=int)

    diary_data = load_json('diary.json', {'entries': []})
    entries = diary_data.get('entries', [])

    # 生成日期序列
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)

    # 按日期映射情绪
    emotion_map = {}
    for e in entries:
        try:
            entry_date = date.fromisoformat(e['date'])
            if start_date <= entry_date <= end_date:
                emotion_map[entry_date.isoformat()] = {
                    'level': e.get('emotion_level', 3),
                    'label': e.get('emotion_label', '一般')
                }
        except:
            continue

    # 填充数据
    chart_data = []
    current = start_date
    while current <= end_date:
        date_str = current.isoformat()
        if date_str in emotion_map:
            chart_data.append({
                'date': date_str,
                'level': emotion_map[date_str]['level'],
                'label': emotion_map[date_str]['label']
            })
        else:
            chart_data.append({
                'date': date_str,
                'level': None,
                'label': None
            })
        current += timedelta(days=1)

    return jsonify({
        'success': True,
        'chart_data': chart_data,
        'period_days': days
    })


@insights_bp.route('/subject-analysis', methods=['GET'])
def get_subject_analysis():
    """获取科目分析"""
    days = request.args.get('days', 30, type=int)

    study_data = load_json('study_tracker.json', {'sessions': []})
    sessions = study_data.get('sessions', [])

    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    # 按科目聚合
    subject_stats = defaultdict(lambda: {'total_minutes': 0, 'sessions': 0, 'dates': set()})

    for s in sessions:
        try:
            session_date = date.fromisoformat(s['date'])
            if start_date <= session_date <= end_date:
                subject = s.get('subject', '其他')
                subject_stats[subject]['total_minutes'] += s.get('duration', 0)
                subject_stats[subject]['sessions'] += 1
                subject_stats[subject]['dates'].add(s['date'])
        except:
            continue

    # 计算统计数据
    total_minutes = sum(v['total_minutes'] for v in subject_stats.values())
    result = []

    for subject, stats in sorted(subject_stats.items(), key=lambda x: x[1]['total_minutes'], reverse=True):
        minutes = stats['total_minutes']
        result.append({
            'subject': subject,
            'total_hours': round(minutes / 60, 1),
            'sessions': stats['sessions'],
            'active_days': len(stats['dates']),
            'percentage': round(minutes / total_minutes * 100, 1) if total_minutes > 0 else 0
        })

    return jsonify({
        'success': True,
        'subjects': result,
        'total_hours': round(total_minutes / 60, 1)
    })


@insights_bp.route('/weekly-summary', methods=['GET'])
def get_weekly_summary():
    """获取周报摘要"""
    # 本周数据
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    study_data = load_json('study_tracker.json', {'sessions': []})
    diary_data = load_json('diary.json', {'entries': []})

    # 本周学习
    week_sessions = [
        s for s in study_data.get('sessions', [])
        if s.get('date') and week_start <= date.fromisoformat(s['date']) <= week_end
    ]
    week_minutes = sum(s.get('duration', 0) for s in week_sessions)

    # 本周日记
    week_entries = [
        e for e in diary_data.get('entries', [])
        if e.get('date') and week_start <= date.fromisoformat(e['date']) <= week_end
    ]

    # 情绪分布
    emotion_counts = defaultdict(int)
    for e in week_entries:
        emotion_counts[e.get('emotion_label', '一般')] += 1

    # 计算上周对比
    prev_week_start = week_start - timedelta(days=7)
    prev_week_end = week_start - timedelta(days=1)

    prev_sessions = [
        s for s in study_data.get('sessions', [])
        if s.get('date') and prev_week_start <= date.fromisoformat(s['date']) <= prev_week_end
    ]
    prev_minutes = sum(s.get('duration', 0) for s in prev_sessions)

    # 计算变化
    change = 0
    if prev_minutes > 0:
        change = round((week_minutes - prev_minutes) / prev_minutes * 100, 1)

    # 本周各天分布
    daily_breakdown = []
    for i in range(7):
        day = week_start + timedelta(days=i)
        day_sessions = [s for s in week_sessions if s.get('date') == day.isoformat()]
        day_minutes = sum(s.get('duration', 0) for s in day_sessions)
        daily_breakdown.append({
            'day': day.isoformat(),
            'weekday': ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][i],
            'hours': round(day_minutes / 60, 1),
            'sessions': len(day_sessions)
        })

    return jsonify({
        'success': True,
        'summary': {
            'week_start': week_start.isoformat(),
            'week_end': week_end.isoformat(),
            'total_hours': round(week_minutes / 60, 1),
            'total_sessions': len(week_sessions),
            'total_entries': len(week_entries),
            'change_percent': change,
            'emotion_distribution': dict(emotion_counts),
            'daily_breakdown': daily_breakdown
        }
    })
