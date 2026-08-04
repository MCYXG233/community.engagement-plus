"""共享工具函数，避免多模块重复定义。"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from maibot_sdk.context import PluginContext


async def safe_get_person_name(ctx: PluginContext, user_id: str, fallback: str = "") -> str:
    """安全获取用户名称，兼容不同 SDK 返回格式。"""
    try:
        person_id = await ctx.person.get_id("unknown", user_id)
        if not person_id:
            return fallback
        result = await ctx.person.get_value(person_id, "name")
        if isinstance(result, str):
            return result
        if isinstance(result, dict):
            return result.get("value", result.get("name", fallback))
        if hasattr(result, "name"):
            return str(result.name)
        if hasattr(result, "value"):
            return str(result.value)
        return str(result) if result else fallback
    except Exception:
        return fallback


def safe_format_value(value: Any) -> str:
    """安全格式化 person.get_value 返回值。"""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return value.get("value", value.get("name", str(value)))
    if hasattr(value, "value"):
        return str(value.value)
    if hasattr(value, "name"):
        return str(value.name)
    return str(value)


def extract_user_id(message: dict) -> str:
    """从消息中提取用户 ID。"""
    msg_info = message.get("message_info", {})
    user_info = msg_info.get("user_info", {})
    return user_info.get("user_id", "")


def extract_stream_id(message: dict) -> str:
    """从消息中提取 stream_id，兼容 session_id 键名。"""
    return message.get("stream_id", message.get("session_id", ""))
