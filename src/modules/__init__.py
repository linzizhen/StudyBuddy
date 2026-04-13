"""
StudyPal 功能模块
包含任务管理、学习日历、数据管理、AI记忆、成就系统等模块
"""

from .task_manager import TaskManager, Task
from .study_calendar import StudyCalendar
from .data_manager import (
    load_user_settings, save_user_settings,
    get_motto, set_motto,
    get_favorite_quote, set_favorite_quote,
    get_daily_goal, set_daily_goal
)
from .ai_memory import AIMemory, get_ai_memory
from .achievements import AchievementManager, get_achievement_manager, get_achievements_data, unlock_achievement, check_achievements

__all__ = [
    'TaskManager', 'Task',
    'StudyCalendar',
    'load_user_settings', 'save_user_settings',
    'get_motto', 'set_motto',
    'get_favorite_quote', 'set_favorite_quote',
    'get_daily_goal', 'set_daily_goal',
    'AIMemory', 'get_ai_memory',
    'AchievementManager', 'get_achievement_manager',
    'get_achievements_data', 'unlock_achievement', 'check_achievements',
]
