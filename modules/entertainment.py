"""模块3: 互动娱乐 — 投票、抽奖、打卡、早安晚安、接龙"""

from __future__ import annotations

import json
import random
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from maibot_sdk.context import PluginContext

    from ..config import EntertainmentConfig

from .privacy import _KEY_PREFIX


@dataclass
class VoteSession:
    """投票会话。"""

    creator_id: str
    options: List[str]
    votes: Dict[str, int] = field(default_factory=dict)  # user_id -> option_index
    created_at: float = 0.0
    is_active: bool = True


@dataclass
class ChainSession:
    """接龙会话。"""

    creator_id: str
    content: str
    entries: List[Dict[str, str]] = field(default_factory=list)  # [{user_id, text}]
    created_at: float = 0.0
    is_active: bool = True


class EntertainmentModule:
    """互动娱乐模块：提供投票、抽奖、打卡、早晚问候、接龙、节日彩蛋等功能。"""

    # 节日彩蛋配置
    HOLIDAYS = {
        "01-01": "新年快乐！新的一年，万事如意！🎉",
        "02-14": "情人节快乐！有情人终成眷属！💕",
        "05-01": "劳动节快乐！辛苦了，好好休息！🎉",
        "06-01": "儿童节快乐！保持童心，永远年轻！🎈",
        "10-01": "国庆节快乐！祝福祖国！🇨🇳",
        "12-25": "圣诞节快乐！Merry Christmas! 🎄",
        "12-31": "跨年快乐！告别旧岁，迎接新年！🎆",
    }

    def __init__(self, ctx: PluginContext, config: EntertainmentConfig) -> None:
        self._ctx = ctx
        self._config = config
        # stream_id -> 当前投票
        self._votes: Dict[str, VoteSession] = {}
        # stream_id -> 当前接龙
        self._chains: Dict[str, ChainSession] = {}
        self._data_dir = ctx.paths.data_dir
        # streak 缓存: (stream_id, user_id, date) -> streak_days
        self._streak_cache: Dict[tuple, int] = {}
        self._streak_cache_date: str = ""

    # ─── 投票 ────────────────────────────────────────────────

    async def create_vote(self, stream_id: str, user_id: str, options: List[str]) -> str:
        """创建投票。"""
        if not options or len(options) < 2:
            return "请提供至少 2 个选项"
        if len(options) > 10:
            return "最多支持 10 个选项"

        session = VoteSession(
            creator_id=user_id,
            options=options,
            created_at=time.time(),
        )
        self._votes[stream_id] = session

        options_text = "\n".join(f"  {i + 1}. {opt}" for i, opt in enumerate(options))
        return f"投票已创建！\n{options_text}\n发送 /投票1 ~ /投票{len(options)} 进行投票"

    async def cast_vote(self, stream_id: str, user_id: str, option_index: int) -> str:
        """投票。"""
        vote = self._votes.get(stream_id)
        if not vote or not vote.is_active:
            return "当前没有进行中的投票"
        if option_index < 0 or option_index >= len(vote.options):
            return f"无效选项，请输入 1 ~ {len(vote.options)}"

        vote.votes[user_id] = option_index
        return f"已投票给「{vote.options[option_index]}」"

    async def get_vote_result(self, stream_id: str) -> str:
        """获取投票结果。"""
        vote = self._votes.get(stream_id)
        if not vote:
            return "当前没有进行中的投票"

        result_lines = ["投票结果："]
        for i, opt in enumerate(vote.options):
            count = sum(1 for v in vote.votes.values() if v == i)
            bar = "█" * count
            result_lines.append(f"  {i + 1}. {opt} — {count} 票 {bar}")

        total = len(vote.votes)
        result_lines.append(f"\n共 {total} 人参与投票")
        return "\n".join(result_lines)

    async def end_vote(self, stream_id: str) -> str:
        """结束投票。"""
        vote = self._votes.get(stream_id)
        if not vote:
            return "当前没有进行中的投票"
        vote.is_active = False
        return await self.get_vote_result(stream_id)

    # ─── 抽奖 ────────────────────────────────────────────────

    async def lottery(self, stream_id: str, count: int = 1) -> str:
        """抽奖：从最近发言用户中随机抽取。"""
        count = max(1, min(count, 20))
        # 获取最近发言的用户
        recent_messages = await self._ctx.message.get_recent(stream_id, limit=50)
        if not recent_messages:
            return "暂无足够用户参与抽奖"

        user_ids = set()
        for msg in recent_messages:
            msg_info = msg.get("message_info", {})
            user_info = msg_info.get("user_info", {})
            uid = user_info.get("user_id", "")
            if uid:
                user_ids.add(uid)

        users = list(user_ids)
        if not users:
            return "暂无足够用户参与抽奖"

        picked = random.sample(users, min(count, len(users)))
        results = []
        for uid in picked:
            person_id = await self._ctx.person.get_id("unknown", uid)
            name = uid
            if person_id:
                nickname = await self._ctx.person.get_value(person_id, "name")
                if nickname:
                    name = nickname
            results.append(name)

        return f"抽奖结果（共 {len(results)} 人）：\n" + "\n".join(f"  - {r}" for r in results)

    # ─── 打卡 ────────────────────────────────────────────────

    async def check_in(self, stream_id: str, user_id: str) -> str:
        """每日签到打卡。"""
        today = time.strftime("%Y-%m-%d")
        check_in_key = f"{_KEY_PREFIX}checkin_{stream_id}_{user_id}_{today}"

        # 检查是否已打卡
        existing = await self._ctx.db.query(
            "PluginData",
            query_type="get",
            filters={"key": check_in_key},
        )
        if existing:
            return "今天已经打卡过了！"

        # 保存打卡记录
        await self._ctx.db.save("PluginData", data={
            "key": check_in_key,
            "value": json.dumps({"user_id": user_id, "date": today}),
        })

        # 查询连续打卡天数
        streak = await self._calc_streak(stream_id, user_id)
        return f"打卡成功！连续打卡 {streak} 天"

    async def _calc_streak(self, stream_id: str, user_id: str) -> int:
        """计算连续打卡天数（带日级缓存，避免重复查询 DB）。"""
        import datetime
        today_str = datetime.date.today().strftime("%Y-%m-%d")

        # 缓存按天失效
        if self._streak_cache_date != today_str:
            self._streak_cache.clear()
            self._streak_cache_date = today_str

        cache_key = (stream_id, user_id, today_str)
        if cache_key in self._streak_cache:
            return self._streak_cache[cache_key]

        streak = 0
        today = datetime.date.today()

        for i in range(365):
            day = today - datetime.timedelta(days=i)
            date_str = day.strftime("%Y-%m-%d")
            key = f"{_KEY_PREFIX}checkin_{stream_id}_{user_id}_{date_str}"
            result = await self._ctx.db.query(
                "PluginData",
                query_type="count",
                filters={"key": key},
            )
            if result and result > 0:
                streak += 1
            else:
                break

        self._streak_cache[cache_key] = streak
        return streak

    # ─── 早安晚安 ────────────────────────────────────────────

    async def greeting(self, stream_id: str, user_id: str, greeting_type: str) -> str:
        """生成早安/晚安问候。"""
        # 获取用户信息
        person_id = await self._ctx.person.get_id("unknown", user_id)
        name = "你"
        if person_id:
            nickname = await self._ctx.person.get_value(person_id, "name")
            if nickname:
                name = nickname

        # 使用 LLM 生成个性化问候
        prompt = f"请用简短、温暖的中文生成一句{greeting_type}问候语，称呼「{name}」，不超过30字。"
        try:
            result = await self._ctx.llm.generate(prompt)
            response = result.get("response", "")
            if response:
                return response.strip()
        except Exception:
            self._ctx.logger.warning("LLM 生成问候失败，使用默认问候")

        if greeting_type == "早安":
            return f"{name}，早安！今天也要元气满满哦~"
        return f"{name}，晚安！好梦~"

    # ─── 节日彩蛋 ────────────────────────────────────────────

    def get_holiday_greeting(self) -> str | None:
        """检查今天是否有节日彩蛋，返回问候语或 None。"""
        today = time.strftime("%m-%d")
        return self.HOLIDAYS.get(today)

    # ─── 接龙 ────────────────────────────────────────────────

    async def start_chain(self, stream_id: str, user_id: str, content: str) -> str:
        """发起接龙。"""
        session = ChainSession(
            creator_id=user_id,
            content=content,
            created_at=time.time(),
        )
        self._chains[stream_id] = session
        return f"接龙已发起：{content}\n发送 /加入接龙 <你的内容> 参与"

    async def join_chain(self, stream_id: str, user_id: str, text: str) -> str:
        """参与接龙。"""
        chain = self._chains.get(stream_id)
        if not chain or not chain.is_active:
            return "当前没有进行中的接龙"

        chain.entries.append({"user_id": user_id, "text": text})
        count = len(chain.entries)
        return f"已参与接龙（第 {count} 位）：{text}"

    async def get_chain(self, stream_id: str) -> str:
        """查看当前接龙。"""
        chain = self._chains.get(stream_id)
        if not chain:
            return "当前没有进行中的接龙"

        lines = [f"接龙：{chain.content}"]
        for i, entry in enumerate(chain.entries, 1):
            lines.append(f"  {i}. {entry['text']}")
        return "\n".join(lines)

    # ─── 数据持久化 ──────────────────────────────────────────

    async def load_persistent_data(self) -> None:
        """加载持久化数据。"""
        data_file = self._data_dir / "entertainment.json"
        if data_file.exists():
            try:
                data = json.loads(data_file.read_text(encoding="utf-8"))
                # 恢复投票状态
                for sid, vdata in data.get("votes", {}).items():
                    self._votes[sid] = VoteSession(
                        creator_id=vdata["creator_id"],
                        options=vdata["options"],
                        votes=vdata.get("votes", {}),
                        is_active=vdata.get("is_active", True),
                    )
                # 恢复接龙状态
                for sid, cdata in data.get("chains", {}).items():
                    self._chains[sid] = ChainSession(
                        creator_id=cdata["creator_id"],
                        content=cdata["content"],
                        entries=cdata.get("entries", []),
                        is_active=cdata.get("is_active", True),
                    )
                self._ctx.logger.info("互动娱乐持久化数据已加载")
            except Exception as e:
                self._ctx.logger.warning(f"加载互动娱乐数据失败: {e}")

    async def save_persistent_data(self) -> None:
        """保存持久化数据。"""
        data_file = self._data_dir / "entertainment.json"
        try:
            self._data_dir.mkdir(parents=True, exist_ok=True)
            data = {
                "votes": {
                    sid: {
                        "creator_id": v.creator_id,
                        "options": v.options,
                        "votes": v.votes,
                        "is_active": v.is_active,
                    }
                    for sid, v in self._votes.items()
                },
                "chains": {
                    sid: {
                        "creator_id": c.creator_id,
                        "content": c.content,
                        "entries": c.entries,
                        "is_active": c.is_active,
                    }
                    for sid, c in self._chains.items()
                },
            }
            data_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            self._ctx.logger.warning(f"保存互动娱乐数据失败: {e}")

    async def cleanup(self) -> None:
        """清理资源。"""
        await self.save_persistent_data()
        self._votes.clear()
        self._chains.clear()
