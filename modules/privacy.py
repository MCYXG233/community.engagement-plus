"""模块10: 隐私保护 — 敏感词脱敏、数据导出、注销清理"""

from __future__ import annotations

import json
import re
import time
from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from maibot_sdk.context import PluginContext

    from ..config import PrivacyConfig

# 本插件所有持久化键的统一前缀，防止误删其他插件数据
_KEY_PREFIX = "ce_"

# 默认敏感词脱敏模式
DEFAULT_SENSITIVE_PATTERNS = [
    (r"1[3-9]\d{9}", "***手机号***"),  # 手机号
    (r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b", "***邮箱***"),  # 邮箱
    (r"\d{17}[\dXx]", "***身份证***"),  # 身份证
]


class PrivacyModule:
    """隐私保护模块：敏感词脱敏、用户数据导出和注销清理。"""

    def __init__(self, ctx: PluginContext, config: PrivacyConfig) -> None:
        self._ctx = ctx
        self._config = config
        # 编译脱敏正则
        self._sensitive_patterns: List[tuple] = []
        patterns = config.sensitive_patterns or []
        if not patterns:
            # 使用默认模式
            for pattern, replacement in DEFAULT_SENSITIVE_PATTERNS:
                try:
                    self._sensitive_patterns.append(
                        (re.compile(pattern), replacement)
                    )
                except re.error:
                    self._ctx.logger.warning(f"无效的脱敏正则: {pattern}")
        else:
            for pattern_str in patterns:
                try:
                    self._sensitive_patterns.append(
                        (re.compile(pattern_str), "***")
                    )
                except re.error:
                    self._ctx.logger.warning(f"无效的脱敏正则: {pattern_str}")

    def sanitize(self, text: str) -> str:
        """对文本进行敏感词脱敏。"""
        if not text:
            return text

        for pattern, replacement in self._sensitive_patterns:
            text = pattern.sub(replacement, text)

        return text

    async def export_data(self, user_id: str) -> str:
        """导出用户数据为 JSON。"""
        data: Dict[str, Any] = {
            "user_id": user_id,
            "export_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "data": {},
        }

        # 尝试获取用户信息
        try:
            person_id = await self._ctx.person.get_id("unknown", user_id)
            if person_id:
                data["person_id"] = person_id
                # 获取用户基本信息
                for field in ["name", "state"]:
                    value = await self._ctx.person.get_value(person_id, field)
                    if value:
                        data["data"][field] = value
        except Exception as e:
            self._ctx.logger.warning(f"导出用户数据失败: {e}")

        # 保存到文件
        data_dir = self._ctx.paths.data_dir
        data_dir.mkdir(parents=True, exist_ok=True)
        export_file = data_dir / f"export_{user_id}_{int(time.time())}.json"

        try:
            export_file.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            return f"数据已导出到: {export_file.name}"
        except Exception as e:
            return f"导出失败: {e}"

    async def delete_user_data(self, user_id: str) -> str:
        """注销并清理本插件中该用户的相关数据。"""
        deleted_count = 0

        try:
            # 只删除本插件前缀的记录，避免误伤其他插件数据
            search_pattern = f"{_KEY_PREFIX}{user_id}"
            results = await self._ctx.db.query(
                "PluginData",
                query_type="count",
                filters={"key__contains": search_pattern},
            )
            if results and results > 0:
                await self._ctx.db.delete(
                    "PluginData",
                    filters={"key__contains": search_pattern},
                )
                deleted_count += results
        except Exception as e:
            self._ctx.logger.warning(f"清理用户数据失败: {e}")

        return f"已清理 {deleted_count} 条用户数据"

    async def cleanup(self) -> None:
        """清理资源。"""
        pass
