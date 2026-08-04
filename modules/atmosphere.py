"""模块4: 氛围监测 — 群温度计、活跃榜、新人欢迎、潜水党召回"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from maibot_sdk.context import PluginContext

    from ..config import AtmosphereConfig


class AtmosphereModule:
    """氛围监测模块：监测群聊活跃度、欢迎新人、召回潜水用户。"""

    def __init__(self, ctx: PluginContext, config: AtmosphereConfig) -> None:
        self._ctx = ctx
        self._config = config
        # stream_id -> {user_id: last_active_timestamp}
        self._user_activity: Dict[str, Dict[str, float]] = {}
        # stream_id -> {user_id: first_seen_timestamp}
        self._known_users: Dict[str, Dict[str, float]] = {}

    async def get_temperature(self, stream_id: str) -> str:
        """获取群温度（活跃度评分 0-100）。"""
        recent = await self._ctx.message.get_recent(stream_id, limit=100)
        if not recent:
            return "群温度：0°C（当前无消息记录）"

        now = time.time()
        # 统计最近1小时内的消息
        hour_ago = now - 3600
        recent_hour = [m for m in recent if self._get_timestamp(m) > hour_ago]
        msg_count = len(recent_hour)

        # 统计活跃用户数
        active_users: set = set()
        for msg in recent_hour:
            uid = self._extract_user_id(msg)
            if uid:
                active_users.add(uid)

        user_count = len(active_users)

        # 计算温度值
        msg_score = min(msg_count * 2, 50)  # 消息数贡献最多50分
        user_score = min(user_count * 10, 50)  # 用户数贡献最多50分
        temperature = msg_score + user_score

        # 温度描述
        if temperature >= 80:
            desc = "🔥 非常活跃"
        elif temperature >= 60:
            desc = "😊 比较活跃"
        elif temperature >= 40:
            desc = "😐 一般"
        elif temperature >= 20:
            desc = "😴 有些冷清"
        else:
            desc = "🥶 非常冷清"

        return (
            f"群温度：{temperature}°C {desc}\n"
            f"最近1小时：{msg_count} 条消息，{user_count} 人参与"
        )

    async def get_active_rank(self, stream_id: str, days: int = 7) -> str:
        """获取活跃排行榜。"""
        since = time.time() - days * 86400
        recent = await self._ctx.message.get_recent(stream_id, limit=500)
        if not recent:
            return "暂无活跃数据"

        # 统计每个用户的发言数
        user_counts: Dict[str, int] = {}
        for msg in recent:
            ts = self._get_timestamp(msg)
            if ts < since:
                continue
            uid = self._extract_user_id(msg)
            if uid:
                user_counts[uid] = user_counts.get(uid, 0) + 1

        if not user_counts:
            return f"最近 {days} 天暂无活跃数据"

        # 排序取前10
        sorted_users = sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        lines = [f"最近 {days} 天活跃排行："]
        medals = ["🥇", "🥈", "🥉"]
        for i, (uid, count) in enumerate(sorted_users):
            prefix = medals[i] if i < 3 else f"  {i + 1}."
            # 尝试获取用户名
            name = uid
            try:
                person_id = await self._ctx.person.get_id("unknown", uid)
                if person_id:
                    nickname = await self._ctx.person.get_value(person_id, "name")
                    if nickname:
                        name = nickname
            except Exception:
                pass
            lines.append(f"{prefix} {name} — {count} 条消息")

        return "\n".join(lines)

    async def check_new_user(self, message: dict) -> str | None:
        """检查是否为新用户首次发言，返回欢迎消息或 None。"""
        if not self._config.enabled or not self._config.welcome_enabled:
            return None

        user_id = self._extract_user_id(message)
        stream_id = message.get("session_id", "")
        if not user_id or not stream_id:
            return None

        now = time.time()

        # 检查是否已知用户
        known = self._known_users.get(stream_id, {})
        if user_id in known:
            return None

        # 记录新用户
        if stream_id not in self._known_users:
            self._known_users[stream_id] = {}
        self._known_users[stream_id][user_id] = now

        # 获取用户名
        name = "新朋友"
        try:
            person_id = await self._ctx.person.get_id("unknown", user_id)
            if person_id:
                nickname = await self._ctx.person.get_value(person_id, "name")
                if nickname:
                    name = nickname
        except Exception:
            pass

        return f"欢迎 {name} 加入群聊！发送 /社区帮助 查看可用命令"

    async def get_lurkers(self, stream_id: str, days: int = 7) -> str:
        """获取长期未发言用户列表。"""
        since = time.time() - days * 86400
        recent = await self._ctx.message.get_recent(stream_id, limit=500)

        # 找出最近活跃的用户
        active_users: set = set()
        for msg in recent:
            ts = self._get_timestamp(msg)
            if ts > since:
                uid = self._extract_user_id(msg)
                if uid:
                    active_users.add(uid)

        # 从已知用户中找出不活跃的
        known = self._known_users.get(stream_id, {})
        lurkers = [
            uid for uid, first_seen in known.items()
            if uid not in active_users and first_seen < since
        ]

        if not lurkers:
            return f"最近 {days} 天内没有发现潜水用户"

        lines = [f"潜水用户（{len(lurkers)} 人超过 {days} 天未发言）："]
        for uid in lurkers[:20]:
            name = uid
            try:
                person_id = await self._ctx.person.get_id("unknown", uid)
                if person_id:
                    nickname = await self._ctx.person.get_value(person_id, "name")
                    if nickname:
                        name = nickname
            except Exception:
                pass
            lines.append(f"  - {name}")

        return "\n".join(lines)

    async def check_anniversaries(self, stream_id: str) -> list[str]:
        """检查今天是否有用户周年纪念日，返回祝福列表。

        通过比对用户首次发言日期和今天是否为同月同日来判断。
        """
        today = time.strftime("%m-%d")
        results: list[str] = []

        known = self._known_users.get(stream_id, {})
        for uid, first_seen in known.items():
            import datetime
            first_date = datetime.datetime.fromtimestamp(first_seen)
            if first_date.strftime("%m-%d") == today:
                years = datetime.date.today().year - first_date.year
                if years > 0:
                    name = uid
                    try:
                        person_id = await self._ctx.person.get_id("unknown", uid)
                        if person_id:
                            nickname = await self._ctx.person.get_value(person_id, "name")
                            if nickname:
                                name = nickname
                    except Exception:
                        pass
                    results.append(f"{name} 加入群聊 {years} 周年！🎉")

        return results

    def _get_timestamp(self, message: dict) -> float:
        """从消息中提取时间戳。"""
        ts = message.get("timestamp", "0")
        try:
            return float(ts)
        except (ValueError, TypeError):
            return 0.0

    def _extract_user_id(self, message: dict) -> str:
        """从消息中提取用户 ID。"""
        msg_info = message.get("message_info", {})
        user_info = msg_info.get("user_info", {})
        return user_info.get("user_id", "")

    async def cleanup(self) -> None:
        """清理资源。"""
        self._user_activity.clear()
        self._known_users.clear()
