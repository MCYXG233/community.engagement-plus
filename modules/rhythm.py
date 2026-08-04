"""模块1: 发言管理 — 节流、刷屏拦截、复读检测、冷场提醒"""

from __future__ import annotations

import time
from collections import deque
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from maibot_sdk.context import PluginContext

from ._utils import extract_user_id


class RhythmModule:
    """发言管理模块：节流、刷屏拦截、复读检测、冷场提醒。"""

    def __init__(self, ctx: PluginContext, config) -> None:
        self._ctx = ctx
        self._config = config
        # user_id -> 消息时间戳队列
        self._user_messages: Dict[str, deque] = {}
        # stream_id -> 最近消息文本队列 (text, user_id, timestamp)
        self._recent_texts: Dict[str, deque] = {}
        # user_id -> 上次刷屏警告时间
        self._flood_warnings: Dict[str, float] = {}
        # stream_id -> 最后一条消息的时间戳（用于冷场检测）
        self._last_message_time: Dict[str, float] = {}
        # stream_id -> 上次冷场提醒时间（避免重复提醒）
        self._last_silence_alert: Dict[str, float] = {}

    async def check_message(self, message: dict) -> dict | None:
        """检查消息是否应被拦截。返回 None 表示放行，返回修改后的 message 表示拦截。

        依次执行：风控前置检查 → 节流 → 刷屏 → 复读检测。
        """
        if not self._config.enabled:
            return message

        user_id = self._extract_user_id(message)
        stream_id = message.get("stream_id", message.get("session_id", ""))
        text = self._extract_text(message)
        now = time.time()

        # 记录所有消息（用于复读检测和冷场检测，无论是否为 @ 或命令）
        if user_id:
            self._record_message(user_id, stream_id, text, now)
        if stream_id:
            self._last_message_time[stream_id] = now

        # 发言节流
        if user_id and self._is_throttled(user_id, now):
            self._ctx.logger.debug(f"[节奏控制] 用户 {user_id} 被节流，丢弃消息")
            return None

        # 刷屏拦截
        if user_id and self._is_flooding(user_id, stream_id, now):
            await self._send_warning(stream_id, f"检测到刷屏行为，请稍后再发言")
            return None

        # 多 Bot 协调：非 @ 且非命令的消息跳过复读检测（避免干扰正常聊天）
        is_at = message.get("is_at", False)
        is_command = message.get("is_command", False)
        is_mentioned = message.get("is_mentioned", False)
        if not is_at and not is_mentioned and not is_command and not text.startswith("/"):
            return message

        # 复读检测（不拦截，仅提醒）
        if text and stream_id:
            repeat_info = self._check_repeat(stream_id, text, user_id)
            if repeat_info:
                await self._send_warning(stream_id, repeat_info)

        return message

    def _extract_user_id(self, message: dict) -> str:
        """从消息中提取用户 ID。"""
        return extract_user_id(message)

    def _extract_text(self, message: dict) -> str:
        """从消息中提取纯文本。"""
        return message.get("processed_plain_text", "") or ""

    def _is_throttled(self, user_id: str, now: float) -> bool:
        """检查用户是否被节流。"""
        timestamps = self._user_messages.get(user_id, deque())
        if not timestamps:
            return False
        last_time = timestamps[-1]
        return (now - last_time) < self._config.throttle_seconds

    def _is_flooding(self, user_id: str, stream_id: str, now: float) -> bool:
        """检查用户是否在刷屏（10秒内超过阈值）。"""
        timestamps = self._user_messages.get(user_id, deque())
        # 清理超过10秒的记录
        cutoff = now - 10
        recent = [t for t in timestamps if t > cutoff]
        self._user_messages[user_id] = deque(recent)

        if len(recent) >= self._config.flood_threshold:
            # 避免重复警告
            last_warn = self._flood_warnings.get(user_id, 0)
            if (now - last_warn) > 10:
                self._flood_warnings[user_id] = now
                return True
        return False

    def _check_repeat(self, stream_id: str, text: str, user_id: str) -> str | None:
        """检测复读行为。返回提醒文本或 None。

        统计相同文本的不同发送者数量，达到阈值时提醒。
        """
        if not text or len(text) < 2:
            return None

        recent = self._recent_texts.get(stream_id, deque())
        # 统计相同文本的发送者和总次数
        same_text_users: set = set()
        same_text_count = 0
        for t, uid, _ in recent:
            if t == text:
                same_text_count += 1
                if uid != user_id:
                    same_text_users.add(uid)

        user_count = len(same_text_users) + 1  # 包括当前用户
        if user_count >= self._config.repeat_threshold:
            if same_text_count > user_count:
                return f"复读合并：{user_count} 人共发送 {same_text_count} 条相同消息"
            return f"检测到复读行为（{user_count} 人发送了相同内容）"
        return None

    def _record_message(self, user_id: str, stream_id: str, text: str, now: float) -> None:
        """记录消息到内存。"""
        if user_id not in self._user_messages:
            self._user_messages[user_id] = deque()
        self._user_messages[user_id].append(now)
        # 限制队列大小
        if len(self._user_messages[user_id]) > 100:
            self._user_messages[user_id].popleft()

        if stream_id not in self._recent_texts:
            self._recent_texts[stream_id] = deque()
        self._recent_texts[stream_id].append((text, user_id, now))
        if len(self._recent_texts[stream_id]) > 50:
            self._recent_texts[stream_id].popleft()

    async def _send_warning(self, stream_id: str, text: str) -> None:
        """发送提醒消息。"""
        await self._ctx.send.text(text, stream_id)

    async def check_silence(self, stream_id: str) -> str | None:
        """检查群是否冷场，返回提醒文本或 None。

        由 maisaka.proactive.trigger 定时调用。
        """
        if not self._config.enabled or not self._config.silence_reminder:
            return None

        now = time.time()
        last_time = self._last_message_time.get(stream_id, 0)
        if last_time == 0:
            return None

        silence_minutes = (now - last_time) / 60
        threshold = self._config.silence_minutes

        if silence_minutes < threshold:
            return None

        # 避免重复提醒（30分钟内只提醒一次）
        last_alert = self._last_silence_alert.get(stream_id, 0)
        if (now - last_alert) < 1800:
            return None

        self._last_silence_alert[stream_id] = now
        minutes = int(silence_minutes)
        return f"群已经安静了 {minutes} 分钟了，来聊点什么吧~"

    async def cleanup(self) -> None:
        """清理资源。"""
        self._user_messages.clear()
        self._recent_texts.clear()
        self._flood_warnings.clear()
        self._last_message_time.clear()
        self._last_silence_alert.clear()
