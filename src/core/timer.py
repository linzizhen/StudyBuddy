"""
StudyPal 学习计时器
增强版学习监督功能，包含番茄钟、目标设置、进度跟踪等

作者：StudyPal
创建日期：2026-04-13
"""

import time
from datetime import datetime, timedelta
from config import DEFAULT_TIMER_MINUTES


class StudyTimer:
    """
    学习计时器类
    
    功能：
    - 记录学习时长
    - 支持暂停/继续
    - 目标时长设置
    - 完成检测
    """
    
    def __init__(self, duration_minutes=DEFAULT_TIMER_MINUTES):
        """
        初始化计时器
        
        参数：
            duration_minutes: 目标学习时长（分钟），默认 25 分钟（番茄钟）
        """
        self._target_minutes = duration_minutes  # 目标时长
        self._start_time = None       # 开始时间
        self._pause_time = None       # 暂停时间
        self._paused_seconds = 0      # 累计暂停时长
        self._is_running = False      # 是否正在运行
        self._is_finished = False     # 是否已完成
    
    def start(self):
        """
        开始计时
        
        返回：
            True 表示开始成功，False 表示已在运行
        """
        if self._is_running:
            return False
        
        self._start_time = time.time()
        self._is_running = True
        self._is_finished = False
        return True
    
    def stop(self):
        """
        结束计时
        
        返回：
            学习时长（分钟）
        """
        if not self._is_running:
            return self.get_current_duration()
        
        # 计算总时长
        total_seconds = self.get_current_duration() * 60
        self._is_running = False
        self._is_finished = total_seconds >= self._target_minutes * 60
        
        # 重置状态
        self._start_time = None
        self._pause_time = None
        self._paused_seconds = 0
        
        return total_seconds / 60
    
    def pause(self):
        """
        暂停计时
        
        返回：
            True 表示暂停成功，False 表示未在运行
        """
        if not self._is_running:
            return False
        
        self._pause_time = time.time()
        self._is_running = False
        return True
    
    def resume(self):
        """
        继续计时
        
        返回：
            True 表示继续成功，False 表示未在暂停状态
        """
        if self._is_running or self._pause_time is None:
            return False
        
        # 累加暂停时长
        pause_duration = time.time() - self._pause_time
        self._paused_seconds += pause_duration
        self._pause_time = None
        self._is_running = True
        return True
    
    def get_current_duration(self):
        """
        获取当前已学时长（分钟）
        
        返回：
            已学习时长（分钟，浮点数）
        """
        if self._start_time is None:
            return 0
        
        if self._is_running:
            # 计算当前已过去的秒数
            elapsed = time.time() - self._start_time - self._paused_seconds
        else:
            # 已暂停，计算到暂停时的时长
            elapsed = self._pause_time - self._start_time - self._paused_seconds
        
        return elapsed / 60  # 转换为分钟
    
    def get_remaining(self):
        """
        获取剩余时长（分钟）
        
        返回：
            剩余学习时长（分钟）
        """
        current = self.get_current_duration()
        remaining = self._target_minutes - current
        return max(0, remaining)
    
    def is_finished(self):
        """
        检查是否已完成学习（达到目标时长）
        
        返回：
            True 表示已完成，False 表示未完成
        """
        return self.get_current_duration() >= self._target_minutes
    
    def check_finish(self):
        """
        检查是否完成，返回完成信号
        
        返回：
            True 表示刚刚完成（触发完成事件）
        """
        if not self._is_finished and self.is_finished():
            self._is_finished = True
            return True
        return False
    
    def reset(self):
        """
        重置计时器
        """
        self._start_time = None
        self._pause_time = None
        self._paused_seconds = 0
        self._is_running = False
        self._is_finished = False
    
    def set_target(self, minutes):
        """
        设置目标时长
        
        参数：
            minutes: 新的目标时长（分钟）
        """
        self._target_minutes = minutes
    
    def __str__(self):
        """
        字符串表示
        
        返回：
            字符串形式的状态描述
        """
        if self._is_running:
            status = "🟢 进行中"
        elif self._pause_time:
            status = "🟡 已暂停"
        else:
            status = "⚫ 未开始"
        
        current = self.get_current_duration()
        return f"StudyTimer: {current:.1f}/{self._target_minutes}分钟 ({status})"


class StudySupervisor:
    """
    学习监督器类
    
    功能：
    - 番茄钟模式
    - 学习目标设置
    - 进度跟踪
    - 休息提醒
    - 空闲检测
    """
    
    def __init__(self):
        """初始化监督器"""
        # 番茄钟设置
        self._pomodoro_study_minutes = 25  # 学习时长
        self._pomodoro_break_minutes = 5   # 休息时长
        self._current_pomodoro_cycle = 0   # 当前番茄钟周期
        self._is_break_mode = False        # 是否在休息模式
        
        # 学习目标
        self._daily_goal_minutes = 120     # 每日目标（分钟），默认 2 小时
        self._today_study_minutes = 0      # 今日已学习时长
        self._today_start_date = datetime.now().date()  # 今日日期
        
        # 进度跟踪
        self._completed_pomodoros = 0      # 已完成的番茄钟数量
        self._session_history = []         # 学习会话历史
        
        # 休息提醒
        self._last_break_time = datetime.now()  # 上次休息时间
        self._max_continuous_minutes = 50  # 最大连续学习时长（分钟）
        self._should_remind_break = False  # 是否应该提醒休息
        
        # 空闲检测
        self._last_activity_time = datetime.now()  # 最后活动时间
        self._idle_warning_time = 30       # 空闲警告时间（分钟）
        self._idle_alert_time = 60         # 空闲警报时间（分钟）
    
    def set_daily_goal(self, minutes):
        """
        设置每日学习目标
        
        参数：
            minutes: 目标时长（分钟）
        """
        self._daily_goal_minutes = minutes
    
    def start_pomodoro(self):
        """
        开始番茄钟模式
        
        返回：
            包含番茄钟信息的字典
        """
        self._is_break_mode = False
        self._current_pomodoro_cycle += 1
        return {
            'mode': 'study',
            'cycle': self._current_pomodoro_cycle,
            'duration': self._pomodoro_study_minutes,
            'message': f'第{self._current_pomodoro_cycle}个番茄钟，加油！📚'
        }
    
    def start_break(self):
        """
        开始休息
        
        返回：
            包含休息信息的字典
        """
        self._is_break_mode = True
        self._last_break_time = datetime.now()
        return {
            'mode': 'break',
            'duration': self._pomodoro_break_minutes,
            'message': '休息一下吧！站起来活动活动~ 💪'
        }
    
    def complete_pomodoro(self):
        """
        完成一个番茄钟
        
        返回：
            包含完成信息的字典
        """
        self._completed_pomodoros += 1
        self._is_break_mode = False
        
        # 每 4 个番茄钟后长休息
        if self._completed_pomodoros % 4 == 0:
            self._pomodoro_break_minutes = 15
            message = '太棒了！完成 4 个番茄钟，来个长休息吧！🎉'
        else:
            self._pomodoro_break_minutes = 5
            message = '完成一个番茄钟！真棒！🎉'
        
        return {
            'completed': self._completed_pomodoros,
            'cycle': self._current_pomodoro_cycle,
            'message': message,
            'next_break': self._pomodoro_break_minutes
        }
    
    def check_idle_time(self):
        """
        检测空闲时间（是否在玩手机）
        
        返回：
            包含空闲状态的字典
        """
        now = datetime.now()
        idle_minutes = (now - self._last_activity_time).total_seconds() / 60
        
        status = 'ok'
        message = ''
        
        if idle_minutes >= self._idle_alert_time:
            status = 'alert'
            message = f'你已经 {idle_minutes:.0f} 分钟没学习了！别玩手机啦！😡'
        elif idle_minutes >= self._idle_warning_time:
            status = 'warning'
            message = f'你已经 {idle_minutes:.0f} 分钟没学习了，该开始学习了！😢'
        
        return {
            'idle_minutes': idle_minutes,
            'status': status,
            'message': message
        }
    
    def record_activity(self):
        """
        记录一次活动，重置空闲计时
        """
        self._last_activity_time = datetime.now()
    
    def check_break_reminder(self):
        """
        检查是否需要提醒休息
        
        返回：
            是否需要提醒
        """
        if self._is_break_mode:
            return False
        
        continuous_minutes = (datetime.now() - self._last_break_time).total_seconds() / 60
        
        if continuous_minutes >= self._max_continuous_minutes:
            self._should_remind_break = True
            return True
        
        return False
    
    def get_break_reminder_message(self):
        """
        获取休息提醒消息
        
        返回：
            休息提醒消息字符串
        """
        continuous_minutes = (datetime.now() - self._last_break_time).total_seconds() / 60
        return f'你已经连续学习了 {continuous_minutes:.0f} 分钟，站起来活动一下吧！💪'
    
    def get_progress(self):
        """
        获取今日学习进度
        
        返回：
            包含进度信息的字典
        """
        # 检查是否是新的一天
        today = datetime.now().date()
        if today != self._today_start_date:
            self._today_start_date = today
            self._today_study_minutes = 0
            self._completed_pomodoros = 0
            self._last_break_time = datetime.now()
        
        progress_percent = min(100, (self._today_study_minutes / self._daily_goal_minutes) * 100)
        
        # 检查是否达到目标
        reached_goal = self._today_study_minutes >= self._daily_goal_minutes
        
        return {
            'today_minutes': self._today_study_minutes,
            'goal_minutes': self._daily_goal_minutes,
            'progress_percent': progress_percent,
            'completed_pomodoros': self._completed_pomodoros,
            'reached_goal': reached_goal,
            'remaining_minutes': max(0, self._daily_goal_minutes - self._today_study_minutes)
        }
    
    def add_study_time(self, minutes):
        """
        添加学习时长
        
        参数：
            minutes: 学习时长（分钟）
        """
        self._today_study_minutes += minutes
        self._last_break_time = datetime.now()  # 重置休息计时
        self.record_activity()
    
    def get_status(self):
        """
        获取完整状态信息
        
        返回：
            包含所有状态的字典
        """
        progress = self.get_progress()
        idle_status = self.check_idle_time()
        needs_break = self.check_break_reminder()
        
        return {
            'progress': progress,
            'idle': idle_status,
            'needs_break': needs_break,
            'break_message': self.get_break_reminder_message() if needs_break else '',
            'pomodoro': {
                'cycle': self._current_pomodoro_cycle,
                'completed': self._completed_pomodoros,
                'is_break_mode': self._is_break_mode
            }
        }
    
    def reset_today(self):
        """
        重置今日数据
        """
        self._today_study_minutes = 0
        self._completed_pomodoros = 0
        self._today_start_date = datetime.now().date()
        self._last_break_time = datetime.now()
        self._should_remind_break = False
    
    def __str__(self):
        """
        字符串表示
        
        返回：
            字符串形式的状态描述
        """
        progress = self.get_progress()
        return f"StudySupervisor: 今日{progress['today_minutes']}/{progress['goal_minutes']}min ({progress['progress_percent']:.0f}%)"
