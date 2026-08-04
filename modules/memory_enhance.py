"""模块5: 记忆增强 — 跨日上下文、用户画像聚合、共同记忆回顾"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from maibot_sdk.context import PluginContext

    from ..config import MemoryConfig


def _safe_format_value(value: Any) -> str:
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


class MemoryEnhanceModule:
    """记忆增强模块：增强对话记忆、用户画像聚合和共同回忆。"""

    def __init__(self, ctx: PluginContext, config: MemoryConfig) -> None:
        self._ctx = ctx
        self._config = config

    async def get_user_profile(self, stream_id: str, user_id: str) -> str:
        """获取用户画像（只读聚合，不写入原生数据）。"""
        profile_parts: List[str] = []

        # 读取原生画像数据
        try:
            person_id = await self._ctx.person.get_id("unknown", user_id)
            if person_id:
                for field_name in self._config.profile_fields:
                    value = await self._ctx.person.get_value(person_id, field_name)
                    formatted = _safe_format_value(value)
                    if formatted:
                        profile_parts.append(f"  {field_name}: {formatted}")
        except Exception as e:
            self._ctx.logger.warning(f"读取用户画像失败: {e}")

        # 统计活跃信息（只读聚合）
        recent = await self._ctx.message.get_recent(stream_id, limit=200)
        user_messages = [
            m for m in recent
            if self._extract_user_id(m) == user_id
        ]

        if user_messages:
            # 统计发言数
            profile_parts.append(f"  最近发言数: {len(user_messages)} 条")

            # 统计活跃时段
            hours = [self._get_hour(m) for m in user_messages if self._get_hour(m) >= 0]
            if hours:
                from collections import Counter
                hour_counts = Counter(hours)
                peak_hour = hour_counts.most_common(1)[0][0]
                profile_parts.append(f"  活跃时段: {peak_hour}:00 ~ {peak_hour + 1}:00")

        if not profile_parts:
            return f"暂无用户 {user_id} 的画像数据"

        return f"用户画像：\n" + "\n".join(profile_parts)

    async def memory_recall(self, stream_id: str) -> str:
        """共同记忆回顾：拉取历史消息并用 LLM 生成摘要。"""
        recent = await self._ctx.message.get_recent(stream_id, limit=100)
        if not recent:
            return "暂无历史消息可回顾"

        # 构建可读文本
        readable = await self._ctx.message.build_readable(recent)
        if not readable:
            return "暂无可读的历史消息"

        # 截取合理长度
        text = str(readable)
        if len(text) > 2000:
            text = text[:2000] + "..."

        # 使用 LLM 生成摘要
        prompt = (
            "请用简短的中文总结以下群聊记录的主要话题和有趣瞬间，"
            "不超过200字：\n\n" + text
        )
        try:
            result = await self._ctx.llm.generate(prompt)
            summary = result.get("response", "")
            if summary:
                return f"共同记忆回顾：\n{summary.strip()}"
        except Exception as e:
            self._ctx.logger.warning(f"LLM 生成记忆摘要失败: {e}")

        return "记忆回顾生成失败，请稍后再试"

    async def append_context(self, stream_id: str, text: str) -> None:
        """向当前对话上下文追加重要事件。"""
        try:
            await self._ctx.maisaka.context.append(
                stream_id,
                [{"type": "text", "content": text}],
            )
        except Exception as e:
            self._ctx.logger.warning(f"追加上下文失败: {e}")

    async def sync_cross_session(self, user_id: str, source_stream: str, target_stream: str) -> str:
        """跨会话记忆同步：将用户在一个会话中的关键信息同步到另一个会话。

        使用 ctx.db 存储同步标记，通过 ctx.maisaka.context.append 追加上下文。
        """
        if not self._config.cross_session_sync:
            return "跨会话同步未启用"

        try:
            # 从源会话获取最近消息
            recent = await self._ctx.message.get_recent(source_stream, limit=10)
            user_msgs = [
                m for m in recent
                if self._extract_user_id(m) == user_id
            ]

            if not user_msgs:
                return "源会话中没有该用户的消息"

            # 提取关键信息
            texts = [m.get("processed_plain_text", "") for m in user_msgs if m.get("processed_plain_text")]
            if not texts:
                return "没有可同步的文本内容"

            # 使用 LLM 提取关键信息
            combined = "\n".join(texts[:5])
            prompt = f"请用一句话总结以下用户发言的核心要点：\n{combined}"
            result = await self._ctx.llm.generate(prompt)
            summary = result.get("response", "")

            if summary:
                # 追加到目标会话上下文
                sync_text = f"[跨会话同步] 用户 {user_id} 之前说过：{summary}"
                await self._ctx.maisaka.context.append(
                    target_stream,
                    [{"type": "text", "content": sync_text}],
                )
                return f"已同步用户 {user_id} 的上下文到目标会话"

            return "无法提取关键信息"
        except Exception as e:
            self._ctx.logger.warning(f"跨会话同步失败: {e}")
            return f"同步失败: {e}"

    def _extract_user_id(self, message: dict) -> str:
        """从消息中提取用户 ID。"""
        msg_info = message.get("message_info", {})
        user_info = msg_info.get("user_info", {})
        return user_info.get("user_id", "")

    def _get_hour(self, message: dict) -> int:
        """从消息中提取小时数。"""
        import time
        ts = message.get("timestamp", "0")
        try:
            return time.localtime(float(ts)).tm_hour
        except (ValueError, TypeError):
            return -1

    async def cleanup(self) -> None:
        """清理资源。"""
        pass
