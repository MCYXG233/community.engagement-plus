"""模块2: 消息优化 — 链接去重、关键词高亮、长文折叠"""

from __future__ import annotations

import time
from collections import deque
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from maibot_sdk.context import PluginContext


class QualityModule:
    """消息优化模块：链接去重、关键词高亮、长文折叠。"""

    def __init__(self, ctx: PluginContext, config) -> None:
        self._ctx = ctx
        self._config = config
        # stream_id -> 最近消息队列 (type, content, user_id, timestamp)
        self._recent_messages: Dict[str, deque] = {}
        # (stream_id, url) -> 首次出现时间
        self._seen_urls: Dict[tuple, float] = {}

    async def check_outgoing(self, text: str, stream_id: str) -> str | None:
        """检查 outgoing 消息是否需要优化。返回优化后的文本或 None（表示不修改）。"""
        if not self._config.enabled:
            return None

        now = time.time()

        # 链接去重
        if text:
            text = self._deduplicate_urls(text, stream_id, now)

        # 关键词高亮
        if text and self._config.highlight_keywords:
            text = self._highlight_keywords(text)

        return text

    def _highlight_keywords(self, text: str) -> str:
        """对配置中的关键词添加 【】 标记。"""
        for kw in self._config.highlight_keywords:
            if kw in text:
                text = text.replace(kw, f"【{kw}】")
        return text

    def _deduplicate_urls(self, text: str, stream_id: str, now: float) -> str:
        """去重：相同 URL 在窗口期内不重复展示。"""
        import re

        url_pattern = re.compile(r"https?://\S+")
        urls = url_pattern.findall(text)
        if not urls:
            return text

        cutoff = now - self._config.dedup_window
        # 清理过期记录
        self._seen_urls = {
            k: v for k, v in self._seen_urls.items() if v > cutoff
        }

        new_urls = []
        duplicate_urls = []
        for url in urls:
            key = (stream_id, url)
            if key not in self._seen_urls:
                self._seen_urls[key] = now
                new_urls.append(url)
            else:
                duplicate_urls.append(url)

        # 移除重复 URL 但保留其余文本
        if duplicate_urls:
            for url in duplicate_urls:
                text = text.replace(url, "").strip()
            # 清理多余空格
            text = " ".join(text.split())

        return text if text else None

    async def cleanup(self) -> None:
        """清理资源。"""
        self._recent_messages.clear()
        self._seen_urls.clear()
