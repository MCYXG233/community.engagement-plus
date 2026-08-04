"""模块8: 输出美化 — 分段发送、长文折叠、表情插入"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from maibot_sdk.context import PluginContext

    from ..config import OutputFormatConfig


class OutputFormatModule:
    """输出美化模块：优化消息输出格式。"""

    def __init__(self, ctx: PluginContext, config: OutputFormatConfig) -> None:
        self._ctx = ctx
        self._config = config

    async def format_output(self, text: str, stream_id: str) -> str:
        """格式化输出消息（仅本地操作，不调用外部 API）。"""
        if not self._config.enabled or not text:
            return text

        # 长文折叠
        if len(text) > self._config.max_length:
            text = self._fold_text(text)

        # 表情插入
        text = await self._insert_emoji(text)

        return text

    async def translate(self, text: str) -> str | None:
        """按需翻译：调用外部翻译 API。返回翻译结果或 None。"""
        translation = await self._translate(text)
        if translation and translation != text:
            return f"{text}\n\n🌐 {translation}"
        return None

    def _fold_text(self, text: str) -> str:
        """长文折叠：超过阈值时添加折叠标记。"""
        max_len = self._config.max_length
        if len(text) <= max_len:
            return text

        # 在自然断点处截断
        truncated = text[:max_len]
        last_newline = truncated.rfind("\n")
        last_period = truncated.rfind("。")
        last_comma = truncated.rfind("，")

        # 选择最靠后的断点
        cut_point = max(last_newline, last_period, last_comma)
        if cut_point > max_len // 2:
            truncated = text[:cut_point + 1]

        return truncated + "\n... (内容过长，已折叠)"

    async def _insert_emoji(self, text: str) -> str:
        """根据消息内容在句尾插入合适的表情。"""
        if not text or len(text) < 5:
            return text

        # 根据语气关键词选择表情
        emoji_keywords = {
            "开心": "😊", "高兴": "😄", "快乐": "🎉",
            "谢谢": "🙏", "感谢": "❤️", "好的": "👍",
            "加油": "💪", "努力": "🔥", "厉害": "🌟",
            "难过": "😢", "伤心": "💔", "抱歉": "🙇",
            "疑问": "❓", "为什么": "🤔", "真的吗": "😲",
        }

        for keyword, emoji in emoji_keywords.items():
            if keyword in text:
                # 避免重复插入
                if emoji not in text:
                    return text + " " + emoji
                break

        return text

    async def split_long_message(self, text: str, stream_id: str) -> list[str]:
        """将长消息拆分为多条。"""
        if len(text) <= self._config.max_length:
            return [text]

        parts: list[str] = []
        remaining = text

        while remaining:
            if len(remaining) <= self._config.max_length:
                parts.append(remaining)
                break

            # 在自然断点处拆分
            cut_point = self._config.max_length
            last_newline = remaining.rfind("\n", 0, cut_point)
            last_period = remaining.rfind("。", 0, cut_point)
            last_comma = remaining.rfind("，", 0, cut_point)

            best = max(last_newline, last_period, last_comma)
            if best > cut_point // 2:
                cut_point = best + 1

            parts.append(remaining[:cut_point].rstrip())
            remaining = remaining[cut_point:].lstrip()

        return parts

    async def _translate(self, text: str) -> str | None:
        """调用外部翻译 API。返回翻译结果或 None。"""
        api_url = self._config.translate_api_url
        if not api_url:
            return None

        try:
            import aiohttp
            headers = {"Content-Type": "application/json"}
            if self._config.translate_api_key:
                headers["Authorization"] = f"Bearer {self._config.translate_api_key}"

            payload = {
                "text": text,
                "target_lang": self._config.translate_target_lang,
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=payload, headers=headers, timeout=10) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return result.get("translation", result.get("text", ""))
        except Exception as e:
            self._ctx.logger.warning(f"翻译 API 调用失败: {e}")

        return None

    async def cleanup(self) -> None:
        """清理资源。"""
        pass
