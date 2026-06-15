"""
StudyPal 任务路由
处理任务管理相关 API
"""

from flask import Blueprint, jsonify, request
from datetime import datetime

tasks_bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')


def get_task_manager():
    """获取任务管理器"""
    from src.modules.task_manager import get_task_manager as _get_tm
    return _get_tm()


def get_buddy():
    """获取 Buddy 实例"""
    from src.core.buddy import get_buddy
    return get_buddy()


@tasks_bp.route('', methods=['GET'])
def get_tasks():
    """获取任务列表"""
    task_manager = get_task_manager()
    status = request.args.get('status', 'all')
    tasks = task_manager.get_tasks(status=status)

    return jsonify({
        'success': True,
        'tasks': [t.to_dict() for t in tasks]
    })


@tasks_bp.route('', methods=['POST'])
def add_task():
    """添加任务"""
    task_manager = get_task_manager()
    data = request.json or {}

    title = data.get('title', '').strip()
    if not title:
        return jsonify({'success': False, 'error': '任务标题不能为空'}), 400

    deadline = data.get('deadline')
    if deadline:
        deadline = deadline.replace('T', ' ')

    task = task_manager.add_task(
        title=title,
        description=data.get('description', '').strip(),
        deadline=deadline
    )

    return jsonify({
        'success': True,
        'message': '任务添加成功',
        'task': task.to_dict()
    })


@tasks_bp.route('/<task_id>', methods=['PUT'])
def update_task(task_id):
    """更新任务"""
    task_manager = get_task_manager()
    data = request.json or {}

    valid_fields = ['title', 'description', 'deadline', 'completed']
    update_data = {}
    for k, v in data.items():
        if k in valid_fields:
            if k == 'completed':
                update_data['status'] = 'completed' if v else 'pending'
            else:
                update_data[k] = v

    task = task_manager.update_task(task_id, **update_data)
    if task:
        return jsonify({'success': True, 'task': task.to_dict()})
    return jsonify({'success': False, 'error': '任务不存在'}), 404


@tasks_bp.route('/<task_id>/complete', methods=['POST'])
def complete_task(task_id):
    """完成任务"""
    task_manager = get_task_manager()
    buddy = get_buddy()

    success = task_manager.mark_complete(task_id)
    if success:
        task = task_manager.get_task(task_id)
        buddy.on_task_complete(task.title)

        # 检查成就
        from src.modules.achievements import check_achievements, get_achievement_manager
        manager = get_achievement_manager()

        task_stats = task_manager.get_stats()
        study_stats = buddy.get_study_stats()

        user_stats = {
            'tasks_completed': task_stats.get('completed', 0),
            'total_pomodoros': task_stats.get('completed', 0),
            'conversations_count': 0,
        }

        new_achievements = check_achievements(user_stats)
        level_info = manager.get_level()

        return jsonify({
            'success': True,
            'task': task.to_dict(),
            'emotion': buddy.get_emotion(),
            'emoji': buddy.get_emoji(),
            'new_achievements': new_achievements,
            'level_info': level_info.get('level', {}),
            'points_earned': sum(a['reward'] for a in new_achievements)
        })

    return jsonify({'success': False, 'error': '任务不存在'}), 404


@tasks_bp.route('/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """删除任务"""
    task_manager = get_task_manager()
    success = task_manager.delete_task(task_id)
    return jsonify({'success': success})


@tasks_bp.route('/stats', methods=['GET'])
def get_task_stats():
    """获取任务统计"""
    task_manager = get_task_manager()
    stats = task_manager.get_stats()
    return jsonify({'success': True, 'stats': stats})
