"""
AI监督系统模块（ai_supervisor）
用于检测用户学习专注度

作者：AI助手
版本：1.0.0
"""

__version__ = "1.0.0"
__author__ = "AI Assistant"

def _load_monitor():
    """延迟加载 Monitor 类"""
    from .monitor import Monitor as M
    return M

class _MonitorGetter:
    """延迟加载器，用于 __getattr__"""
    def __call__(self):
        return _load_monitor()

def __getattr__(name):
    if name == "Monitor":
        return _load_monitor()
    raise AttributeError(f"模块 '{__name__}' 没有属性 '{name}'")

def __dir__():
    return ["Monitor", "__version__", "__author__"]

# 标记为懒加载模块
__all__ = ["Monitor"]
