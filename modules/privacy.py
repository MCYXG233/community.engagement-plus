"""模块10: 隐私保护 — 敏感词脱敏、数据导出、注销清理"""

from __future__ import annotations

import json
import re
import time
from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from maibot_sdk.context import PluginContext

# 本插件所有持久化键的统一前缀，防止误删其他插件数据
_KEY_PREFIX = "community_engagement_"


def _safe_format_value(value: Any) -> Any:
    """安全格式化 person.get_value 返回值，保留原始类型但确保可序列化。"""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return value.get("value", value.get("name", value))
    if hasattr(value, "value"):
        return str(value.value)
    if hasattr(value, "name"):
        return str(value.name)
    return value

# 默认敏感词脱敏模式
DEFAULT_SENSITIVE_PATTERNS = [
    (r"1[3-9]\d{9}", "***手机号***"),  # 手机号
    (r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b", "***邮箱***"),  # 邮箱
    (r"\d{17}[\dXx]", "***身份证***"),  # 身份证
]


class PrivacyModule:
    """隐私保护模块：敏感词脱敏、用户数据导出和注销清理。"""

    def __init__(self, ctx: PluginContext, config) -> None:
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

    def encrypt_profile(self, data: dict) -> dict:
        """对用户画像数据进行简单加密（Base64 编码）。

        注意：这是轻量级混淆，非安全加密。如需真正加密请使用专业库。
        """
        if not self._config.encrypt_profiles:
            return data

        import base64
        encrypted = {}
        for key, value in data.items():
            if isinstance(value, str):
                encrypted[key] = base64.b64encode(value.encode("utf-8")).decode("ascii")
            else:
                encrypted[key] = value
        return encrypted

    def decrypt_profile(self, data: dict) -> dict:
        """解密用户画像数据。"""
        if not self._config.encrypt_profiles:
            return data

        import base64
        decrypted = {}
        for key, value in data.items():
            if isinstance(value, str):
                try:
                    decrypted[key] = base64.b64decode(value.encode("ascii")).decode("utf-8")
                except Exception:
                    decrypted[key] = value
            else:
                decrypted[key] = value
        return decrypted

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
                    formatted = _safe_format_value(value)
                    if formatted:
                        data["data"][field] = formatted
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
        """注销并清理本插件中该用户的相关数据。

        清理范围：
        1. PluginData 表中本插件前缀且含 user_id 的记录（打卡等）
        2. entertainment.json 中该用户的投票和接龙数据
        """
        deleted_count = 0

        # 1. 清理 PluginData 表中的打卡记录
        try:
            # 查询所有记录，然后在代码层过滤（SDK 不支持 __contains）
            all_records = await self._ctx.db.query(
                "PluginData",
                query_type="get",
                data={},
                filters={},
                limit=1000,
            )

            records_to_delete = []
            if isinstance(all_records, list):
                for record in all_records:
                    key = record.get("key", "") if isinstance(record, dict) else ""
                    if key and _KEY_PREFIX in key and user_id in key:
                        records_to_delete.append(key)
            elif isinstance(all_records, dict) and all_records:
                key = all_records.get("key", "")
                if key and _KEY_PREFIX in key and user_id in key:
                    records_to_delete.append(key)

            for key in records_to_delete:
                try:
                    await self._ctx.db.delete(
                        "PluginData",
                        filters={"key": key},
                    )
                    deleted_count += 1
                except Exception:
                    pass
        except Exception as e:
            self._ctx.logger.warning(f"清理 PluginData 失败: {e}")

        # 2. 清理 entertainment.json 中的用户数据
        try:
            data_dir = self._ctx.paths.data_dir
            ent_file = data_dir / "entertainment.json"
            if ent_file.exists():
                data = json.loads(ent_file.read_text(encoding="utf-8"))
                modified = False

                # 清理投票中的用户投票记录
                for sid, vote_data in data.get("votes", {}).items():
                    votes = vote_data.get("votes", {})
                    if user_id in votes:
                        del votes[user_id]
                        modified = True

                # 清理接龙中的用户参与记录
                for sid, chain_data in data.get("chains", {}).items():
                    entries = chain_data.get("entries", [])
                    new_entries = [e for e in entries if e.get("user_id") != user_id]
                    if len(new_entries) != len(entries):
                        chain_data["entries"] = new_entries
                        modified = True

                if modified:
                    ent_file.write_text(
                        json.dumps(data, ensure_ascii=False, indent=2),
                        encoding="utf-8",
                    )
                    deleted_count += 1
        except Exception as e:
            self._ctx.logger.warning(f"清理 entertainment.json 失败: {e}")

        return f"已清理 {deleted_count} 条用户数据"

    async def cleanup(self) -> None:
        """清理资源。"""
        pass
