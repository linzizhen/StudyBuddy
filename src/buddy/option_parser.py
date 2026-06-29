"""从搭子回复中解析 A-Z 选项，并检测游戏化结束"""
import re
from typing import List, Tuple

_OPTION_LETTER = r'[A-Z]'
_OPTION_LINE = re.compile(
    rf'^[ \t]*({_OPTION_LETTER})[\.、:\)）]\s*(.+)$',
    re.MULTILINE | re.IGNORECASE,
)

_GAME_OVER_MARKERS = (
    r'\[GAME_OVER\]',
    r'\[END\]',
    r'本局结束',
    r'游戏化结束',
)

_GAME_OVER_PHRASES = (
    r'恭喜通关',
    r'冒险结束',
    r'游戏结束',
    r'探索完成',
    r'本轮结束',
    r'你已经学习了',
    r'你想要怎么做',
    r'真了不起',
    r'做得真棒',
    r'学得不错',
    r'表现.*不错',
)


def parse_chat_options(reply: str) -> Tuple[List[str], List[str]]:
    """解析回复中的 A-Z 选项，至少 2 个才返回"""
    if not reply:
        return [], []

    options: List[str] = []
    option_texts: List[str] = []

    for match in _OPTION_LINE.finditer(reply):
        letter = match.group(1).upper()
        if letter in options:
            continue
        text = match.group(2).strip()
        text = re.split(rf'\s+{_OPTION_LETTER}[\.、:\)）]\s*', text)[0].strip()
        options.append(letter)
        option_texts.append(text)

    if len(options) >= 2:
        return options, option_texts
    return [], []


def is_game_option_message(message: str, game_mode: str = 'auto') -> bool:
    """用户点击 A-Z 选项（单字母消息）且处于可游戏化模式"""
    mode = (game_mode or 'auto').lower()
    if mode == 'direct':
        return False
    return bool(re.match(r'^[A-Z]$', (message or '').strip(), re.IGNORECASE))


def detect_game_over(reply: str, options: List[str], in_active_game: bool = False) -> bool:
    """检测游戏化讲解是否结束（无选项时结合标记/结束语判断）"""
    if not reply:
        return False
    for pattern in _GAME_OVER_MARKERS:
        if re.search(pattern, reply, re.IGNORECASE):
            return True
    if options:
        return False
    if in_active_game:
        return True
    for pattern in _GAME_OVER_PHRASES:
        if re.search(pattern, reply):
            return True
    return False


def strip_game_markers(reply: str) -> str:
    """移除游戏结束标记，供前端展示"""
    if not reply:
        return reply
    cleaned = re.sub(r'\[GAME_OVER\]', '', reply, flags=re.IGNORECASE)
    cleaned = re.sub(r'\[END\]', '', cleaned, flags=re.IGNORECASE)
    return cleaned.strip()
