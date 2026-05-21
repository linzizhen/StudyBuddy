"""
StudyPal 通用验证器
提供输入验证和参数检查的装饰器

作者：StudyPal
日期：2026-04-30
"""

from functools import wraps
from typing import Any, Callable, List, Optional, Tuple

from flask import request, jsonify


def get_request_json(required: bool = True) -> Tuple[Optional[dict], Optional[Any]]:
    """
    获取请求中的 JSON 数据

    返回:
        (data, error_response) - data 为字典，error_response 为错误响应或 None
    """
    if request.method in ('POST', 'PUT', 'PATCH'):
        if not request.is_json:
            if required:
                return None, (jsonify({"success": False, "error": "请求需要 JSON 格式"}), 400)
            return None, None
        return request.get_json(), None
    elif request.method == 'GET':
        data = request.args.to_dict()
        return data, None
    return {}, None


def validate_required(*required_fields: str) -> Callable:
    """
    验证必填字段的装饰器

    用法:
        @validate_required('title', 'content')
        def create_post():
            data = request.get_json()
            # ...
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            data, error = get_request_json()
            if error:
                return error

            missing = [field for field in required_fields if not data.get(field)]
            if missing:
                return jsonify({
                    "success": False,
                    "error": f"缺少必填字段: {', '.join(missing)}"
                }), 400

            return f(*args, **kwargs)
        return wrapper
    return decorator


def validate_range(field: str, min_val: float, max_val: float, source: str = 'json') -> Callable:
    """
    验证数值范围的装饰器

    参数:
        field: 字段名
        min_val: 最小值
        max_val: 最大值
        source: 数据来源 ('json' 或 'args')

    用法:
        @validate_range('emotion_level', 1, 5)
        def save_emotion():
            # ...
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            if source == 'json':
                data, error = get_request_json()
                if error:
                    return error
            else:
                data = request.args.to_dict()
                try:
                    val = float(data.get(field, 'NaN'))
                except (ValueError, TypeError):
                    val = float('nan')

            if field in data:
                try:
                    val = float(data[field])
                    if not (min_val <= val <= max_val):
                        return jsonify({
                            "success": False,
                            "error": f"{field} 的值必须在 {min_val} 到 {max_val} 之间"
                        }), 400
                except (ValueError, TypeError):
                    return jsonify({
                        "success": False,
                        "error": f"{field} 必须是有效数字"
                    }), 400

            return f(*args, **kwargs)
        return wrapper
    return decorator


def validate_string_length(field: str, min_len: int = 0, max_len: int = 10000) -> Callable:
    """
    验证字符串长度的装饰器

    用法:
        @validate_string_length('content', min_len=1, max_len=500)
        def post_comment():
            # ...
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            data, error = get_request_json()
            if error:
                return error

            value = data.get(field, '')
            if not isinstance(value, str):
                return jsonify({
                    "success": False,
                    "error": f"{field} 必须是字符串"
                }), 400

            length = len(value)
            if length < min_len or length > max_len:
                return jsonify({
                    "success": False,
                    "error": f"{field} 的长度必须在 {min_len} 到 {max_len} 之间"
                }), 400

            return f(*args, **kwargs)
        return wrapper
    return decorator


def validate_enum(field: str, allowed_values: List[Any]) -> Callable:
    """
    验证枚举值的装饰器

    用法:
        @validate_enum('status', ['pending', 'completed', 'cancelled'])
        def update_status():
            # ...
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            data, error = get_request_json()
            if error:
                return error

            value = data.get(field)
            if value is not None and value not in allowed_values:
                return jsonify({
                    "success": False,
                    "error": f"{field} 必须是以下值之一: {', '.join(map(str, allowed_values))}"
                }), 400

            return f(*args, **kwargs)
        return wrapper
    return decorator


# 统一的响应格式辅助函数

def success_response(data: Any = None, message: str = "", **kwargs) -> tuple:
    """生成成功响应"""
    response = {"success": True}
    if data is not None:
        response["data"] = data
    if message:
        response["message"] = message
    response.update(kwargs)
    return jsonify(response), 200


def error_response(message: str, status_code: int = 400, **kwargs) -> tuple:
    """生成错误响应"""
    response = {"success": False, "error": message}
    response.update(kwargs)
    return jsonify(response), status_code


def validation_error(errors: List[str]) -> tuple:
    """生成验证错误响应"""
    return jsonify({
        "success": False,
        "error": "验证失败",
        "details": errors
    }), 400
