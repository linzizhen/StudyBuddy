"""
StudyBuddy 核心模块
包含情绪管理、计时器、监督器等核心功能
"""

from .buddy import Buddy
from .timer import StudyTimer, StudySupervisor

__all__ = ['Buddy', 'StudyTimer', 'StudySupervisor']
