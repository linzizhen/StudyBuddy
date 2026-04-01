"""
StudyBuddy 功能模块
包含任务管理、学习日历、数据管理等模块
"""

from .task_manager import TaskManager, Task
from .study_calendar import StudyCalendar
from .data_manager import (
    load_user_settings, save_user_settings,
    get_motto, set_motto,
    get_favorite_quote, set_favorite_quote,
    get_daily_goal, set_daily_goal
)

__all__ = [
    'TaskManager', 'Task',
    'StudyCalendar',
    'load_user_settings', 'save_user_settings',
    'get_motto', 'set_motto',
    'get_favorite_quote', 'set_favorite_quote',
    'get_daily_goal', 'set_daily_goal'
]
