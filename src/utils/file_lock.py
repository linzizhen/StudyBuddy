"""
StudyPal 文件操作工具
提供原子化的 JSON 文件读写，防止并发写入冲突

支持跨平台：Linux/macOS 使用 fcntl，Windows 使用 msvcrt

作者：StudyPal
日期：2026-04-30
"""

import json
import os
import sys
from typing import Any, Optional

# 跨平台文件锁支持
_file_lock = None
try:
    # Unix/Linux/macOS
    import fcntl
    _file_lock = 'fcntl'
except ImportError:
    try:
        # Windows
        import msvcrt
        _file_lock = 'msvcrt'
    except ImportError:
        # 无锁版本（回退）
        _file_lock = None


def _lock_file(f, mode):
    """获取文件锁"""
    if _file_lock == 'fcntl':
        if mode == 'shared':
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        else:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
    elif _file_lock == 'msvcrt':
        # Windows 锁定模式
        if mode == 'shared':
            msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)
        else:
            msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)


def _unlock_file(f):
    """释放文件锁"""
    if _file_lock == 'fcntl':
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    elif _file_lock == 'msvcrt':
        try:
            msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
        except (OSError, IOError):
            pass


def ensure_dir(filepath: str) -> None:
    """确保目录存在"""
    dir_path = os.path.dirname(filepath)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)


def atomic_write_json(filepath: str, data: Any) -> None:
    """
    原子化写入 JSON 文件
    使用文件锁确保并发安全

    参数:
        filepath: 文件路径
        data: 要写入的数据
    """
    ensure_dir(filepath)
    temp_path = filepath + '.tmp'
    try:
        with open(temp_path, 'w', encoding='utf-8') as f:
            if _file_lock:
                try:
                    _lock_file(f, 'exclusive')
                except (OSError, IOError):
                    pass
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
            if _file_lock:
                try:
                    _unlock_file(f)
                except (OSError, IOError):
                    pass
        # 原子替换
        if os.path.exists(filepath):
            os.remove(filepath)
        os.rename(temp_path, filepath)
    except Exception:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
        raise


def atomic_read_json(filepath: str, default: Optional[Any] = None) -> Any:
    """
    读取 JSON 文件（带文件锁）

    参数:
        filepath: 文件路径
        default: 文件不存在时返回的默认值

    返回:
        解析后的数据或默认值
    """
    if not os.path.exists(filepath):
        return default if default is not None else {}

    try:
        with open(filepath, 'r', encoding='utf-8', newline='') as f:
            if _file_lock:
                try:
                    _lock_file(f, 'shared')
                except (OSError, IOError):
                    pass
            data = json.load(f)
            if _file_lock:
                try:
                    _unlock_file(f)
                except (OSError, IOError):
                    pass
            return data
    except (json.JSONDecodeError, IOError):
        return default if default is not None else {}


def safe_write_json(filepath: str, data: Any) -> None:
    """
    安全写入 JSON 文件（无锁版本，用于单进程场景）

    参数:
        filepath: 文件路径
        data: 要写入的数据
    """
    ensure_dir(filepath)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
