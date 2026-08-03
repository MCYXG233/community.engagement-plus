"""模块7: 输入解析 — @ 检测、回复上下文、引用追溯"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from maibot_sdk.context import PluginContext

    from ..config import InputParseConfig


class InputParseModule:
    """输入解析模块：解析消息中的 @、回复上下文等结构化信息。"""

    def __init__(self, ctx: PluginContext, config: InputParseConfig) -> None:
        self._ctx = ctx
        self._config = config

    async def parse(self, message: dict) -> Dict[str, Any]:
        """解析消息输入，返回结构化信息。"""
        result: Dict[str, Any] = {
            "mentions": [],
            "reply_context": None,
            "is_reply": False,
        }

        if not self._config.enabled:
            return result

        # 解析 @ 检测
        result["mentions"] = self._parse_mentions(message)
        result["is_mentioned"] = message.get("is_mentioned", False)
        result["is_at"] = message.get("is_at", False)

        # 解析回复上下文
        reply_to = message.get("reply_to")
        if reply_to:
            result["is_reply"] = True
            result["reply_context"] = await self._get_reply_context(reply_to)

        return result

    def _parse_mentions(self, message: dict) -> List[Dict[str, str]]:
        """从 raw_message 中解析 @ 组件。"""
        mentions: List[Dict[str, str]] = []
        raw_message = message.get("raw_message", [])

        for segment in raw_message:
            if segment.get("type") == "at":
                data = segment.get("data", {})
                mentions.append({
                    "user_id": data.get("target_user_id", ""),
                    "nickname": data.get("target_user_nickname", ""),
                    "cardname": data.get("target_user_cardname", ""),
                })

        return mentions

    async def _get_reply_context(self, reply_to: str) -> Optional[Dict[str, Any]]:
        """获取被回复消息的上下文。"""
        try:
            msg = await self._ctx.message.get_by_id(reply_to)
            if not msg:
                return None

            user_info = msg.get("message_info", {}).get("user_info", {})
            return {
                "message_id": reply_to,
                "user_id": user_info.get("user_id", ""),
                "nickname": user_info.get("user_nickname", ""),
                "text": msg.get("processed_plain_text", ""),
            }
        except Exception as e:
            self._ctx.logger.warning(f"获取回复上下文失败: {e}")
            return None

    async def cleanup(self) -> None:
        """清理资源。"""
        pass
