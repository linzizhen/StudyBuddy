"""
StudyPal AI 模块
包含 AI 助手、API 调用等功能
"""

from .ai_helper import (
    StudyPalAI,
    get_ai_instance,
    ask_ai,
    ask_ai_sync,
    clear_ai_history,
    SYSTEM_PROMPT
)

__all__ = [
    'StudyPalAI',
    'get_ai_instance',
    'ask_ai',
    'ask_ai_sync',
    'clear_ai_history',
    'SYSTEM_PROMPT'
]
