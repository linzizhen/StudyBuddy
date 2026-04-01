"""
StudyBuddy AI 模块
包含 AI 助手、API 调用等功能
"""

from .ai_helper import (
    StudyBuddyAI,
    get_ai_instance,
    ask_ai,
    ask_ai_sync,
    clear_ai_history,
    SYSTEM_PROMPT,
    MOCK_RESPONSES
)

__all__ = [
    'StudyBuddyAI',
    'get_ai_instance',
    'ask_ai',
    'ask_ai_sync',
    'clear_ai_history',
    'SYSTEM_PROMPT',
    'MOCK_RESPONSES'
]
