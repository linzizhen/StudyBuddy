"""
StudyPal 计划路由
处理学习计划相关 API
"""

from flask import Blueprint, jsonify, request

plans_bp = Blueprint('plans', __name__, url_prefix='/api/plans')


@plans_bp.route('', methods=['GET'])
def get_study_plans():
    """获取所有学习计划"""
    from src.modules.plan_generator import get_plan_generator
    generator = get_plan_generator()

    plans = generator.get_active_plans()
    completed = generator.get_completed_plans()
    stats = generator.get_stats()

    return jsonify({
        'success': True,
        'active_plans': [p.to_dict() for p in plans],
        'completed_plans': [p.to_dict() for p in completed],
        'stats': stats
    })


@plans_bp.route('', methods=['POST'])
def create_study_plan():
    """创建学习计划"""
    from src.modules.plan_generator import get_plan_generator
    generator = get_plan_generator()

    data = request.json or {}
    subject = data.get('subject', '').strip()
    exam_date = data.get('exam_date', '')
    daily_hours = data.get('daily_hours', 2.0)
    use_ai = data.get('use_ai', True)

    if not subject:
        return jsonify({'success': False, 'error': '科目名称不能为空'}), 400

    if not exam_date:
        return jsonify({'success': False, 'error': '考试日期不能为空'}), 400

    try:
        if use_ai and generator.ai_helper:
            plan = generator.generate_plan_ai(subject, exam_date, daily_hours)
        else:
            plan = generator.generate_plan_basic(subject, exam_date, daily_hours)

        return jsonify({
            'success': True,
            'message': '学习计划已生成',
            'plan': plan.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@plans_bp.route('/<int:plan_id>', methods=['GET'])
def get_study_plan(plan_id):
    """获取指定学习计划"""
    from src.modules.plan_generator import get_plan_generator
    generator = get_plan_generator()

    plan = generator.get_plan(plan_id)
    if plan:
        return jsonify({'success': True, 'plan': plan.to_dict()})
    return jsonify({'success': False, 'error': '计划不存在'}), 404


@plans_bp.route('/<int:plan_id>', methods=['PUT'])
def update_study_plan(plan_id):
    """更新学习计划"""
    from src.modules.plan_generator import get_plan_generator
    generator = get_plan_generator()

    data = request.json or {}
    plan = generator.get_plan(plan_id)

    if plan:
        if data.get('completed'):
            plan.mark_complete()
        generator._save_plans()
        return jsonify({'success': True, 'plan': plan.to_dict()})
    return jsonify({'success': False, 'error': '计划不存在'}), 404


@plans_bp.route('/<int:plan_id>', methods=['DELETE'])
def delete_study_plan(plan_id):
    """删除学习计划"""
    from src.modules.plan_generator import get_plan_generator
    generator = get_plan_generator()

    success = generator.delete_plan(plan_id)
    return jsonify({'success': success})


@plans_bp.route('/expiring', methods=['GET'])
def get_expiring_plans():
    """获取即将到期的学习计划"""
    from src.modules.plan_generator import get_plan_generator
    generator = get_plan_generator()

    days = request.args.get('days', 7, type=int)
    plans = generator.get_expiring_plans(days)

    return jsonify({
        'success': True,
        'plans': [p.to_dict() for p in plans]
    })
