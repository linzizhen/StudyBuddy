"""
提醒模块
负责输出各种提醒信息
"""

import time
import logging
from typing import Dict, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class ReminderLevel(Enum):
    """提醒级别"""
    INFO = "info"
    WARNING = "warning"
    ALERT = "alert"
    CRITICAL = "critical"


class Notifier:
    """提醒器类"""
    
    def __init__(self, config: Dict = None):
        """
        初始化提醒器
        
        Args:
            config: 提醒配置
        """
        from .config import NOTIFIER_CONFIG
        
        self.config = config or NOTIFIER_CONFIG
        
        # 消息模板
        self.messages = self.config.get("messages", {})
        
        # 提醒间隔
        self.reminder_interval = self.config.get("reminder_interval", 60)
        
        # 最后提醒时间记录
        self.last_reminders: Dict[str, float] = {
            "focused": 0,
            "normal": 0,
            "distracted": 0,
            "away": 0,
            "switch_warning": 0,
            "learning_detected": 0
        }
        
        # 是否启用各类提醒
        self.enable_focus = self.config.get("enable_focus_reminder", True)
        self.enable_distraction = self.config.get("enable_distraction_alert", True)
        self.enable_leave = self.config.get("enable_leave_alert", True)
        self.enable_report = self.config.get("enable_report", True)
    
    def _can_remind(self, reminder_type: str) -> bool:
        """
        检查是否可以发送提醒
        
        Args:
            reminder_type: 提醒类型
            
        Returns:
            是否可以发送
        """
        current_time = time.time()
        last_time = self.last_reminders.get(reminder_type, 0)
        
        if current_time - last_time < self.reminder_interval:
            return False
        
        self.last_reminders[reminder_type] = current_time
        return True
    
    def _format_message(self, template: str, data: Dict = None) -> str:
        """
        格式化消息
        
        Args:
            template: 消息模板
            data: 数据字典
            
        Returns:
            格式化后的消息
        """
        if data is None:
            data = {}
        
        try:
            return template.format(**data)
        except (KeyError, ValueError):
            return template
    
    def notify_focused(self, data: Optional[Dict] = None) -> bool:
        """
        发送专注提醒
        
        Args:
            data: 数据字典
            
        Returns:
            是否发送成功
        """
        if not self.enable_focus:
            return False
        
        if not self._can_remind("focused"):
            return False
        
        message = self.messages.get("focused", "专注中")
        print(message)
        logger.info(f"提醒: {message}")
        return True
    
    def notify_normal(self, data: Optional[Dict] = None) -> bool:
        """
        发送一般状态提醒
        
        Args:
            data: 数据字典
            
        Returns:
            是否发送成功
        """
        if not self.enable_focus:
            return False
        
        if not self._can_remind("normal"):
            return False
        
        message = self.messages.get("normal", "状态一般")
        print(message)
        logger.info(f"提醒: {message}")
        return True
    
    def notify_distracted(self, data: Optional[Dict] = None) -> bool:
        """
        发送分心提醒
        
        Args:
            data: 数据字典
            
        Returns:
            是否发送成功
        """
        if not self.enable_distraction:
            return False
        
        if not self._can_remind("distracted"):
            return False
        
        message = self.messages.get("distracted", "状态分心")
        print(message)
        logger.warning(f"提醒: {message}")
        return True
    
    def notify_away(self, data: Optional[Dict] = None) -> bool:
        """
        发送离开提醒
        
        Args:
            data: 数据字典
            
        Returns:
            是否发送成功
        """
        if not self.enable_leave:
            return False
        
        if not self._can_remind("away"):
            return False
        
        message = self.messages.get("away", "检测到已离开")
        print(message)
        logger.warning(f"提醒: {message}")
        return True
    
    def notify_learning_detected(self, data: Optional[Dict] = None) -> bool:
        """
        发送检测到学习软件提醒
        
        Args:
            data: 数据字典
            
        Returns:
            是否发送成功
        """
        if not self.enable_focus:
            return False
        
        if not self._can_remind("learning_detected"):
            return False
        
        message = self.messages.get("learning_detected", "检测到学习软件")
        print(message)
        logger.info(f"提醒: {message}")
        return True
    
    def notify_switch_warning(self, data: Optional[Dict] = None) -> bool:
        """
        发送切换频繁提醒
        
        Args:
            data: 数据字典
            
        Returns:
            是否发送成功
        """
        if not self.enable_distraction:
            return False
        
        if not self._can_remind("switch_warning"):
            return False
        
        message = self.messages.get("switch_warning", "切换频繁")
        print(message)
        logger.warning(f"提醒: {message}")
        return True
    
    def notify_report(self, report: Dict) -> bool:
        """
        输出分析报告
        
        Args:
            report: 报告字典
            
        Returns:
            是否成功
        """
        if not self.enable_report:
            return False
        
        print("\n" + "=" * 50)
        print("学习专注度报告")
        print("=" * 50)
        
        # 格式化时间
        def format_time(seconds):
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            if hours > 0:
                return f"{hours}小时{minutes}分钟{secs}秒"
            elif minutes > 0:
                return f"{minutes}分钟{secs}秒"
            else:
                return f"{secs}秒"
        
        print(f"会话时长: {format_time(report.get('session_duration', 0))}")
        print(f"专注时间: {format_time(report.get('total_focused_time', 0))} ({report.get('focused_ratio', 0):.1f}%)")
        print(f"一般时间: {format_time(report.get('total_normal_time', 0))} ({report.get('normal_ratio', 0):.1f}%)")
        print(f"分心时间: {format_time(report.get('total_distracted_time', 0))} ({report.get('distracted_ratio', 0):.1f}%)")
        print("-" * 50)
        
        # 评分详情
        score_details = report.get('score_details', {})
        print("评分详情:")
        print(f"  - 人脸检测: {score_details.get('face_score', 0):.1f}分")
        print(f"  - 学习窗口: {score_details.get('window_score', 0):.1f}分")
        print(f"  - 切换频率: {score_details.get('switch_score', 0):.1f}分")
        print(f"  - 专注时间: {score_details.get('time_score', 0):.1f}分")
        print(f"  总分: {report.get('current_score', 0):.1f}/100")
        print("=" * 50 + "\n")
        
        logger.info("报告已输出")
        return True
    
    def notify_state_change(self, old_state: str, new_state: str, score: float) -> bool:
        """
        通知状态变化
        
        Args:
            old_state: 旧状态
            new_state: 新状态
            score: 当前评分
            
        Returns:
            是否成功
        """
        message = f"状态变化: {old_state} → {new_state} (评分: {score:.1f})"
        print(message)
        logger.info(message)
        return True
    
    def reset_reminder_cooldowns(self):
        """重置提醒冷却时间"""
        current_time = time.time()
        for key in self.last_reminders:
            self.last_reminders[key] = current_time
