"""
StudyPal 挑战路由
处理"我的挑战"模块相关 API：小学/初中/高中三阶段挑战体系
"""

from flask import Blueprint, jsonify, request

challenges_bp = Blueprint('challenges', __name__, url_prefix='/api/challenges')


def get_manager():
    """获取挑战管理器实例"""
    from src.modules.challenge_manager import ChallengeManager
    return ChallengeManager()


# ============ 数据读取与保存 ============

@challenges_bp.route('', methods=['GET'])
def get_challenges():
    """获取完整挑战数据"""
    manager = get_manager()
    return jsonify({
        'success': True,
        'data': manager.data,
    })


@challenges_bp.route('', methods=['POST'])
def save_challenges():
    """保存完整挑战数据（前端整体覆盖写入）"""
    manager = get_manager()
    payload = request.json or {}
    if not isinstance(payload, dict):
        return jsonify({'success': False, 'error': '数据格式错误'}), 400

    # 仅允许更新白名单字段
    new_data = {
        'user_grade_mode': payload.get('user_grade_mode', manager.data.get('user_grade_mode', 'middle')),
        'active_challenge_id': payload.get('active_challenge_id'),
        'challenges': payload.get('challenges', []),
    }
    manager.data.update(new_data)
    manager._save_data()
    return jsonify({'success': True, 'data': manager.data})


# ============ 学段管理 ============

@challenges_bp.route('/grade', methods=['POST'])
def set_grade_mode():
    """设置用户学段"""
    manager = get_manager()
    data = request.json or {}
    grade_mode = data.get('grade_mode')
    try:
        manager.set_grade_mode(grade_mode)
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    return jsonify({'success': True, 'grade_mode': manager.get_grade_mode()})


# ============ 预设模板查询 ============

@challenges_bp.route('/presets/grade/<grade_mode>', methods=['GET'])
def get_grade_presets(grade_mode):
    """获取指定学段的学科预设模板"""
    manager = get_manager()
    presets = manager.get_grade_presets(grade_mode)
    return jsonify({'success': True, 'presets': presets, 'grade_mode': grade_mode})


@challenges_bp.route('/presets/icons', methods=['GET'])
def get_icon_library():
    """获取图标库"""
    manager = get_manager()
    return jsonify({'success': True, 'icons': manager.get_icon_library()})


# ============ 挑战 CRUD ============

@challenges_bp.route('/challenge', methods=['POST'])
def create_challenge():
    """新建挑战"""
    manager = get_manager()
    data = request.json or {}

    name = (data.get('name') or '').strip()
    grade_mode = data.get('grade_mode')
    challenge_type = data.get('type', '学期考试')
    deadline = data.get('deadline', '')
    description = data.get('description', '')

    if not name:
        return jsonify({'success': False, 'error': '挑战名称不能为空'}), 400
    if not grade_mode:
        return jsonify({'success': False, 'error': '请选择学段'}), 400

    try:
        challenge = manager.create_challenge(
            name=name,
            grade_mode=grade_mode,
            challenge_type=challenge_type,
            deadline=deadline,
            description=description,
        )
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400

    return jsonify({'success': True, 'challenge': challenge, 'data': manager.data})


@challenges_bp.route('/challenge/<challenge_id>', methods=['PUT'])
def update_challenge(challenge_id):
    """更新挑战信息"""
    manager = get_manager()
    data = request.json or {}
    challenge = manager.update_challenge(challenge_id, **data)
    if not challenge:
        return jsonify({'success': False, 'error': '挑战不存在'}), 404
    return jsonify({'success': True, 'challenge': challenge})


@challenges_bp.route('/challenge/<challenge_id>', methods=['DELETE'])
def delete_challenge(challenge_id):
    """删除挑战"""
    manager = get_manager()
    manager.delete_challenge(challenge_id)
    return jsonify({'success': True, 'data': manager.data})


@challenges_bp.route('/challenge/<challenge_id>/activate', methods=['POST'])
def activate_challenge(challenge_id):
    """激活某个挑战"""
    manager = get_manager()
    manager.set_active_challenge(challenge_id)
    return jsonify({'success': True, 'active_challenge_id': challenge_id})


# ============ 学科管理 ============

@challenges_bp.route('/challenge/<challenge_id>/subject', methods=['POST'])
def add_subject(challenge_id):
    """添加学科"""
    manager = get_manager()
    data = request.json or {}
    subject = manager.add_subject(challenge_id, data)
    if not subject:
        return jsonify({'success': False, 'error': '挑战不存在'}), 404
    return jsonify({'success': True, 'subject': subject})


@challenges_bp.route('/challenge/<challenge_id>/subject/<subject_id>', methods=['PUT'])
def update_subject(challenge_id, subject_id):
    """更新学科"""
    manager = get_manager()
    data = request.json or {}
    subject = manager.update_subject(challenge_id, subject_id, **data)
    if not subject:
        return jsonify({'success': False, 'error': '学科不存在'}), 404
    return jsonify({'success': True, 'subject': subject})


@challenges_bp.route('/challenge/<challenge_id>/subject/<subject_id>', methods=['DELETE'])
def delete_subject(challenge_id, subject_id):
    """删除学科"""
    manager = get_manager()
    manager.delete_subject(challenge_id, subject_id)
    return jsonify({'success': True})


# ============ 成绩记录 ============

@challenges_bp.route('/challenge/<challenge_id>/subject/<subject_id>/score', methods=['POST'])
def add_score(challenge_id, subject_id):
    """记录成绩"""
    manager = get_manager()
    data = request.json or {}
    date = data.get('date', '')
    score = data.get('score')
    exam_name = data.get('exam_name', '')
    note = data.get('note', '')

    if score is None:
        return jsonify({'success': False, 'error': '请填写分数'}), 400

    try:
        score = float(score)
    except (TypeError, ValueError):
        return jsonify({'success': False, 'error': '分数必须是数字'}), 400

    subject = manager.add_score_record(
        challenge_id=challenge_id,
        subject_id=subject_id,
        date=date,
        score=score,
        exam_name=exam_name,
        note=note,
    )
    if not subject:
        return jsonify({'success': False, 'error': '学科不存在'}), 404
    return jsonify({'success': True, 'subject': subject})


# ============ 里程碑管理 ============

@challenges_bp.route('/challenge/<challenge_id>/milestone', methods=['POST'])
def add_milestone(challenge_id):
    """添加对比项"""
    manager = get_manager()
    data = request.json or {}
    ms = manager.add_milestone(challenge_id, data)
    if not ms:
        return jsonify({'success': False, 'error': '挑战不存在'}), 404
    return jsonify({'success': True, 'milestone': ms})


@challenges_bp.route('/challenge/<challenge_id>/milestone/<ms_id>/toggle', methods=['POST'])
def toggle_milestone(challenge_id, ms_id):
    """切换对比项可见性"""
    manager = get_manager()
    manager.toggle_milestone_visible(challenge_id, ms_id)
    return jsonify({'success': True})


@challenges_bp.route('/challenge/<challenge_id>/milestone/<ms_id>', methods=['DELETE'])
def delete_milestone(challenge_id, ms_id):
    """删除对比项"""
    manager = get_manager()
    manager.delete_milestone(challenge_id, ms_id)
    return jsonify({'success': True})


# ============ 时间线节点管理 ============

@challenges_bp.route('/challenge/<challenge_id>/timeline', methods=['POST'])
def add_timeline_node(challenge_id):
    """添加时间线节点"""
    manager = get_manager()
    data = request.json or {}
    node = manager.add_timeline_node(challenge_id, data)
    if not node:
        return jsonify({'success': False, 'error': '挑战不存在'}), 404
    return jsonify({'success': True, 'node': node})


@challenges_bp.route('/challenge/<challenge_id>/timeline/<node_id>/toggle', methods=['POST'])
def toggle_timeline(challenge_id, node_id):
    """切换节点完成状态"""
    manager = get_manager()
    manager.toggle_timeline_completed(challenge_id, node_id)
    return jsonify({'success': True})


@challenges_bp.route('/challenge/<challenge_id>/timeline/<node_id>', methods=['DELETE'])
def delete_timeline_node(challenge_id, node_id):
    """删除时间线节点"""
    manager = get_manager()
    manager.delete_timeline_node(challenge_id, node_id)
    return jsonify({'success': True})


# ============ 数据迁移 ============

@challenges_bp.route('/migrate', methods=['POST'])
def migrate_data():
    """从旧版考研目标数据迁移到新的挑战体系"""
    manager = get_manager()
    result = manager.migrate_from_user_settings()
    return jsonify({'success': True, **result, 'data': manager.data})