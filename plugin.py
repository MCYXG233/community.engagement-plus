"""社区互动增强插件 — 主入口

提供 10 大功能模块：节奏控制、质量优化、互动娱乐、氛围监测、
记忆增强、风控过滤、输入解析、输出美化、人格切换、隐私保护。
"""

from __future__ import annotations

from typing import Any, ClassVar, Dict

from maibot_sdk import (
    Command,
    EventHandler,
    Field,
    HookHandler,
    MaiBotPlugin,
    PluginConfigBase,
    Tool,
)
from maibot_sdk.types import HookMode, HookOrder, ToolParameterInfo, ToolParamType

from .config import CommunityEngagementConfig
from .modules import (
    AtmosphereModule,
    EntertainmentModule,
    InputParseModule,
    MemoryEnhanceModule,
    OutputFormatModule,
    PersonaModule,
    PrivacyModule,
    QualityModule,
    RhythmModule,
    SecurityModule,
)


class CommunityEngagementPlusPlugin(MaiBotPlugin):
    """社区互动增强插件"""

    config_model = CommunityEngagementConfig

    def __init__(self) -> None:
        super().__init__()
        # 模块实例（在 on_load 中初始化）
        self._rhythm: RhythmModule = None  # type: ignore[assignment]
        self._quality: QualityModule = None  # type: ignore[assignment]
        self._entertainment: EntertainmentModule = None  # type: ignore[assignment]
        self._atmosphere: AtmosphereModule = None  # type: ignore[assignment]
        self._memory: MemoryEnhanceModule = None  # type: ignore[assignment]
        self._security: SecurityModule = None  # type: ignore[assignment]
        self._input_parse: InputParseModule = None  # type: ignore[assignment]
        self._output_format: OutputFormatModule = None  # type: ignore[assignment]
        self._persona: PersonaModule = None  # type: ignore[assignment]
        self._privacy: PrivacyModule = None  # type: ignore[assignment]

    # ─── 生命周期 ────────────────────────────────────────────

    async def on_load(self) -> None:
        """插件加载：初始化 10 个模块实例"""
        self.ctx.logger.info("社区互动增强插件加载中...")

        # 初始化各模块
        self._rhythm = RhythmModule(self.ctx, self.config.rhythm)
        self._quality = QualityModule(self.ctx, self.config.quality)
        self._entertainment = EntertainmentModule(self.ctx, self.config.entertainment)
        self._atmosphere = AtmosphereModule(self.ctx, self.config.atmosphere)
        self._memory = MemoryEnhanceModule(self.ctx, self.config.memory)
        self._security = SecurityModule(self.ctx, self.config.security)
        self._input_parse = InputParseModule(self.ctx, self.config.input_parse)
        self._output_format = OutputFormatModule(self.ctx, self.config.output_format)
        self._persona = PersonaModule(self.ctx, self.config.persona)
        self._privacy = PrivacyModule(self.ctx, self.config.privacy)

        # 加载持久化数据
        await self._entertainment.load_persistent_data()

        self.ctx.logger.info("社区互动增强插件加载完成，共加载 10 个模块")

    async def on_unload(self) -> None:
        """插件卸载：保存状态、清理资源"""
        self.ctx.logger.info("社区互动增强插件卸载中...")

        # 保存持久化数据
        await self._entertainment.save_persistent_data()

        # 清理各模块资源
        for module in [
            self._rhythm, self._quality, self._entertainment,
            self._atmosphere, self._memory, self._security,
            self._input_parse, self._output_format,
            self._persona, self._privacy,
        ]:
            if hasattr(module, "cleanup"):
                await module.cleanup()

        self.ctx.logger.info("社区互动增强插件卸载完成")

    async def on_config_update(self, scope: str, config_data: dict, version: str) -> None:
        """配置热更新：通知各模块刷新配置"""
        self.ctx.logger.info(f"收到配置更新: scope={scope}, version={version}")
        if scope == "self":
            for module in [
                self._rhythm, self._quality, self._entertainment,
                self._atmosphere, self._memory, self._security,
                self._input_parse, self._output_format,
                self._persona, self._privacy,
            ]:
                if hasattr(module, "on_config_update"):
                    await module.on_config_update(config_data)

    # ─── EventHandler: 消息过滤器 ───────────────────────────

    @EventHandler(
        "消息过滤器",
        description="合并风控+节奏控制：拦截违规内容、刷屏、节流、复读",
        event_type="on_message_pre_process",
        intercept_message=True,
        weight=10,
    )
    async def handle_message_filter(self, message: Any, **kwargs) -> Any:
        """统一消息过滤：风控检查 → 节奏检查。"""
        # 风控检查
        result = await self._security.check_message(message)
        if result is None:
            return None

        # 节奏检查
        result = await self._rhythm.check_message(message)
        return result

    # ─── EventHandler: 新人欢迎 ─────────────────────────────

    @EventHandler(
        "新人欢迎器",
        description="检测新用户首次发言并发送欢迎消息",
        event_type="on_message",
        intercept_message=False,
        weight=0,
    )
    async def handle_new_user(self, message: Any, **kwargs) -> None:
        """检查新用户并发送欢迎消息。"""
        welcome = await self._atmosphere.check_new_user(message)
        if welcome:
            stream_id = message.get("session_id", "")
            if stream_id:
                await self.ctx.send.text(welcome, stream_id)

    # ─── HookHandler: 输出美化钩子 ─────────────────────────

    @HookHandler(
        "send_service.before_send",
        name="社区互动_输出美化",
        mode=HookMode.BLOCKING,
        order=HookOrder.NORMAL,
    )
    async def hook_output_format(self, **kwargs) -> dict:
        """在发送前美化消息格式。"""
        text = kwargs.get("text", "")
        stream_id = kwargs.get("stream_id", "")
        if text and self._output_format:
            formatted = await self._output_format.format_output(text, stream_id)
            if formatted != text:
                kwargs["text"] = formatted
        return {"action": "continue", "modified_kwargs": kwargs}

    # ─── Commands ───────────────────────────────────────────

    @Command("社区帮助", description="查看所有社区互动命令", pattern=r"^/社区帮助\s*$")
    async def handle_help(self, stream_id: str = "", **kwargs) -> None:
        """显示帮助信息。"""
        help_text = (
            "社区互动增强 — 命令帮助\n"
            "━━━ 互动娱乐 ━━━\n"
            "/投票 <选项1> <选项2> ... — 发起投票\n"
            "/投票1 /投票2 ... — 对应选项投票\n"
            "/投票结果 — 查看投票结果\n"
            "/结束投票 — 结束当前投票\n"
            "/抽奖 [人数] — 随机抽取幸运用户\n"
            "/打卡 — 每日签到打卡\n"
            "/连续打卡 — 查看连续打卡天数\n"
            "/早安 — 早安问候\n"
            "/晚安 — 晚安问候\n"
            "/接龙 <内容> — 发起接龙\n"
            "/加入接龙 <内容> — 参与接龙\n"
            "━━━ 氛围监测 ━━━\n"
            "/活跃榜 [天数] — 查看活跃排行\n"
            "/群温度 — 查看群活跃温度\n"
            "/潜水 [天数] — 查看潜水用户\n"
            "━━━ 记忆增强 ━━━\n"
            "/画像 [用户] — 查看用户画像\n"
            "/回顾 — 共同记忆回顾\n"
            "━━━ 人格切换 ━━━\n"
            "/切换人格 <名称> — 切换人格\n"
            "/当前人格 — 查看当前人格\n"
            "━━━ 隐私保护 ━━━\n"
            "/导出数据 — 导出用户数据\n"
            "/注销 — 注销并清理数据\n"
        )
        await self.ctx.send.text(help_text, stream_id)

    # ─── 互动娱乐命令 ──────────────────────────────────────

    @Command("投票", description="发起投票", pattern=r"^/投票\s+(?P<options>.+)$")
    async def handle_create_vote(self, stream_id: str = "", user_id: str = "", matched_groups: dict | None = None, **kwargs) -> None:
        """发起投票。"""
        raw = (matched_groups or {}).get("options", "")
        options = [o.strip() for o in raw.split() if o.strip()]
        result = await self._entertainment.create_vote(stream_id, user_id, options)
        await self.ctx.send.text(result, stream_id)

    @Command("投票选择", description="投票选择", pattern=r"^/投票(?P<number>\d+)\s*$")
    async def handle_cast_vote(self, stream_id: str = "", user_id: str = "", matched_groups: dict | None = None, **kwargs) -> None:
        """投票。"""
        number = int((matched_groups or {}).get("number", "1")) - 1
        result = await self._entertainment.cast_vote(stream_id, user_id, number)
        await self.ctx.send.text(result, stream_id)

    @Command("投票结果", description="查看投票结果", pattern=r"^/投票结果\s*$")
    async def handle_vote_result(self, stream_id: str = "", **kwargs) -> None:
        """查看投票结果。"""
        result = await self._entertainment.get_vote_result(stream_id)
        await self.ctx.send.text(result, stream_id)

    @Command("结束投票", description="结束投票", pattern=r"^/结束投票\s*$")
    async def handle_end_vote(self, stream_id: str = "", **kwargs) -> None:
        """结束投票。"""
        result = await self._entertainment.end_vote(stream_id)
        await self.ctx.send.text(result, stream_id)

    @Command("抽奖", description="抽奖", pattern=r"^/抽奖\s*(?P<count>\d*)\s*$")
    async def handle_lottery(self, stream_id: str = "", matched_groups: dict | None = None, **kwargs) -> None:
        """抽奖。"""
        count_str = (matched_groups or {}).get("count", "1")
        count = int(count_str) if count_str else 1
        result = await self._entertainment.lottery(stream_id, count)
        await self.ctx.send.text(result, stream_id)

    @Command("打卡", description="每日签到", pattern=r"^/打卡\s*$")
    async def handle_check_in(self, stream_id: str = "", user_id: str = "", **kwargs) -> None:
        """每日签到。"""
        result = await self._entertainment.check_in(stream_id, user_id)
        await self.ctx.send.text(result, stream_id)

    @Command("连续打卡", description="查看连续打卡天数", pattern=r"^/连续打卡\s*$")
    async def handle_streak(self, stream_id: str = "", user_id: str = "", **kwargs) -> None:
        """查看连续打卡天数。"""
        streak = await self._entertainment._calc_streak(stream_id, user_id)
        await self.ctx.send.text(f"连续打卡 {streak} 天", stream_id)

    @Command("早安", description="早安问候", pattern=r"^/早安\s*$")
    async def handle_gmorning(self, stream_id: str = "", user_id: str = "", **kwargs) -> None:
        """早安问候。"""
        result = await self._entertainment.greeting(stream_id, user_id, "早安")
        await self.ctx.send.text(result, stream_id)

    @Command("晚安", description="晚安问候", pattern=r"^/晚安\s*$")
    async def handle_gnight(self, stream_id: str = "", user_id: str = "", **kwargs) -> None:
        """晚安问候。"""
        result = await self._entertainment.greeting(stream_id, user_id, "晚安")
        await self.ctx.send.text(result, stream_id)

    @Command("接龙", description="发起接龙", pattern=r"^/接龙\s+(?P<content>.+)$")
    async def handle_start_chain(self, stream_id: str = "", user_id: str = "", matched_groups: dict | None = None, **kwargs) -> None:
        """发起接龙。"""
        content = (matched_groups or {}).get("content", "")
        result = await self._entertainment.start_chain(stream_id, user_id, content)
        await self.ctx.send.text(result, stream_id)

    @Command("加入接龙", description="参与接龙", pattern=r"^/加入接龙\s+(?P<text>.+)$")
    async def handle_join_chain(self, stream_id: str = "", user_id: str = "", matched_groups: dict | None = None, **kwargs) -> None:
        """参与接龙。"""
        text = (matched_groups or {}).get("text", "")
        result = await self._entertainment.join_chain(stream_id, user_id, text)
        await self.ctx.send.text(result, stream_id)

    # ─── 氛围监测命令 ──────────────────────────────────────

    @Command("活跃榜", description="查看活跃排行", pattern=r"^/活跃榜\s*(?P<days>\d*)\s*$")
    async def handle_active_rank(self, stream_id: str = "", matched_groups: dict | None = None, **kwargs) -> None:
        """查看活跃排行。"""
        days_str = (matched_groups or {}).get("days", "7")
        days = int(days_str) if days_str else 7
        result = await self._atmosphere.get_active_rank(stream_id, days)
        await self.ctx.send.text(result, stream_id)

    @Command("群温度", description="查看群活跃温度", pattern=r"^/群温度\s*$")
    async def handle_temperature(self, stream_id: str = "", **kwargs) -> None:
        """查看群活跃温度。"""
        result = await self._atmosphere.get_temperature(stream_id)
        await self.ctx.send.text(result, stream_id)

    @Command("潜水", description="查看潜水用户", pattern=r"^/潜水\s*(?P<days>\d*)\s*$")
    async def handle_lurkers(self, stream_id: str = "", matched_groups: dict | None = None, **kwargs) -> None:
        """查看潜水用户。"""
        days_str = (matched_groups or {}).get("days", "7")
        days = int(days_str) if days_str else 7
        result = await self._atmosphere.get_lurkers(stream_id, days)
        await self.ctx.send.text(result, stream_id)

    # ─── 记忆增强命令 ──────────────────────────────────────

    @Command("画像", description="查看用户画像", pattern=r"^/画像\s*(?P<user>.*)\s*$")
    async def handle_profile(self, stream_id: str = "", user_id: str = "", matched_groups: dict | None = None, **kwargs) -> None:
        """查看用户画像。"""
        target_user = (matched_groups or {}).get("user", "").strip() or user_id
        result = await self._memory.get_user_profile(stream_id, target_user)
        await self.ctx.send.text(result, stream_id)

    @Command("回顾", description="共同记忆回顾", pattern=r"^/回顾\s*$")
    async def handle_recall(self, stream_id: str = "", **kwargs) -> None:
        """共同记忆回顾。"""
        result = await self._memory.memory_recall(stream_id)
        await self.ctx.send.text(result, stream_id)

    # ─── 人格切换命令 ──────────────────────────────────────

    @Command("切换人格", description="切换人格", pattern=r"^/切换人格\s+(?P<name>.+)$")
    async def handle_switch_persona(self, stream_id: str = "", matched_groups: dict | None = None, **kwargs) -> None:
        """切换人格。"""
        name = (matched_groups or {}).get("name", "")
        result = await self._persona.switch_persona(stream_id, name)
        await self.ctx.send.text(result, stream_id)

    @Command("当前人格", description="查看当前人格", pattern=r"^/当前人格\s*$")
    async def handle_current_persona(self, stream_id: str = "", **kwargs) -> None:
        """查看当前人格。"""
        current = self._persona.get_current_persona(stream_id)
        await self.ctx.send.text(f"当前人格：{current}", stream_id)

    # ─── 隐私保护命令 ──────────────────────────────────────

    @Command("导出数据", description="导出用户数据", pattern=r"^/导出数据\s*$")
    async def handle_export(self, stream_id: str = "", user_id: str = "", **kwargs) -> None:
        """导出用户数据。"""
        result = await self._privacy.export_data(user_id)
        await self.ctx.send.text(result, stream_id)

    @Command("注销", description="注销并清理数据", pattern=r"^/注销\s*$")
    async def handle_delete(self, stream_id: str = "", user_id: str = "", **kwargs) -> None:
        """注销并清理数据。"""
        result = await self._privacy.delete_user_data(user_id)
        await self.ctx.send.text(result, stream_id)

    # ─── Tools ──────────────────────────────────────────────

    @Tool(
        "get_group_temperature",
        description="查询群聊活跃温度",
        parameters=[
            ToolParameterInfo(
                name="stream_id",
                param_type=ToolParamType.STRING,
                description="聊天流 ID",
                required=True,
            ),
        ],
    )
    async def tool_group_temperature(self, stream_id: str = "", **kwargs) -> dict:
        """LLM 工具：查询群温度。"""
        result = await self._atmosphere.get_temperature(stream_id)
        return {"temperature": result}

    @Tool(
        "get_user_profile",
        description="查询用户画像",
        parameters=[
            ToolParameterInfo(
                name="stream_id",
                param_type=ToolParamType.STRING,
                description="聊天流 ID",
                required=True,
            ),
            ToolParameterInfo(
                name="user_id",
                param_type=ToolParamType.STRING,
                description="用户 ID",
                required=True,
            ),
        ],
    )
    async def tool_user_profile(self, stream_id: str = "", user_id: str = "", **kwargs) -> dict:
        """LLM 工具：查询用户画像。"""
        result = await self._memory.get_user_profile(stream_id, user_id)
        return {"profile": result}

    @Tool(
        "recall_memory",
        description="共同记忆回顾",
        parameters=[
            ToolParameterInfo(
                name="stream_id",
                param_type=ToolParamType.STRING,
                description="聊天流 ID",
                required=True,
            ),
        ],
    )
    async def tool_recall_memory(self, stream_id: str = "", **kwargs) -> dict:
        """LLM 工具：共同记忆回顾。"""
        result = await self._memory.memory_recall(stream_id)
        return {"recall": result}

    @Tool(
        "sanitize_text",
        description="文本敏感词脱敏",
        parameters=[
            ToolParameterInfo(
                name="text",
                param_type=ToolParamType.STRING,
                description="待脱敏文本",
                required=True,
            ),
        ],
    )
    async def tool_sanitize(self, text: str = "", **kwargs) -> dict:
        """LLM 工具：文本脱敏。"""
        result = self._privacy.sanitize(text)
        return {"sanitized": result}


def create_plugin() -> CommunityEngagementPlusPlugin:
    """插件工厂函数。"""
    return CommunityEngagementPlusPlugin()
