"""
StudyPal 路由公共工具
提供路由层共用的辅助函数

作者：StudyPal
日期：2026-04-30
"""

from functools import lru_cache

from flask import jsonify


@lru_cache(maxsize=1)
def get_buddy():
    """
    获取 Buddy 单例实例

    使用 LRU 缓存确保同一请求周期内只创建一个实例
    """
    from src.core.buddy import get_buddy
    return get_buddy()


def success_response(data=None, message="", **kwargs):
    """
    生成统一格式的成功响应

    参数:
        data: 响应数据
        message: 成功消息
        **kwargs: 其他附加字段

    返回:
        Flask JSON 响应元组
    """
    response = {"success": True}
    if data is not None:
        response["data"] = data
    if message:
        response["message"] = message
    response.update(kwargs)
    return jsonify(response), 200


def error_response(message, status_code=400, **kwargs):
    """
    生成统一格式的错误响应

    参数:
        message: 错误消息
        status_code: HTTP 状态码
        **kwargs: 其他附加字段

    返回:
        Flask JSON 响应元组
    """
    response = {"success": False, "error": message}
    response.update(kwargs)
    return jsonify(response), status_code


def get_buddy_singleton():
    """获取 Buddy 单例的别名（兼容旧代码）"""
    return get_buddy()
