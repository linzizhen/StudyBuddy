"""
StudyPal Web 版本
使用 Flask 构建 Web 服务器

功能概述：
- AI 学习助手问答
- 番茄钟计时器
- 任务管理
- 学习计划生成
- 学习日历统计
- 成就系统
- 用户设置管理

作者：StudyPal
创建日期：2026-04-13
"""

from flask import Flask, render_template, jsonify, request
from src.core.buddy import Buddy
from src.ai.ai_helper import ask_ai_with_context, get_ai_conversations, get_conversation_messages, delete_ai_conversation, new_ai_conversation
from src.core.timer import StudyTimer, StudySupervisor
from src.modules.data_manager import (
    load_user_settings, get_motto, set_motto,
    get_favorite_quote, set_favorite_quote,
    get_daily_goal, set_daily_goal
)
from datetime import datetime
import threading
import time
import logging

logger = logging.getLogger(__name__)

# ==================== AI 监督模块集成 ====================

# 延迟导入 ai_supervisor，实现优雅降级
_monitor_class = None
_monitor_enabled = False

try:
    import sys
    import os

    # 将 ai_supervisor 添加到模块搜索路径
    ai_supervisor_path = os.path.join(os.path.dirname(__file__), 'ai_supervisor')
    if ai_supervisor_path not in sys.path:
        sys.path.insert(0, ai_supervisor_path)

    from ai_supervisor import Monitor
    _monitor_class = Monitor
    _monitor_enabled = True
    logger.info("AI Monitor 模块加载成功")
except Exception as e:
    logger.warning(f"AI Monitor 模块未加载，功能受限: {type(e).__name__}: {e}")
    _monitor_class = None
    _monitor_enabled = False
except Exception as e:
    logger.warning(f"加载 AI Monitor 模块时发生错误: {e}")
    _monitor_class = None
    _monitor_enabled = False

app = Flask(__name__)

# ==================== 全局会话管理 ====================

class Session:
    """
    会话管理类
    
    每个会话包含：
    - StudySupervisor: 番茄钟监督器
    - Buddy: 学习伙伴
    - StudyTimer: 计时器
    - Monitor: AI 监督器（可选）
    - 用户设置缓存
    """
    def __init__(self):
        self.supervisor = StudySupervisor()
        self.buddy = Buddy(self.supervisor)
        self.timer = StudyTimer()
        self.lock = threading.Lock()
        # AI 监督模块（可选）
        self.monitor = None
        self._monitor_thread = None
        self._monitor_running = False
        # 加载用户设置
        settings = load_user_settings()
        self.motto = settings.get("motto", "")
        self.favorite_quote = settings.get("favorite_quote", "")
        # 使用持久化的每日目标
        self.supervisor.set_daily_goal(settings.get("daily_goal_minutes", 120))
        # 尝试初始化 AI 监督器
        self._init_monitor()

    def _init_monitor(self):
        """初始化 AI 监督器（可选功能）"""
        global _monitor_class, _monitor_enabled
        if not _monitor_enabled or _monitor_class is None:
            return
        
        try:
            self.monitor = _monitor_class()
            logger.info("Session 中的 AI Monitor 实例已创建")
        except Exception as e:
            logger.warning(f"创建 AI Monitor 实例失败: {e}")
            self.monitor = None

    def start_monitor(self):
        """启动 AI 监督监控"""
        if self.monitor is None:
            return False
        
        if self._monitor_running:
            return False
        
        try:
            self.monitor.start()
            self._monitor_running = True
            logger.info("AI Monitor 已启动")
            return True
        except Exception as e:
            logger.warning(f"启动 AI Monitor 失败: {e}")
            return False

    def stop_monitor(self):
        """停止 AI 监督监控"""
        if self.monitor is None or not self._monitor_running:
            return False
        
        try:
            self.monitor.stop()
            self._monitor_running = False
            logger.info("AI Monitor 已停止")
            return True
        except Exception as e:
            logger.warning(f"停止 AI Monitor 失败: {e}")
            return False

    def get_focus_status(self):
        """获取专注度状态（来自 AI Monitor）"""
        if self.monitor is None or not self._monitor_running:
            return None
        
        try:
            state = self.monitor.get_state()
            score = self.monitor.get_score()
            report = self.monitor.get_report()
            return {
                'state': state,
                'score': score,
                'report': report,
                'monitor_enabled': True
            }
        except Exception as e:
            logger.warning(f"获取专注度状态失败: {e}")
            return None

    def get_monitor_camera_frame(self):
        """获取摄像头画面（用于前端显示）"""
        if self.monitor is None:
            return None
        
        try:
            return self.monitor.get_camera_frame()
        except Exception:
            return None

# 全局会话存储（键为 session_id）
sessions = {}

# ==================== 基础路由 ====================

@app.route('/')
def index():
    """
    主页路由
    
    返回主页面模板
    """
    return render_template('index.html')

# ==================== 状态 API ====================

@app.route('/api/status', methods=['GET'])
def get_status():
    """
    获取当前会话状态
    
    返回：
    - 情绪状态
    - 计时器状态
    - 番茄钟状态
    - 学习统计
    - 专注度状态（AI Monitor）
    """
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
        
        # 获取专注度状态并更新情绪（如果有 AI Monitor）
        focus_status = session.get_focus_status()
        if focus_status:
            session.buddy.update_by_focus(
                focus_status.get('score'),
                focus_status.get('state')
            )
        
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
            },
            'focus': focus_status,
            'focus_stats': session.buddy.get_focus_stats()
        })

# ==================== AI 问答 API ====================

@app.route('/api/ask', methods=['POST'])
def ask():
    """
    AI 问答 API
    
    请求体：
    - question: 问题内容
    - conversation_id: 对话 ID（可选，用于继续对话）
    
    返回：
    - answer: AI 回答
    - conversation_id: 对话 ID
    - emotion: 当前情绪
    - emoji: 当前表情
    """
    session_id = request.args.get('session_id', 'default')
    if session_id not in sessions:
        sessions[session_id] = Session()

    session = sessions[session_id]
    data = request.json
    question = data.get('question', '')
    conversation_id = data.get('conversation_id')  # 可选，指定对话 ID

    if not question:
        return jsonify({'error': '问题不能为空'}), 400

    with session.lock:
        # 设置为思考状态
        session.buddy.update_by_action('ask')

        try:
            # 调用 AI，返回结果包含 answer 和 conversation_id
            result = ask_ai_with_context(question, conversation_id)
            answer = result['answer']
            conv_id = result['conversation_id']
        except Exception as e:
            return jsonify({
                'error': str(e),
                'emotion': session.buddy.get_emotion(),
                'emoji': session.buddy.get_emoji()
            }), 500

        # 设置为开心状态
        session.buddy.update_by_action('answer_received')

        return jsonify({
            'answer': answer,
            'conversation_id': conv_id,
            'emotion': session.buddy.get_emotion(),
            'emoji': session.buddy.get_emoji()
        })

# ==================== 学习计时器 API ====================

@app.route('/api/study/start', methods=['POST'])
def start_study():
    """
    开始学习
    
    启动计时器和番茄钟，同时启动 AI 监督（如果可用）
    """
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
            # 启动 AI 监督
            monitor_started = session.start_monitor()
            return jsonify({
                'success': True,
                'message': pomodoro_info['message'],
                'emotion': session.buddy.get_emotion(),
                'emoji': session.buddy.get_emoji(),
                'pomodoro': pomodoro_info,
                'monitor': {
                    'enabled': _monitor_enabled,
                    'started': monitor_started
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': '已在计时中'
            })

@app.route('/api/study/pause', methods=['POST'])
def pause_study():
    """
    暂停/继续学习
    
    如果正在学习则暂停，如果已暂停则继续
    """
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
    """
    停止学习
    
    停止计时器，记录学习时长，完成番茄钟，同时停止 AI 监督
    """
    session_id = request.args.get('session_id', 'default')
    if session_id not in sessions:
        sessions[session_id] = Session()
    
    session = sessions[session_id]
    
    with session.lock:
        # 停止 AI 监督
        session.stop_monitor()
        
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
    """
    重置会话
    
    重新初始化所有组件，包括 AI Monitor
    """
    session_id = request.args.get('session_id', 'default')
    if session_id not in sessions:
        sessions[session_id] = Session()
    
    session = sessions[session_id]
    
    with session.lock:
        # 先停止 AI 监督
        session.stop_monitor()
        
        session.supervisor = StudySupervisor()
        session.buddy = Buddy(session.supervisor)
        session.timer = StudyTimer()
        # 重新初始化 AI 监督器
        session._init_monitor()
        
        return jsonify({
            'success': True,
            'emotion': session.buddy.get_emotion(),
            'emoji': session.buddy.get_emoji()
        })

@app.route('/api/set_goal', methods=['POST'])
def set_goal_api():
    """
    设置每日学习目标
    
    请求体：
    - minutes: 目标分钟数
    """
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
    """
    开始休息
    
    番茄钟完成后进入休息模式
    """
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

@app.route('/api/timer', methods=['GET'])
def get_timer():
    """
    获取计时器状态
    
    返回当前计时器信息
    """
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
    """
    设置计时器目标时长
    
    请求体：
    - minutes: 目标分钟数
    """
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

# ==================== AI 监督专注度 API ====================

@app.route('/api/monitor/status', methods=['GET'])
def get_monitor_status():
    """
    获取 AI Monitor 状态
    
    返回：
    - enabled: 是否可用
    - running: 是否正在运行
    - state: 当前专注状态
    - score: 专注度评分
    """
    session_id = request.args.get('session_id', 'default')
    if session_id not in sessions:
        sessions[session_id] = Session()
    
    session = sessions[session_id]
    
    return jsonify({
        'enabled': _monitor_enabled,
        'running': session._monitor_running,
        'state': session.monitor.get_state() if session.monitor else None,
        'score': session.monitor.get_score() if session.monitor else None,
        'monitor_available': session.monitor is not None
    })

@app.route('/api/monitor/start', methods=['POST'])
def start_monitor():
    """
    启动 AI 监督
    
    开始监控专注度和行为
    """
    session_id = request.args.get('session_id', 'default')
    if session_id not in sessions:
        sessions[session_id] = Session()
    
    session = sessions[session_id]
    
    if not _monitor_enabled:
        return jsonify({
            'success': False,
            'error': 'AI Monitor 模块未启用'
        }), 400
    
    success = session.start_monitor()
    if success:
        return jsonify({
            'success': True,
            'message': 'AI 监督已启动'
        })
    return jsonify({
        'success': False,
        'error': '监督已在运行或初始化失败'
    })

@app.route('/api/monitor/stop', methods=['POST'])
def stop_monitor():
    """
    停止 AI 监督
    
    停止监控专注度
    """
    session_id = request.args.get('session_id', 'default')
    if session_id not in sessions:
        sessions[session_id] = Session()
    
    session = sessions[session_id]
    
    success = session.stop_monitor()
    if success:
        return jsonify({
            'success': True,
            'message': 'AI 监督已停止'
        })
    return jsonify({
        'success': False,
        'error': '监督未在运行'
    })

@app.route('/api/monitor/report', methods=['GET'])
def get_monitor_report():
    """
    获取专注度分析报告
    
    返回详细的专注度分析报告
    """
    session_id = request.args.get('session_id', 'default')
    if session_id not in sessions:
        sessions[session_id] = Session()
    
    session = sessions[session_id]
    
    if session.monitor is None:
        return jsonify({
            'success': False,
            'error': 'AI Monitor 未初始化'
        }), 400
    
    try:
        report = session.monitor.get_report()
        return jsonify({
            'success': True,
            'report': report
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/monitor/camera', methods=['GET'])
def get_camera_frame():
    """
    获取摄像头画面（用于实时显示）
    
    返回 base64 编码的图像
    """
    session_id = request.args.get('session_id', 'default')
    if session_id not in sessions:
        sessions[session_id] = Session()
    
    session = sessions[session_id]
    
    if session.monitor is None:
        return jsonify({
            'success': False,
            'error': 'AI Monitor 未初始化'
        }), 400
    
    try:
        frame = session.get_monitor_camera_frame()
        if frame is None:
            return jsonify({
                'success': False,
                'error': '无法获取摄像头画面'
            }), 400
        
        import base64
        import cv2
        import numpy as np
        
        # 将 OpenCV 图像转换为 base64
        _, buffer = cv2.imencode('.jpg', frame)
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'success': True,
            'frame': frame_base64
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/monitor/focus', methods=['GET'])
def get_focus_data():
    """
    获取专注度数据（用于前端显示）
    
    返回专注度状态和评分
    """
    session_id = request.args.get('session_id', 'default')
    if session_id not in sessions:
        sessions[session_id] = Session()
    
    session = sessions[session_id]
    
    focus_status = session.get_focus_status()
    if focus_status is None:
        return jsonify({
            'success': True,
            'enabled': _monitor_enabled,
            'monitor_available': session.monitor is not None,
            'focus': None
        })
    
    return jsonify({
        'success': True,
        'enabled': _monitor_enabled,
        'focus': focus_status
    })

# ==================== 任务管理 API ====================

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """
    获取所有任务
    
    查询参数：
    - status: 任务状态 (all/pending/completed)
    """
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
    """
    添加新任务
    
    请求体：
    - title: 任务标题（必填）
    - description: 任务描述
    - deadline: 截止时间 (YYYY-MM-DD HH:MM 格式)
    """
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
    """
    更新任务
    
    请求体：
    - title: 任务标题
    - description: 任务描述
    - deadline: 截止时间
    - completed: 是否完成
    """
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
    """
    完成任务
    
    完成任务时触发成就系统
    """
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
    """
    删除任务
    """
    session_id = request.args.get('session_id', 'default')
    if session_id not in sessions:
        sessions[session_id] = Session()
    
    session = sessions[session_id]
    success = session.buddy.task_manager.delete_task(task_id)
    return jsonify({'success': success})

@app.route('/api/tasks/stats', methods=['GET'])
def get_task_stats():
    """
    获取任务统计信息
    """
    session_id = request.args.get('session_id', 'default')
    if session_id not in sessions:
        sessions[session_id] = Session()
    
    session = sessions[session_id]
    stats = session.buddy.task_manager.get_stats()
    return jsonify({'success': True, 'stats': stats})

@app.route('/api/tasks/reminders', methods=['GET'])
def get_task_reminders():
    """
    获取任务提醒
    
    返回即将到期的任务
    """
    session_id = request.args.get('session_id', 'default')
    if session_id not in sessions:
        sessions[session_id] = Session()
    
    session = sessions[session_id]
    reminders = session.buddy.task_manager.check_reminders()
    return jsonify({'success': True, 'reminders': reminders})

# ==================== 学习日历 API ====================

@app.route('/api/calendar', methods=['GET'])
def get_calendar():
    """
    获取日历数据
    
    查询参数：
    - year: 年份
    - month: 月份
    
    返回指定月份的学习记录
    """
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
            'entries': entries
        })
    
    return jsonify({
        'success': True,
        'calendar': calendar_data,
        'daily_goal': goal_minutes,
        'year': year,
        'month': month
    })

@app.route('/api/calendar/stats', methods=['GET'])
def get_calendar_stats():
    """
    获取学习日历统计
    """
    session_id = request.args.get('session_id', 'default')
    if session_id not in sessions:
        sessions[session_id] = Session()
    
    session = sessions[session_id]
    stats = session.buddy.get_calendar_stats()
    return jsonify({'success': True, 'stats': stats})

@app.route('/api/calendar/log', methods=['POST'])
def log_study():
    """
    手动记录学习
    
    请求体：
    - duration: 学习时长（分钟）
    - subject: 学习科目
    """
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
    """
    获取学习历史
    
    查询参数：
    - days: 最近几天
    """
    session_id = request.args.get('session_id', 'default')
    if session_id not in sessions:
        sessions[session_id] = Session()
    
    session = sessions[session_id]
    days = request.args.get('days', 7, type=int)
    activity = session.buddy.study_calendar.get_recent_activity(days)
    return jsonify({'success': True, 'history': activity})

# ==================== 统计 API ====================

@app.route('/api/stats', methods=['GET'])
def get_all_stats():
    """
    获取所有统计数据
    
    包含：
    - 伙伴学习统计
    - 日历统计
    - 任务统计
    - 番茄钟统计
    """
    session_id = request.args.get('session_id', 'default')
    if session_id not in sessions:
        sessions[session_id] = Session()
    
    session = sessions[session_id]
    
    buddy_stats = session.buddy.get_study_stats()
    calendar_stats = session.buddy.get_calendar_stats()
    task_stats = session.buddy.task_manager.get_stats()
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

# ==================== 用户设置 API ====================

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
    """
    设置座右铭
    
    请求体：
    - motto: 座右铭内容
    """
    data = request.json
    motto = data.get('motto', '').strip()
    
    if set_motto(motto):
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
    """
    设置喜欢的激励语录
    
    请求体：
    - quote: 语录内容
    """
    data = request.json
    quote = data.get('quote', '').strip()
    
    if set_favorite_quote(quote):
        session_id = request.args.get('session_id', 'default')
        if session_id in sessions:
            sessions[session_id].favorite_quote = quote
        return jsonify({
            'success': True,
            'message': '激励语录已更新',
            'quote': quote
        })
    return jsonify({'success': False, 'error': '保存失败'}), 500

# ==================== AI 历史记录 API ====================

@app.route('/api/ai/history', methods=['GET'])
def get_ai_history():
    """获取所有 AI 对话历史列表"""
    conversations = get_ai_conversations()
    return jsonify({
        'success': True,
        'conversations': conversations
    })

@app.route('/api/ai/history/<conversation_id>', methods=['GET'])
def get_ai_conversation(conversation_id):
    """获取指定对话的详细消息"""
    messages = get_conversation_messages(conversation_id)
    return jsonify({
        'success': True,
        'conversation_id': conversation_id,
        'messages': messages
    })

@app.route('/api/ai/history', methods=['POST'])
def create_ai_conversation():
    """创建新对话"""
    data = request.json or {}
    title = data.get('title')
    conv_id = new_ai_conversation()
    return jsonify({
        'success': True,
        'conversation_id': conv_id,
        'message': '新对话已创建'
    })

@app.route('/api/ai/history/<conversation_id>', methods=['DELETE'])
def delete_ai_history(conversation_id):
    """删除指定对话"""
    success = delete_ai_conversation(conversation_id)
    return jsonify({
        'success': success,
        'message': '对话已删除' if success else '对话不存在'
    })

@app.route('/api/ai/stats', methods=['GET'])
def get_ai_stats():
    """获取 AI 使用统计"""
    from src.ai.ai_helper import get_ai_instance
    ai = get_ai_instance()
    stats = ai.get_ai_stats()
    return jsonify({
        'success': True,
        'stats': stats
    })

# ==================== 学习计划 API ====================

@app.route('/api/plans', methods=['GET'])
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

@app.route('/api/plans', methods=['POST'])
def create_study_plan():
    """
    创建学习计划
    
    请求体：
    - subject: 科目名称（必填）
    - exam_date: 考试日期（必填）
    - daily_hours: 每日学习时长（小时）
    - use_ai: 是否使用 AI 生成
    """
    from src.modules.plan_generator import get_plan_generator
    generator = get_plan_generator()
    
    data = request.json
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

@app.route('/api/plans/<int:plan_id>', methods=['GET'])
def get_study_plan(plan_id):
    """获取指定学习计划"""
    from src.modules.plan_generator import get_plan_generator
    generator = get_plan_generator()
    
    plan = generator.get_plan(plan_id)
    if plan:
        return jsonify({'success': True, 'plan': plan.to_dict()})
    return jsonify({'success': False, 'error': '计划不存在'}), 404

@app.route('/api/plans/<int:plan_id>', methods=['PUT'])
def update_study_plan(plan_id):
    """
    更新学习计划
    
    请求体：
    - completed: 是否完成
    """
    from src.modules.plan_generator import get_plan_generator
    generator = get_plan_generator()
    
    data = request.json
    plan = generator.get_plan(plan_id)
    if plan:
        if data.get('completed'):
            plan.mark_complete()
        generator._save_plans()
        return jsonify({'success': True, 'plan': plan.to_dict()})
    return jsonify({'success': False, 'error': '计划不存在'}), 404

@app.route('/api/plans/<int:plan_id>', methods=['DELETE'])
def delete_study_plan(plan_id):
    """删除学习计划"""
    from src.modules.plan_generator import get_plan_generator
    generator = get_plan_generator()
    
    success = generator.delete_plan(plan_id)
    return jsonify({'success': success})

@app.route('/api/plans/expiring', methods=['GET'])
def get_expiring_plans():
    """
    获取即将到期的学习计划
    
    查询参数：
    - days: 剩余天数阈值
    """
    from src.modules.plan_generator import get_plan_generator
    generator = get_plan_generator()
    
    days = request.args.get('days', 7, type=int)
    plans = generator.get_expiring_plans(days)
    
    return jsonify({
        'success': True,
        'plans': [p.to_dict() for p in plans]
    })

# ==================== 成就系统 API ====================

@app.route('/api/achievements', methods=['GET'])
def get_achievements():
    """获取用户成就"""
    from src.modules.achievements import get_achievements_data
    data = get_achievements_data()
    return jsonify({
        'success': True,
        'achievements': data
    })

@app.route('/api/achievements/unlock', methods=['POST'])
def unlock_achievement():
    """解锁成就（由系统触发）"""
    from src.modules.achievements import unlock_achievement as do_unlock
    data = request.json
    achievement_id = data.get('achievement_id')
    if do_unlock(achievement_id):
        return jsonify({'success': True, 'message': '成就解锁！'})
    return jsonify({'success': False, 'message': '成就已存在'}), 400

# ==================== 通知设置 API ====================

@app.route('/api/notification/check', methods=['GET'])
def check_notification_permission():
    """检查通知权限状态"""
    return jsonify({
        'success': True,
        'permission': 'granted'
    })

@app.route('/api/notification/settings', methods=['GET'])
def get_notification_settings():
    """获取通知设置"""
    from src.modules.data_manager import get_data_manager
    dm = get_data_manager()
    data = dm.get_data()
    return jsonify({
        'success': True,
        'settings': {
            'pomodoro_complete': data.get('notification_pomodoro', True),
            'goal_reached': data.get('notification_goal', True),
            'task_reminder': data.get('notification_task', True)
        }
    })

@app.route('/api/notification/settings', methods=['POST'])
def set_notification_settings():
    """
    设置通知选项
    
    请求体：
    - pomodoro_complete: 番茄钟完成通知
    - goal_reached: 达成目标通知
    - task_reminder: 任务提醒
    """
    from src.modules.data_manager import get_data_manager
    dm = get_data_manager()
    data = request.json

    settings = {
        'notification_pomodoro': data.get('pomodoro_complete', True),
        'notification_goal': data.get('goal_reached', True),
        'notification_task': data.get('task_reminder', True)
    }

    dm.update_settings(**settings)
    return jsonify({
        'success': True,
        'message': '通知设置已更新',
        'settings': settings
    })

# ==================== 应用启动 ====================

if __name__ == '__main__':
    """
    应用入口
    
    启动 Flask 开发服务器
    访问地址：http://localhost:5000
    """
    app.run(debug=True, port=5000)
