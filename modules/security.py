"""模块6: 风控过滤 — 关键词屏蔽、图片鉴黄、钓鱼链接拦截、诱导分享检测"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, List

if TYPE_CHECKING:
    from maibot_sdk.context import PluginContext

    from ..config import SecurityConfig


class SecurityModule:
    """风控过滤模块：拦截违规内容、图片、钓鱼链接和诱导分享。"""

    # 常见钓鱼链接特征
    DEFAULT_FISHING_PATTERNS = [
        r"bit\.ly/\S+",
        r"tinyurl\.com/\S+",
        r"t\.cn/\S+",
        r"dwz\.cn/\S+",
    ]

    # 诱导分享关键词
    INDUCE_SHARE_KEYWORDS = [
        "转发到", "分享到", "扩散", "转发朋友圈",
        "不转不是", "转发可得", "分享领取",
    ]

    def __init__(self, ctx: PluginContext, config: SecurityConfig) -> None:
        self._ctx = ctx
        self._config = config
        # 编译正则
        self._fishing_patterns: List[re.Pattern] = []
        for pattern in config.fishing_url_patterns or self.DEFAULT_FISHING_PATTERNS:
            try:
                self._fishing_patterns.append(re.compile(pattern, re.IGNORECASE))
            except re.error:
                self._ctx.logger.warning(f"无效的钓鱼链接正则: {pattern}")

    async def check_message(self, message: dict) -> dict | None:
        """检查消息是否应被拦截。返回 None 表示拦截，返回原 message 表示放行。"""
        if not self._config.enabled:
            return message

        text = self._extract_text(message)
        if not text:
            return message

        # 关键词屏蔽
        if self._check_blocked_words(text):
            self._ctx.logger.info(f"[风控] 消息命中屏蔽词，已拦截")
            return None

        # 钓鱼链接检测
        if self._check_fishing_urls(text):
            self._ctx.logger.info(f"[风控] 消息包含可疑链接，已拦截")
            return None

        # 诱导分享检测
        if self._check_induce_share(text):
            self._ctx.logger.info(f"[风控] 消息包含诱导分享内容，已拦截")
            return None

        # 图片鉴黄检测
        images = self._extract_images(message)
        for img_b64 in images:
            if await self.check_image(img_b64):
                self._ctx.logger.info(f"[风控] 消息包含违规图片，已拦截")
                return None

        return message

    def _check_blocked_words(self, text: str) -> bool:
        """检查文本是否包含屏蔽词。"""
        if not self._config.blocked_words:
            return False
        text_lower = text.lower()
        for word in self._config.blocked_words:
            if word.lower() in text_lower:
                return True
        return False

    def _check_fishing_urls(self, text: str) -> bool:
        """检查文本是否包含钓鱼链接。"""
        for pattern in self._fishing_patterns:
            if pattern.search(text):
                return True
        return False

    def _check_induce_share(self, text: str) -> bool:
        """检查文本是否包含诱导分享内容。"""
        text_lower = text.lower()
        for keyword in self.INDUCE_SHARE_KEYWORDS:
            if keyword in text_lower:
                return True
        return False

    def _extract_text(self, message: dict) -> str:
        """从消息中提取纯文本。"""
        return message.get("processed_plain_text", "") or ""

    def _extract_images(self, message: dict) -> list[str]:
        """从消息中提取图片 base64 数据。"""
        images: list[str] = []
        raw_message = message.get("raw_message", [])
        for segment in raw_message:
            if segment.get("type") == "image":
                data = segment.get("data", {})
                b64 = data.get("binary_data_base64", "")
                if b64:
                    images.append(b64)
        return images

    async def check_image(self, image_base64: str) -> bool:
        """调用外部 API 检查图片是否违规。返回 True 表示违规。"""
        api_url = self._config.image_check_api_url
        if not api_url:
            return False

        try:
            import aiohttp
            headers = {"Content-Type": "application/json"}
            if self._config.image_check_api_key:
                headers["Authorization"] = f"Bearer {self._config.image_check_api_key}"

            payload = {"image": image_base64}
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=payload, headers=headers, timeout=10) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        # 通用审核 API 响应格式：{"label": "nsfw"/"safe", "score": 0.95}
                        label = result.get("label", "").lower()
                        return label in ("nsfw", "unsafe", "blocked", "violation")
        except Exception as e:
            self._ctx.logger.warning(f"图片审核 API 调用失败: {e}")

        return False

    async def cleanup(self) -> None:
        """清理资源。"""
        pass
