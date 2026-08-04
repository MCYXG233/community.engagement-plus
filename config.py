"""社区互动增强插件 — 配置模型"""

from typing import ClassVar, List

from maibot_sdk import Field, PluginConfigBase


class GeneralConfig(PluginConfigBase):
    """通用设置。"""

    __ui_label__: ClassVar[str] = "通用设置"
    __ui_icon__: ClassVar[str] = "settings"
    __ui_order__: ClassVar[int] = 0

    enabled: bool = Field(
        default=True,
        description="启用社区互动增强插件",
        json_schema_extra={"label": "启用插件"},
    )
    config_version: str = Field(
        default="1.2.0",
        description="配置版本号",
        json_schema_extra={"label": "配置版本", "disabled": True},
    )


class MessageControlConfig(PluginConfigBase):
    """发言管理 — 节流、刷屏、复读、冷场。"""

    __ui_label__: ClassVar[str] = "发言管理"
    __ui_icon__: ClassVar[str] = "speed"
    __ui_order__: ClassVar[int] = 1

    enabled: bool = Field(
        default=True,
        description="启用发言管理（节流、刷屏拦截、复读检测）",
        json_schema_extra={"label": "启用发言管理"},
    )
    throttle_seconds: int = Field(
        default=3,
        ge=1,
        le=60,
        description="发言最小间隔（秒），用户消息间隔小于此值时静默丢弃",
        json_schema_extra={"label": "发言间隔（秒）", "placeholder": "3"},
    )
    flood_threshold: int = Field(
        default=5,
        ge=2,
        le=50,
        description="刷屏阈值（条/10秒），短时间发送超过此值触发警告",
        json_schema_extra={"label": "刷屏阈值", "placeholder": "5"},
    )
    repeat_threshold: int = Field(
        default=2,
        ge=2,
        le=20,
        description="复读检测阈值（人），≥此人数发送相同内容触发提醒",
        json_schema_extra={"label": "复读检测阈值", "placeholder": "2"},
    )
    silence_reminder: bool = Field(
        default=True,
        description="启用冷场提醒（群无消息超过30分钟时自动提醒）",
        json_schema_extra={"label": "冷场提醒"},
    )
    silence_minutes: int = Field(
        default=30,
        ge=5,
        le=1440,
        description="冷场提醒阈值（分钟）",
        json_schema_extra={"label": "冷场阈值（分钟）", "placeholder": "30"},
    )


class MessageOptimizeConfig(PluginConfigBase):
    """消息优化 — 链接去重、关键词高亮、长文折叠。"""

    __ui_label__: ClassVar[str] = "消息优化"
    __ui_icon__: ClassVar[str] = "auto_fix_high"
    __ui_order__: ClassVar[int] = 2

    enabled: bool = Field(
        default=True,
        description="启用消息优化（链接去重、长文折叠）",
        json_schema_extra={"label": "启用消息优化"},
    )
    dedup_window: int = Field(
        default=60,
        ge=10,
        le=600,
        description="链接去重窗口（秒），相同 URL 在此时间内不重复展示",
        json_schema_extra={"label": "去重窗口（秒）", "placeholder": "60"},
    )
    highlight_keywords: List[str] = Field(
        default_factory=list,
        description="高亮关键词列表，匹配的词会添加【】标记",
        json_schema_extra={"label": "高亮关键词", "placeholder": "重要,注意,警告"},
    )
    max_length: int = Field(
        default=500,
        ge=100,
        le=5000,
        description="长文折叠阈值（字符），超过此长度自动折叠",
        json_schema_extra={"label": "长文折叠阈值", "placeholder": "500"},
    )


class FunConfig(PluginConfigBase):
    """互动娱乐 — 投票、抽奖、打卡、接龙、节日彩蛋。"""

    __ui_label__: ClassVar[str] = "互动娱乐"
    __ui_icon__: ClassVar[str] = "celebration"
    __ui_order__: ClassVar[int] = 3

    enabled: bool = Field(
        default=True,
        description="启用互动娱乐（投票、抽奖、打卡、接龙、节日彩蛋）",
        json_schema_extra={"label": "启用互动娱乐"},
    )
    holiday_eggs: bool = Field(
        default=True,
        description="启用节日彩蛋（元旦、情人节等自动发送祝福）",
        json_schema_extra={"label": "节日彩蛋"},
    )


class WelcomeConfig(PluginConfigBase):
    """新人欢迎。"""

    __ui_label__: ClassVar[str] = "新人欢迎"
    __ui_icon__: ClassVar[str] = "waving_hand"
    __ui_order__: ClassVar[int] = 4

    enabled: bool = Field(
        default=True,
        description="启用新人欢迎（检测新用户首次发言并发送欢迎消息）",
        json_schema_extra={"label": "启用新人欢迎"},
    )
    welcome_template: str = Field(
        default="欢迎 {name} 加入群聊！发送 /社区帮助 查看可用命令",
        description="欢迎消息模板，{name} 会替换为用户名",
        json_schema_extra={"label": "欢迎消息", "placeholder": "欢迎 {name} 加入群聊！"},
    )


class AtmosphereConfig(PluginConfigBase):
    """氛围监测 — 群温度、活跃榜、潜水检测、情绪分析。"""

    __ui_label__: ClassVar[str] = "氛围监测"
    __ui_icon__: ClassVar[str] = "monitor_heart"
    __ui_order__: ClassVar[int] = 5

    enabled: bool = Field(
        default=True,
        description="启用氛围监测（群温度、活跃榜、潜水检测）",
        json_schema_extra={"label": "启用氛围监测"},
    )
    sentiment_api_url: str = Field(
        default="",
        description="情绪分析 API 地址（可选），留空则禁用 /情绪 命令",
        json_schema_extra={
            "label": "情绪分析 API",
            "placeholder": "https://api.example.com/v1/chat/completions",
        },
    )
    sentiment_api_key: str = Field(
        default="",
        description="情绪分析 API Key",
        json_schema_extra={"label": "情绪分析 Key", "placeholder": "sk-..."},
    )


class MemoryConfig(PluginConfigBase):
    """记忆增强 — 用户画像、共同回忆、跨会话同步。"""

    __ui_label__: ClassVar[str] = "记忆增强"
    __ui_icon__: ClassVar[str] = "memory"
    __ui_order__: ClassVar[int] = 6

    enabled: bool = Field(
        default=True,
        description="启用记忆增强（用户画像、共同回忆）",
        json_schema_extra={"label": "启用记忆增强"},
    )
    profile_fields: List[str] = Field(
        default_factory=lambda: ["活跃时段", "常用表情", "发言主题"],
        description="用户画像统计字段",
        json_schema_extra={"label": "画像字段", "placeholder": "活跃时段,常用表情,发言主题"},
    )
    cross_session_sync: bool = Field(
        default=False,
        description="启用跨会话记忆同步（LLM 可在会话间搬运用户上下文）",
        json_schema_extra={"label": "跨会话同步", "hint": "请评估隐私风险"},
    )


class SecurityConfig(PluginConfigBase):
    """安全过滤 — 屏蔽词、钓鱼链接、图片审核。"""

    __ui_label__: ClassVar[str] = "安全过滤"
    __ui_icon__: ClassVar[str] = "security"
    __ui_order__: ClassVar[int] = 7

    enabled: bool = Field(
        default=True,
        description="启用安全过滤（屏蔽词、钓鱼链接检测）",
        json_schema_extra={"label": "启用安全过滤"},
    )
    blocked_words: List[str] = Field(
        default_factory=list,
        description="屏蔽词列表，命中即拦截消息",
        json_schema_extra={"label": "屏蔽词", "placeholder": "广告,推销,加群"},
    )
    fishing_url_patterns: List[str] = Field(
        default_factory=list,
        description="钓鱼链接正则（留空使用内置默认规则）",
        json_schema_extra={"label": "钓鱼链接规则", "placeholder": "留空使用默认"},
    )
    image_check_api_url: str = Field(
        default="",
        description="图片审核 API 地址（可选），留空则跳过图片检测",
        json_schema_extra={"label": "图片审核 API", "placeholder": "https://api.example.com/audit"},
    )
    image_check_api_key: str = Field(
        default="",
        description="图片审核 API Key",
        json_schema_extra={"label": "图片审核 Key", "placeholder": "sk-..."},
    )


class TranslateConfig(PluginConfigBase):
    """翻译设置。"""

    __ui_label__: ClassVar[str] = "翻译"
    __ui_icon__: ClassVar[str] = "translate"
    __ui_order__: ClassVar[int] = 8

    enabled: bool = Field(
        default=False,
        description="启用翻译功能（/翻译 命令）",
        json_schema_extra={"label": "启用翻译"},
    )
    api_url: str = Field(
        default="",
        description="翻译 API 地址",
        json_schema_extra={"label": "翻译 API", "placeholder": "https://api.example.com/translate"},
    )
    api_key: str = Field(
        default="",
        description="翻译 API Key",
        json_schema_extra={"label": "翻译 Key", "placeholder": "sk-..."},
    )
    target_lang: str = Field(
        default="en",
        description="翻译目标语言代码",
        json_schema_extra={"label": "目标语言", "placeholder": "en"},
    )


class PersonaConfig(PluginConfigBase):
    """人格切换 — 预设人格、心情驱动。"""

    __ui_label__: ClassVar[str] = "人格切换"
    __ui_icon__: ClassVar[str] = "person"
    __ui_order__: ClassVar[int] = 9

    enabled: bool = Field(
        default=False,
        description="启用人格切换（/切换人格 命令）",
        json_schema_extra={"label": "启用人格切换"},
    )
    default_persona: str = Field(
        default="元气",
        description="默认人格，可选：元气、毒舌、温柔、学术",
        json_schema_extra={"label": "默认人格", "placeholder": "元气"},
    )
    mood_driven: bool = Field(
        default=False,
        description="启用心情驱动（LLM 根据消息情绪自动切换人格）",
        json_schema_extra={"label": "心情驱动", "hint": "开启后会消耗额外 LLM 调用"},
    )


class PrivacyConfig(PluginConfigBase):
    """隐私保护 — 数据导出、注销清理。"""

    __ui_label__: ClassVar[str] = "隐私保护"
    __ui_icon__: ClassVar[str] = "shield"
    __ui_order__: ClassVar[int] = 10

    enabled: bool = Field(
        default=True,
        description="启用隐私保护（/导出数据、/注销 命令）",
        json_schema_extra={"label": "启用隐私保护"},
    )
    sensitive_patterns: List[str] = Field(
        default_factory=list,
        description="敏感词脱敏正则（留空使用内置默认：手机号/邮箱/身份证）",
        json_schema_extra={"label": "脱敏规则", "placeholder": "留空使用默认"},
    )
    encrypt_profiles: bool = Field(
        default=False,
        description="加密用户画像数据（Base64 编码）",
        json_schema_extra={"label": "画像加密", "hint": "轻量混淆，非安全加密"},
    )


class CommunityEngagementConfig(PluginConfigBase):
    """社区互动增强插件 — 顶层配置模型。"""

    general: GeneralConfig = Field(default_factory=GeneralConfig, description="通用设置")
    message_control: MessageControlConfig = Field(default_factory=MessageControlConfig, description="发言管理")
    message_optimize: MessageOptimizeConfig = Field(default_factory=MessageOptimizeConfig, description="消息优化")
    fun: FunConfig = Field(default_factory=FunConfig, description="互动娱乐")
    welcome: WelcomeConfig = Field(default_factory=WelcomeConfig, description="新人欢迎")
    atmosphere: AtmosphereConfig = Field(default_factory=AtmosphereConfig, description="氛围监测")
    memory: MemoryConfig = Field(default_factory=MemoryConfig, description="记忆增强")
    security: SecurityConfig = Field(default_factory=SecurityConfig, description="安全过滤")
    translate: TranslateConfig = Field(default_factory=TranslateConfig, description="翻译")
    persona: PersonaConfig = Field(default_factory=PersonaConfig, description="人格切换")
    privacy: PrivacyConfig = Field(default_factory=PrivacyConfig, description="隐私保护")
