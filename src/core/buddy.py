"""
StudyBuddy 情绪管理类
管理宠物的情绪状态和表情变化

情绪状态列表：
- idle(😴): 空闲/休息状态 - 默认状态
- happy(😊): 开心/完成任务
- sad(😢): 难过/太久没学习
- study(📚): 学习中
- thinking(🤔): 思考/AI 回答中
- angry(😡): 生气/用户一直玩手机时
- excited(🎉): 兴奋/完成学习目标时
- sleepy(😪): 困倦/深夜学习时
- proud(😤): 自豪/用户坚持学习时
"""

from datetime import datetime
from config import EMOJIS, DAILY_GOAL_MINUTES
from src.modules.task_manager import TaskManager
from src.modules.study_calendar import StudyCalendar


class Buddy:
    """StudyBuddy 宠物类，负责管理情绪状态"""
    
    def __init__(self, supervisor=None):
        """
        初始化宠物，默认情绪为 idle（空闲）
        
        参数:
            supervisor: StudySupervisor 实例，用于联动
        """
        self._current_emotion = "idle"  # 当前情绪名称
        self._emotion_history = []      # 情绪变化历史记录
        self._last_activity_time = datetime.now()  # 最后活动时间
        self._study_duration = 0  # 累计学习时长（分钟）
        self._consecutive_study_sessions = 0  # 连续学习次数
        self._supervisor = supervisor  # 学习监督器引用
        
        # 任务管理
        self.task_manager = TaskManager()
        
        # 学习日历
        self.study_calendar = StudyCalendar()
    
    def set_emotion(self, emotion_name):
        """
        设置宠物的情绪状态
        
        参数:
            emotion_name: 情绪名称 (idle/happy/sad/study/thinking/angry/excited/sleepy/proud)
        """
        # 记录旧情绪到历史
        if self._current_emotion != emotion_name:
            self._emotion_history.append({
                "from": self._current_emotion,
                "to": emotion_name,
                "time": datetime.now().isoformat()
            })
        
        # 更新情绪
        self._current_emotion = emotion_name
    
    def get_emotion(self):
        """
        获取当前情绪名称
        
        返回:
            当前情绪名称字符串
        """
        return self._current_emotion
    
    def get_emoji(self):
        """
        获取当前情绪的 emoji 字符
        
        返回:
            对应的 emoji 字符
        """
        return EMOJIS.get(self._current_emotion, "❓")
    
    def get_image_path(self):
        """
        获取当前情绪对应的图片路径（预留接口）
        
        返回:
            图片文件路径字符串
        """
        return f"assets/{self._current_emotion}.png"
    
    def update_by_action(self, action):
        """
        根据用户动作自动更新情绪
        
        参数:
            action: 动作名称
                - "ask": 提问 -> 进入思考状态
                - "answer_received": 收到回答 -> 开心
                - "study_start": 开始学习 -> 学习状态
                - "study_finish": 完成学习 -> 兴奋
                - "idle_too_long": 太久没动作 -> 难过
                - "phone_addiction": 一直玩手机 -> 生气
                - "late_night": 深夜学习 -> 困倦
                - "proud_moment": 坚持学习 -> 自豪
        """
        action_map = {
            "ask": "thinking",
            "answer_received": "happy",
            "study_start": "study",
            "study_finish": "excited",  # 完成学习改为兴奋
            "idle_too_long": "sad",
            "phone_addiction": "angry",
            "late_night": "sleepy",
            "proud_moment": "proud"
        }
        
        if action in action_map:
            self.set_emotion(action_map[action])
            self._last_activity_time = datetime.now()
    
    def check_time_based_emotion(self):
        """
        根据时间和活动情况自动更新情绪
        
        返回:
            是否需要更新情绪
        """
        now = datetime.now()
        hours_since_activity = (now - self._last_activity_time).total_seconds() / 3600
        
        # 检查是否深夜学习 (23:00 - 6:00)
        current_hour = now.hour
        if current_hour >= 23 or current_hour <= 5:
            if self._current_emotion == "study":
                self.set_emotion("sleepy")
                return True
        
        # 检查是否太久没活动 (超过 30 分钟)
        if hours_since_activity > 0.5:
            if self._current_emotion in ["idle", "happy"]:
                self.set_emotion("sad")
                return True
        
        # 检查是否一直玩手机 (太久没学习，超过 2 小时)
        if hours_since_activity > 2:
            if self._current_emotion == "idle":
                self.set_emotion("angry")
                return True
        
        # 与 StudySupervisor 联动
        if self._supervisor:
            idle_status = self._supervisor.check_idle_time()
            if idle_status['status'] == 'alert':
                self.set_emotion("angry")
                return True
            elif idle_status['status'] == 'warning':
                self.set_emotion("sad")
                return True
        
        return False
    
    def update_by_supervisor(self, supervisor_status):
        """
        根据 StudySupervisor 的状态更新情绪
        
        参数:
            supervisor_status: StudySupervisor.get_status() 返回的字典
        
        返回:
            是否需要更新情绪
        """
        updated = False
        
        # 检查空闲状态
        idle_status = supervisor_status.get('idle', {})
        if idle_status.get('status') == 'alert':
            self.set_emotion("angry")
            updated = True
        elif idle_status.get('status') == 'warning':
            self.set_emotion("sad")
            updated = True
        
        # 检查是否需要休息
        if supervisor_status.get('needs_break'):
            if self._current_emotion == "study":
                self.set_emotion("sleepy")  # 用困倦表示需要休息
                updated = True
        
        # 检查是否达到目标
        progress = supervisor_status.get('progress', {})
        if progress.get('reached_goal') and self._current_emotion != "excited":
            self.set_emotion("excited")
            updated = True
        
        return updated
    
    def record_study_session(self, duration_minutes):
        """
        记录一次学习会话
        
        参数:
            duration_minutes: 学习时长（分钟）
        """
        self._study_duration += duration_minutes
        self._consecutive_study_sessions += 1
        self._last_activity_time = datetime.now()
        
        # 如果连续学习 3 次以上，显示自豪情绪
        if self._consecutive_study_sessions >= 3:
            self.set_emotion("proud")
        
        # 通知 StudySupervisor
        if self._supervisor:
            self._supervisor.add_study_time(duration_minutes)
    
    def on_pomodoro_complete(self):
        """
        番茄钟完成时的回调
        
        返回:
            是否更新了情绪
        """
        self.set_emotion("excited")
        self._last_activity_time = datetime.now()
        return True
    
    def on_goal_reached(self):
        """
        达到日目标时的回调
        
        返回:
            是否更新了情绪
        """
        self.set_emotion("proud")
        self._last_activity_time = datetime.now()
        return True
    
    def get_study_stats(self):
        """
        获取学习统计数据
        
        返回:
            包含学习统计的字典
        """
        return {
            "total_minutes": self._study_duration,
            "consecutive_sessions": self._consecutive_study_sessions
        }
    
    def on_task_complete(self, task_title):
        """
        任务完成时的回调
        
        参数:
            task_title: 完成的任务标题
        
        返回:
            是否更新了情绪
        """
        self.set_emotion("happy")
        self._last_activity_time = datetime.now()
        
        # 检查是否完成今日所有任务
        stats = self.task_manager.get_stats()
        if stats["pending"] == 0 and stats["completed"] > 0:
            self.set_emotion("excited")
        
        return True
    
    def check_task_reminders(self):
        """
        检查任务提醒
        
        返回:
            提醒信息字典
        """
        return self.task_manager.check_reminders()
    
    def get_calendar_stats(self):
        """
        获取学习日历统计
        
        返回:
            统计信息字典
        """
        return self.study_calendar.get_stats()
    
    def log_study_session(self, duration_minutes):
        """
        记录学习会话到日历
        
        参数:
            duration_minutes: 学习时长（分钟）
        """
        self.study_calendar.log_study(duration_minutes)
        
        # 检查是否达到每日目标
        today_duration = self.study_calendar.get_today_duration()
        if today_duration >= DAILY_GOAL_MINUTES:
            self.set_emotion("excited")
    
    def get_emotion_description(self):
        """
        获取当前情绪的描述文字
        
        返回:
            情绪描述字符串
        """
        descriptions = {
            "idle": "休息一下~",
            "happy": "好开心！",
            "sad": "有点难过...",
            "study": "学习中！",
            "thinking": "思考中...",
            "angry": "生气！别玩手机了！",
            "excited": "太棒了！🎉",
            "sleepy": "好困啊...",
            "proud": "为你骄傲！😤"
        }
        return descriptions.get(self._current_emotion, "未知状态")
    
    def get_history(self):
        """
        获取情绪变化历史（可选功能）
        
        返回:
            情绪变化历史记录列表
        """
        return self._emotion_history
    
    def reset(self):
        """
        重置所有状态到初始值
        """
        self._current_emotion = "idle"
        self._emotion_history = []
        self._last_activity_time = datetime.now()
        self._study_duration = 0
        self._consecutive_study_sessions = 0
    
    def __str__(self):
        """字符串表示，显示当前状态"""
        return f"Buddy[{self._current_emotion}]: {self.get_emoji()}"
