"""
StudyBuddy Web 版本
使用 Flask 构建 Web 服务器
"""

from flask import Flask, render_template, jsonify, request
from src.core.buddy import Buddy
from src.ai.ai_helper import ask_ai
from src.core.timer import StudyTimer, StudySupervisor
from src.modules.data_manager import (
    load_user_settings, get_motto, set_motto,
    get_favorite_quote, set_favorite_quote,
    get_daily_goal, set_daily_goal
)
from datetime import datetime
import threading
import time

app = Flask(__name__)

# 全局变量存储会话状态
class Session:
    def __init__(self):
        self.supervisor = StudySupervisor()
        self.buddy = Buddy(self.supervisor)
        self.timer = StudyTimer()
        self.lock = threading.Lock()
        # 加载用户设置
        settings = load_user_settings()
        self.motto = settings.get("motto", "")
        self.favorite_quote = settings.get("favorite_quote", "")
        # 使用持久化的每日目标
        self.supervisor.set_daily_goal(settings.get("daily_goal_minutes", 120))

sessions = {}

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    """获取当前状态"""
    session_id = request.args.get('session_id', 'default')
    if session_id not in sessions:
        sessions[session_id] = Session()
    
    session = sessions[session_id]
    with session.lock:
        # 检查时间相关的情绪变化
        session.buddy.check_time_based_emotion()
        
        # 获取监督器状态并更新情绪
        supervisor_status = session.supervisor.get_status()
        session.buddy.update_by_supervisor(supervisor_status)
        
        return jsonify({
            'emotion': session.buddy.get_emotion(),
            'emoji': session.buddy.get_emoji(),
            'emotion_desc': session.buddy.get_emotion_description(),
            'study_time': session.timer.get_current_duration(),
            'target_time': session.timer._target_minutes,
            'remaining': session.timer.get_remaining(),
            'is_running': session.timer._is_running,
            'is_paused': session.timer._pause_time is not None,
            'stats': session.buddy.get_study_stats(),
            'supervisor': supervisor_status,
            'pomodoro': {
                'cycle': session.supervisor._current_pomodoro_cycle,
                'completed': session.supervisor._completed_pomodoros,
                'is_break_mode': session.supervisor._is_break_mode
            }
        })

@app.route('/api/ask', methods=['POST'])
def ask():
    """提问 API"""
    session_id = request.args.get('session_id', 'default')
    if session_id not in sessions:
        sessions[session_id] = Session()
    
    session = sessions[session_id]
    data = request.json
    question = data.get('question', '')
    
    if not question:
        return jsonify({'error': '问题不能为空'}), 400
    
    with session.lock:
        # 设置为思考状态
        session.buddy.update_by_action('ask')
        
        # 调用 AI
        answer = ask_ai(question)
        
        # 设置为开心状态
        session.buddy.update_by_action('answer_received')
        
        return jsonify({
            'answer': answer,
            'emotion': session.buddy.get_emotion(),
            'emoji': session.buddy.get_emoji()
        })

@app.route('/api/study/start', methods=['POST'])
def start_study():
    """开始学习"""
    session_id = request.args.get('session_id', 'default')
    if session_id not in sessions:
        sessions[session_id] = Session()
    
    session = sessions[session_id]
    
    with session.lock:
        if session.timer.start():
            session.buddy.update_by_action('study_start')
            # 启动番茄钟
            session.supervisor.record_activity()
            pomodoro_info = session.supervisor.start_pomodoro()
            return jsonify({
                'success': True,
                'message': pomodoro_info['message'],
                'emotion': session.buddy.get_emotion(),
                'emoji': session.buddy.get_emoji(),
                'pomodoro': pomodoro_info
            })
        else:
            return jsonify({
                'success': False,
                'message': '已在计时中'
            })

@app.route('/api/study/pause', methods=['POST'])
def pause_study():
    """暂停学习"""
    session_id = request.args.get('session_id', 'default')
    if session_id not in sessions:
        sessions[session_id] = Session()
    
    session = sessions[session_id]
    
    with session.lock:
        if session.timer._is_running:
            session.timer.pause()
            return jsonify({'success': True, 'message': '已暂停'})
        elif session.timer._pause_time:
            session.timer.resume()
            return jsonify({'success': True, 'message': '继续学习'})
        else:
            return jsonify({'success': False, 'message': '未开始学习'})

@app.route('/api/study/stop', methods=['POST'])
def stop_study():
    """停止学习"""
    session_id = request.args.get('session_id', 'default')
    if session_id not in sessions:
        sessions[session_id] = Session()
    
    session = sessions[session_id]
    
    with session.lock:
        duration = session.timer.stop()
        if session.timer.check_finish():
            session.buddy.update_by_action('study_finish')
            # 完成番茄钟
            pomodoro_result = session.supervisor.complete_pomodoro()
            session.buddy.on_pomodoro_complete()
            
            # 检查是否达到日目标
            progress = session.supervisor.get_progress()
            if progress['reached_goal']:
                session.buddy.on_goal_reached()
            
            return jsonify({
                'success': True,
                'message': pomodoro_result['message'],
                'duration': duration,
                'emotion': session.buddy.get_emotion(),
                'emoji': session.buddy.get_emoji(),
                'finished': True,
                'pomodoro': pomodoro_result,
                'progress': progress
            })
        return jsonify({
            'success': True,
            'message': '已停止',
            'duration': duration,
            'finished': False
        })

@app.route('/api/reset', methods=['POST'])
def reset():
    """重置"""
    session_id = request.args.get('session_id', 'default')
    if session_id not in sessions:
        sessions[session_id] = Session()
    
    session = sessions[session_id]
    
    with session.lock:
        session.supervisor = StudySupervisor()
        session.buddy = Buddy(session.supervisor)
        session.timer = StudyTimer()
        return jsonify({
            'success': True,
            'emotion': session.buddy.get_emotion(),
            'emoji': session.buddy.get_emoji()
        })

@app.route('/api/set_goal', methods=['POST'])
def set_goal_api():
    """设置每日学习目标"""
    session_id = request.args.get('session_id', 'default')
    if session_id not in sessions:
        sessions[session_id] = Session()
    
    session = sessions[session_id]
    data = request.json
    minutes = data.get('minutes', 120)
    
    with session.lock:
        session.supervisor.set_daily_goal(minutes)
        # 持久化保存
        set_daily_goal(minutes)
        return jsonify({
            'success': True,
            'message': f'目标已设置为 {minutes} 分钟',
            'goal': minutes
        })

@app.route('/api/pomodoro/start_break', methods=['POST'])
def start_break():
    """开始休息"""
    session_id = request.args.get('session_id', 'default')
    if session_id not in sessions:
        sessions[session_id] = Session()
    
    session = sessions[session_id]
    
    with session.lock:
        break_info = session.supervisor.start_break()
        session.buddy.set_emotion('idle')
        return jsonify({
            'success': True,
            'message': break_info['message'],
            'duration': break_info['duration'],
            'emotion': session.buddy.get_emotion(),
            'emoji': session.buddy.get_emoji()
        })

# ==================== 任务管理 API ====================

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """获取所有任务"""
    session_id = request.args.get('session_id', 'default')
    if session_id not in sessions:
        sessions[session_id] = Session()
    
    session = sessions[session_id]
    status = request.args.get('status', 'all')
    tasks = session.buddy.task_manager.get_tasks(status=status)
    return jsonify({
        'success': True,
        'tasks': [t.to_dict() for t in tasks]
    })

@app.route('/api/tasks', methods=['POST'])
def add_task():
    """添加任务"""
    session_id = request.args.get('session_id', 'default')
    if session_id not in sessions:
        sessions[session_id] = Session()
    
    session = sessions[session_id]
    data = request.json
    
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'success': False, 'error': '任务标题不能为空'}), 400
    
    # 处理截止时间
    deadline = data.get('deadline')
    if deadline:
        # 将 datetime-local 格式转换为标准格式
        # datetime-local 返回：YYYY-MM-DDTHH:MM
        # 我们需要：YYYY-MM-DD HH:MM
        deadline = deadline.replace('T', ' ')
    
    task = session.buddy.task_manager.add_task(
        title=title,
        description=data.get('description', '').strip(),
        deadline=deadline
    )
    
    return jsonify({
        'success': True,
        'message': '任务添加成功',
        'task': task.to_dict()
    })

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """更新任务"""
    session_id = request.args.get('session_id', 'default')
    if session_id not in sessions:
        sessions[session_id] = Session()
    
    session = sessions[session_id]
    data = request.json
    
    # 过滤出任务对象有的属性
    valid_fields = ['title', 'description', 'deadline', 'completed']
    update_data = {k: v for k, v in data.items() if k in valid_fields}
    
    task = session.buddy.task_manager.update_task(task_id, **update_data)
    if task:
        return jsonify({'success': True, 'task': task.to_dict()})
    return jsonify({'success': False, 'error': '任务不存在'}), 404

@app.route('/api/tasks/<int:task_id>/complete', methods=['POST'])
def complete_task(task_id):
    """完成任务"""
    session_id = request.args.get('session_id', 'default')
    if session_id not in sessions:
        sessions[session_id] = Session()
    
    session = sessions[session_id]
    
    with session.lock:
        success = session.buddy.task_manager.mark_complete(task_id)
        if success:
            task = session.buddy.task_manager.get_task(task_id)
            session.buddy.on_task_complete(task.title)
            return jsonify({
                'success': True,
                'task': task.to_dict(),
                'emotion': session.buddy.get_emotion(),
                'emoji': session.buddy.get_emoji()
            })
    return jsonify({'success': False, 'error': '任务不存在'}), 404

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """删除任务"""
    session_id = request.args.get('session_id', 'default')
    if session_id not in sessions:
        sessions[session_id] = Session()
    
    session = sessions[session_id]
    success = session.buddy.task_manager.delete_task(task_id)
    return jsonify({'success': success})

@app.route('/api/tasks/stats', methods=['GET'])
def get_task_stats():
    """获取任务统计"""
    session_id = request.args.get('session_id', 'default')
    if session_id not in sessions:
        sessions[session_id] = Session()
    
    session = sessions[session_id]
    stats = session.buddy.task_manager.get_stats()
    return jsonify({'success': True, 'stats': stats})

@app.route('/api/tasks/reminders', methods=['GET'])
def get_task_reminders():
    """获取任务提醒"""
    session_id = request.args.get('session_id', 'default')
    if session_id not in sessions:
        sessions[session_id] = Session()
    
    session = sessions[session_id]
    reminders = session.buddy.task_manager.check_reminders()
    return jsonify({'success': True, 'reminders': reminders})

# ==================== 学习日历 API ====================

@app.route('/api/calendar/stats', methods=['GET'])
def get_calendar_stats():
    """获取学习日历统计"""
    session_id = request.args.get('session_id', 'default')
    if session_id not in sessions:
        sessions[session_id] = Session()
    
    session = sessions[session_id]
    stats = session.buddy.get_calendar_stats()
    return jsonify({'success': True, 'stats': stats})

@app.route('/api/calendar/log', methods=['POST'])
def log_study():
    """记录学习"""
    session_id = request.args.get('session_id', 'default')
    if session_id not in sessions:
        sessions[session_id] = Session()
    
    session = sessions[session_id]
    data = request.json
    duration = data.get('duration', 25)
    subject = data.get('subject', '学习')
    
    with session.lock:
        session.buddy.log_study_session(duration)
        today_duration = session.buddy.study_calendar.get_today_duration()
        
        return jsonify({
            'success': True,
            'today_duration': today_duration,
            'emotion': session.buddy.get_emotion(),
            'emoji': session.buddy.get_emoji()
        })

@app.route('/api/calendar/history', methods=['GET'])
def get_study_history():
    """获取学习历史"""
    session_id = request.args.get('session_id', 'default')
    if session_id not in sessions:
        sessions[session_id] = Session()
    
    session = sessions[session_id]
    days = request.args.get('days', 7, type=int)
    # 使用 get_recent_activity 方法
    activity = session.buddy.study_calendar.get_recent_activity(days)
    return jsonify({'success': True, 'history': activity})

# ==================== 计时器 API ====================

@app.route('/api/timer', methods=['GET'])
def get_timer():
    """获取计时器状态"""
    session_id = request.args.get('session_id', 'default')
    if session_id not in sessions:
        sessions[session_id] = Session()
    
    session = sessions[session_id]
    return jsonify({
        'success': True,
        'study_time': session.timer.get_current_duration(),
        'target_time': session.timer._target_minutes,
        'remaining': session.timer.get_remaining(),
        'is_running': session.timer._is_running,
        'is_paused': session.timer._pause_time is not None
    })

@app.route('/api/timer/set_target', methods=['POST'])
def set_timer_target():
    """设置计时器目标"""
    session_id = request.args.get('session_id', 'default')
    if session_id not in sessions:
        sessions[session_id] = Session()
    
    session = sessions[session_id]
    data = request.json
    minutes = data.get('minutes', 25)
    
    session.timer.set_target(minutes)
    return jsonify({
        'success': True,
        'target': minutes
    })

# ==================== 统计 API ====================

@app.route('/api/stats', methods=['GET'])
def get_all_stats():
    """获取所有统计数据"""
    session_id = request.args.get('session_id', 'default')
    if session_id not in sessions:
        sessions[session_id] = Session()
    
    session = sessions[session_id]
    
    # 获取伙伴学习统计
    buddy_stats = session.buddy.get_study_stats()
    
    # 获取日历统计
    calendar_stats = session.buddy.get_calendar_stats()
    
    # 获取任务统计
    task_stats = session.buddy.task_manager.get_stats()
    
    # 获取番茄钟统计
    supervisor_status = session.supervisor.get_status()
    
    return jsonify({
        'success': True,
        'stats': {
            'buddy': buddy_stats,
            'calendar': calendar_stats,
            'tasks': task_stats,
            'pomodoro': {
                'cycle': session.supervisor._current_pomodoro_cycle,
                'completed': session.supervisor._completed_pomodoros,
                'is_break_mode': session.supervisor._is_break_mode,
                'daily_goal': session.supervisor._daily_goal_minutes,
                'today_progress': supervisor_status.get('progress', {})
            }
        }
    })

# ==================== 日历 API ====================

# ==================== 用户自定义数据 API ====================

@app.route('/api/motto', methods=['GET'])
def get_motto_api():
    """获取座右铭"""
    motto = get_motto()
    return jsonify({
        'success': True,
        'motto': motto
    })

@app.route('/api/motto', methods=['POST'])
def set_motto_api():
    """设置座右铭"""
    data = request.json
    motto = data.get('motto', '').strip()
    
    if set_motto(motto):
        # 更新当前会话
        session_id = request.args.get('session_id', 'default')
        if session_id in sessions:
            sessions[session_id].motto = motto
        return jsonify({
            'success': True,
            'message': '座右铭已更新',
            'motto': motto
        })
    return jsonify({'success': False, 'error': '保存失败'}), 500

@app.route('/api/favorite_quote', methods=['GET'])
def get_favorite_quote_api():
    """获取喜欢的激励语录"""
    quote = get_favorite_quote()
    return jsonify({
        'success': True,
        'favorite_quote': quote
    })

@app.route('/api/favorite_quote', methods=['POST'])
def set_favorite_quote_api():
    """设置喜欢的激励语录"""
    data = request.json
    quote = data.get('quote', '').strip()
    
    if set_favorite_quote(quote):
        # 更新当前会话
        session_id = request.args.get('session_id', 'default')
        if session_id in sessions:
            sessions[session_id].favorite_quote = quote
        return jsonify({
            'success': True,
            'message': '激励语录已更新',
            'quote': quote
        })
    return jsonify({'success': False, 'error': '保存失败'}), 500

# ==================== 日历 API ====================

@app.route('/api/calendar', methods=['GET'])
def get_calendar():
    """获取日历数据"""
    session_id = request.args.get('session_id', 'default')
    if session_id not in sessions:
        sessions[session_id] = Session()
    
    session = sessions[session_id]
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    
    # 如果没有指定年月，使用当前年月
    if year is None or month is None:
        now = datetime.now()
        year = now.year
        month = now.month
    
    # 获取指定月份的学习记录
    goal_minutes = session.supervisor._daily_goal_minutes
    calendar_data = []
    
    # 获取该月所有天数
    import calendar as cal
    days_in_month = cal.monthrange(year, month)[1]
    
    for day in range(1, days_in_month + 1):
        date_str = f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}"
        # 查找该日期的学习记录
        entries = session.buddy.study_calendar.get_entries_by_date(date_str)
        total_duration = sum(e['duration'] for e in entries)
        
        progress = (total_duration / goal_minutes * 100) if goal_minutes > 0 else 0
        calendar_data.append({
            'date': date_str,
            'duration': total_duration,
            'goal': goal_minutes,
            'progress': min(progress, 100),
            'entries': entries  # 包含该日期的详细学习记录
        })
    
    return jsonify({
        'success': True,
        'calendar': calendar_data,
        'daily_goal': goal_minutes,
        'year': year,
        'month': month
    })

# ==================== 学习计划 API ====================

if __name__ == '__main__':
    app.run(debug=True, port=5000)
