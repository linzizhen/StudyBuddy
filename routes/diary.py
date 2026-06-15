"""
StudyPal 日记路由 v5
处理日记 CRUD、标签、图片上传等 API
"""

import logging
import os
import base64
import uuid
from flask import Blueprint, jsonify, request
from src.diary.diary import get_diary, DiaryEntry

logger = logging.getLogger(__name__)
diary_bp = Blueprint('diary', __name__, url_prefix='/api/diary')


# ==================== 读取 ====================

@diary_bp.route('', methods=['GET'])
def get_diary_entries():
    """获取日记列表（支持筛选）"""
    diary = get_diary()
    
    keyword = request.args.get('keyword', '').strip() or None
    emotion_level = request.args.get('emotion', type=int)
    tag = request.args.get('tag', '').strip() or None
    date_from = request.args.get('date_from', '').strip() or None
    date_to = request.args.get('date_to', '').strip() or None
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    if keyword or emotion_level or tag or date_from or date_to:
        entries = diary.get_entries_filtered(
            keyword=keyword,
            emotion_level=emotion_level,
            tag=tag,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset
        )
    else:
        entries = diary.get_entries(limit=limit, offset=offset)
    
    return jsonify({
        'success': True,
        'entries': [e.to_dict() for e in entries],
        'streak': diary.get_streak(),
        'total': diary.count()
    })


@diary_bp.route('/today', methods=['GET'])
def get_today_diary():
    """获取今日日记"""
    diary = get_diary()
    entry = diary.get_today()
    return jsonify({
        'success': True,
        'entry': entry.to_dict() if entry else None,
        'streak': diary.get_streak()
    })


@diary_bp.route('/stats', methods=['GET'])
def get_diary_stats():
    """获取日记统计"""
    diary = get_diary()
    days = request.args.get('days', 30, type=int)
    curve = diary.get_emotion_curve(days)
    
    return jsonify({
        'success': True,
        'streak': diary.get_streak(),
        'total_entries': diary.count(),
        'emotion_curve': curve,
        'tags': diary.get_user_tags()
    })


@diary_bp.route('/emotions', methods=['GET'])
def get_emotion_curve():
    """获取情绪曲线"""
    diary = get_diary()
    days = request.args.get('days', 30, type=int)
    curve = diary.get_emotion_curve(days)
    return jsonify({'success': True, 'curve': curve})


@diary_bp.route('/tags', methods=['GET'])
def get_tags():
    """获取标签列表"""
    diary = get_diary()
    return jsonify({
        'success': True,
        'tags': diary.get_user_tags()
    })


# ==================== 写入 ====================

@diary_bp.route('', methods=['POST'])
def save_diary():
    """
    保存日记（今日有则更新，无则创建）
    """
    diary = get_diary()
    data = request.json or {}
    
    emotion_level = data.get('emotion_level', 5)
    if not isinstance(emotion_level, int) or not (1 <= emotion_level <= 10):
        return jsonify({'success': False, 'error': '情绪等级必须在 1 到 10 之间'}), 400
    
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    images = data.get('images', [])
    tags = data.get('tags', [])
    weather = data.get('weather', '')
    
    # 检查今日是否已有日记
    existing = diary.get_today()
    if existing:
        # 更新
        entry = diary.update_entry(
            entry_id=existing.id,
            emotion_level=emotion_level,
            title=title,
            content=content,
            images=images,
            tags=tags,
            weather=weather
        )
        action = 'update'
        logger.info(f"[diary] 更新日记 id={entry.id} emotion={emotion_level}")
    else:
        # 创建
        entry = diary.add_entry(
            emotion_level=emotion_level,
            title=title,
            content=content,
            images=images,
            tags=tags,
            weather=weather
        )
        action = 'create'
        logger.info(f"[diary] 新建日记 id={entry.id} emotion={emotion_level}")
    
    response = {
        'success': True,
        'entry': entry.to_dict(),
        'action': action,
        'streak': diary.get_streak()
    }
    
    # 情绪低时触发搭子关心
    if emotion_level <= 2:
        try:
            buddy = get_buddy()
            caring = buddy.trigger_emotion_support(
                entry.emotion_label, emotion_level
            )
            response['buddy_caring'] = caring.message
        except:
            pass
    
    return jsonify(response)


@diary_bp.route('/<entry_id>', methods=['GET'])
def get_diary_entry(entry_id):
    """获取单条日记"""
    diary = get_diary()
    entry = diary.get_entry(entry_id)
    if entry:
        return jsonify({'success': True, 'entry': entry.to_dict()})
    return jsonify({'success': False, 'error': '日记不存在'}), 404


@diary_bp.route('/<entry_id>', methods=['PUT'])
def update_diary_entry(entry_id):
    """更新日记"""
    diary = get_diary()
    data = request.json or {}
    
    entry = diary.update_entry(
        entry_id=entry_id,
        emotion_level=data.get('emotion_level'),
        title=data.get('title'),
        content=data.get('content'),
        images=data.get('images'),
        tags=data.get('tags'),
        weather=data.get('weather')
    )
    
    if entry:
        return jsonify({'success': True, 'entry': entry.to_dict()})
    return jsonify({'success': False, 'error': '日记不存在'}), 404


@diary_bp.route('/<entry_id>', methods=['DELETE'])
def delete_diary_entry(entry_id):
    """删除日记"""
    diary = get_diary()
    if diary.delete_entry(entry_id):
        return jsonify({'success': True, 'message': '删除成功'})
    return jsonify({'success': False, 'error': '日记不存在'}), 404


# ==================== 标签管理 ====================

@diary_bp.route('/tags', methods=['POST'])
def add_tag():
    """添加标签"""
    diary = get_diary()
    data = request.json or {}
    tag = data.get('tag', '').strip()
    
    if not tag:
        return jsonify({'success': False, 'error': '标签不能为空'}), 400
    
    if diary.add_user_tag(tag):
        return jsonify({'success': True, 'tags': diary.get_user_tags()})
    return jsonify({'success': False, 'error': '标签已存在'})


@diary_bp.route('/tags/<tag>', methods=['DELETE'])
def remove_tag(tag):
    """删除标签"""
    diary = get_diary()
    if diary.remove_user_tag(tag):
        return jsonify({'success': True, 'tags': diary.get_user_tags()})
    return jsonify({'success': False, 'error': '标签不存在'}), 404


# ==================== 图片上传 ====================

@diary_bp.route('/upload-image', methods=['POST'])
def upload_diary_image():
    """上传日记图片"""
    if 'image' not in request.files and not request.data:
        return jsonify({'success': False, 'error': '没有上传文件'}), 400

    try:
        image_data = None
        file_ext = 'png'

        if 'image' in request.files:
            file = request.files['image']
            if file.filename:
                file_ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else 'png'
                image_data = file.read()
        elif request.data:
            try:
                json_data = request.get_json(silent=True)
                if json_data and json_data.get('image_base64'):
                    b64 = json_data['image_base64']
                    if ',' in b64:
                        b64 = b64.split(',', 1)[1]
                    image_data = base64.b64decode(b64)
                    file_ext = 'png'
            except Exception:
                return jsonify({'success': False, 'error': '图片解析失败'}), 400

        if not image_data:
            return jsonify({'success': False, 'error': '没有上传文件'}), 400

        if len(image_data) > 5 * 1024 * 1024:
            return jsonify({'success': False, 'error': '图片大小不能超过 5MB'}), 400

        # 保存到 static/uploads/diary/
        upload_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'static', 'uploads', 'diary'
        )
        os.makedirs(upload_dir, exist_ok=True)

        filename = f"{uuid.uuid4().hex}.{file_ext}"
        filepath = os.path.join(upload_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(image_data)

        image_url = f"/static/uploads/diary/{filename}"

        return jsonify({
            'success': True,
            'image_url': image_url
        })

    except Exception as e:
        return jsonify({'success': False, 'error': f'上传失败: {str(e)}'}), 500


def get_buddy():
    """复用 utils 的缓存版本"""
    from routes.utils import get_buddy
    return get_buddy()


def get_diary():
    """获取日记实例"""
    from src.diary.diary import get_diary as _get_diary
    return _get_diary()
