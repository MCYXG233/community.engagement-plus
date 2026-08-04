"""模块7: 消息解析 — @ 检测、回复上下文、引用追溯、多消息合并"""

from __future__ import annotations

import time
from collections import deque
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from maibot_sdk.context import PluginContext


class InputParseModule:
    """消息解析模块：解析消息中的 @、回复上下文等结构化信息，支持多消息合并。"""

    # 默认合并窗口（秒）
    DEFAULT_MERGE_WINDOW = 5

    def __init__(self, ctx: PluginContext) -> None:
        self._ctx = ctx
        # stream_id -> 最近消息队列 (user_id, text, timestamp)
        self._recent_buffer: Dict[str, deque] = {}

    async def parse(self, message: dict) -> Dict[str, Any]:
        """解析消息输入，返回结构化信息。"""
        result: Dict[str, Any] = {
            "mentions": [],
            "reply_context": None,
            "is_reply": False,
        }

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

    def buffer_message(self, stream_id: str, user_id: str, text: str) -> str | None:
        """缓冲消息，短时间内同一用户的连续消息合并为一条。

        返回合并后的文本，或 None 表示还在缓冲中。
        """
        if not text:
            return None

        now = time.time()
        window = self.DEFAULT_MERGE_WINDOW

        if stream_id not in self._recent_buffer:
            self._recent_buffer[stream_id] = deque()

        buf = self._recent_buffer[stream_id]

        # 检查是否可以合并（同一用户、窗口期内）
        if buf:
            last_uid, last_text, last_ts = buf[-1]
            if last_uid == user_id and (now - last_ts) < window:
                buf.append((user_id, text, now))
                return None  # 继续缓冲

        # 不能合并，输出缓冲区内容
        if buf:
            merged = self._flush_buffer(buf)
            buf.append((user_id, text, now))
            return merged

        buf.append((user_id, text, now))
        return None

    def flush_all(self) -> Dict[str, str]:
        """刷新所有缓冲区，返回各流的合并文本。"""
        results: Dict[str, str] = {}
        for stream_id, buf in self._recent_buffer.items():
            if buf:
                merged = self._flush_buffer(buf)
                if merged:
                    results[stream_id] = merged
        return results

    def _flush_buffer(self, buf: deque) -> str:
        """将缓冲区消息合并为一条。"""
        if not buf:
            return ""

        parts: List[str] = []
        current_user = None
        current_texts: List[str] = []

        for uid, text, _ in buf:
            if uid == current_user:
                current_texts.append(text)
            else:
                if current_user and current_texts:
                    parts.append(self._format_merged(current_user, current_texts))
                current_user = uid
                current_texts = [text]

        if current_user and current_texts:
            parts.append(self._format_merged(current_user, current_texts))

        buf.clear()
        return "\n".join(parts)

    def _format_merged(self, user_id: str, texts: list[str]) -> str:
        """格式化合并后的消息。"""
        if len(texts) == 1:
            return texts[0]
        return f"[{user_id} 连续 {len(texts)} 条] {' / '.join(texts)}"

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
        self._recent_buffer.clear()
