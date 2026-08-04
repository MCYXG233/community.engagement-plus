"""社区互动增强插件 — 配置模型"""

from typing import ClassVar, List

from maibot_sdk import Field, PluginConfigBase


class PluginSectionConfig(PluginConfigBase):
    """插件基础配置。"""

    __ui_label__: ClassVar[str] = "基础设置"
    __ui_icon__: ClassVar[str] = "settings"
    __ui_order__: ClassVar[int] = 0

    config_version: str = Field(
        default="1.1.0",
        description="配置版本号",
        json_schema_extra={"label": "配置版本", "disabled": True},
    )
    enabled: bool = Field(
        default=True,
        description="是否启用社区互动增强插件",
        json_schema_extra={"label": "启用插件"},
    )


class RhythmConfig(PluginConfigBase):
    """节奏控制配置。"""

    __ui_label__: ClassVar[str] = "节奏控制"
    __ui_icon__: ClassVar[str] = "speed"
    __ui_order__: ClassVar[int] = 1

    enabled: bool = Field(
        default=True,
        description="是否启用节奏控制",
        json_schema_extra={"label": "启用节奏控制"},
    )
    throttle_interval: int = Field(
        default=3,
        ge=1,
        le=60,
        description="发言节流间隔（秒），用户消息间隔小于此值时静默丢弃",
        json_schema_extra={"label": "节流间隔（秒）", "placeholder": "3"},
    )
    flood_threshold: int = Field(
        default=5,
        ge=2,
        le=50,
        description="刷屏阈值（条/10秒），短时间发送超过此值触发警告",
        json_schema_extra={"label": "刷屏阈值", "placeholder": "5"},
    )
    repeat_detection_count: int = Field(
        default=2,
        ge=2,
        le=20,
        description="复读检测阈值（人），≥此人数发送相同内容触发提醒",
        json_schema_extra={"label": "复读检测阈值", "placeholder": "2"},
    )
    silence_reminder_minutes: int = Field(
        default=30,
        ge=5,
        le=1440,
        description="冷场提醒阈值（分钟），群无消息超过此时间触发提醒",
        json_schema_extra={"label": "冷场提醒（分钟）", "placeholder": "30"},
    )


class QualityConfig(PluginConfigBase):
    """质量优化配置。"""

    __ui_label__: ClassVar[str] = "质量优化"
    __ui_icon__: ClassVar[str] = "auto_fix_high"
    __ui_order__: ClassVar[int] = 2

    enabled: bool = Field(
        default=True,
        description="是否启用质量优化",
        json_schema_extra={"label": "启用质量优化"},
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
        description="需要高亮的关键词列表，匹配的词会添加【】标记。多个关键词用逗号分隔输入",
        json_schema_extra={"label": "高亮关键词", "placeholder": "重要,注意,警告"},
    )


class EntertainmentConfig(PluginConfigBase):
    """互动娱乐配置。"""

    __ui_label__: ClassVar[str] = "互动娱乐"
    __ui_icon__: ClassVar[str] = "celebration"
    __ui_order__: ClassVar[int] = 3

    enabled: bool = Field(
        default=True,
        description="是否启用互动娱乐",
        json_schema_extra={"label": "启用互动娱乐"},
    )


class AtmosphereConfig(PluginConfigBase):
    """氛围监测配置。"""

    __ui_label__: ClassVar[str] = "氛围监测"
    __ui_icon__: ClassVar[str] = "monitor_heart"
    __ui_order__: ClassVar[int] = 4

    enabled: bool = Field(
        default=True,
        description="是否启用氛围监测",
        json_schema_extra={"label": "启用氛围监测"},
    )
    welcome_enabled: bool = Field(
        default=True,
        description="是否启用新人欢迎",
        json_schema_extra={"label": "新人欢迎"},
    )
    sentiment_api_url: str = Field(
        default="",
        description="情绪分析 API 地址，留空禁用。需要兼容 OpenAI 格式的接口",
        json_schema_extra={
            "label": "情绪分析 API 地址",
            "placeholder": "https://api.example.com/v1/chat/completions",
        },
    )
    sentiment_api_key: str = Field(
        default="",
        description="情绪分析 API Key",
        json_schema_extra={"label": "情绪分析 API Key", "placeholder": "sk-..."},
    )


class MemoryConfig(PluginConfigBase):
    """记忆增强配置。"""

    __ui_label__: ClassVar[str] = "记忆增强"
    __ui_icon__: ClassVar[str] = "memory"
    __ui_order__: ClassVar[int] = 5

    enabled: bool = Field(
        default=True,
        description="是否启用记忆增强",
        json_schema_extra={"label": "启用记忆增强"},
    )
    profile_fields: List[str] = Field(
        default_factory=lambda: ["活跃时段", "常用表情", "发言主题"],
        description="用户画像统计字段列表。多个字段用逗号分隔输入",
        json_schema_extra={"label": "画像统计字段", "placeholder": "活跃时段,常用表情,发言主题"},
    )
    cross_session_sync: bool = Field(
        default=True,
        description="是否启用跨会话记忆同步（开启后 LLM 可在会话间搬运用户上下文）",
        json_schema_extra={"label": "跨会话同步", "hint": "开启后 LLM 可跨会话搬运上下文，请评估隐私风险"},
    )


class SecurityConfig(PluginConfigBase):
    """风控过滤配置。"""

    __ui_label__: ClassVar[str] = "风控过滤"
    __ui_icon__: ClassVar[str] = "security"
    __ui_order__: ClassVar[int] = 6

    enabled: bool = Field(
        default=True,
        description="是否启用风控过滤",
        json_schema_extra={"label": "启用风控过滤"},
    )
    blocked_words: List[str] = Field(
        default_factory=list,
        description="屏蔽词列表，命中即拦截。多个词用逗号分隔输入",
        json_schema_extra={"label": "屏蔽词列表", "placeholder": "广告,推销,加群"},
    )
    fishing_url_patterns: List[str] = Field(
        default_factory=list,
        description="钓鱼链接正则模式列表。留空使用内置默认规则，自定义时每个正则一行",
        json_schema_extra={"label": "钓鱼链接正则", "placeholder": "留空使用默认规则"},
    )
    image_check_api_url: str = Field(
        default="",
        description="图片审核 API 地址，留空禁用。需要接收 base64 图片并返回审核结果",
        json_schema_extra={
            "label": "图片审核 API 地址",
            "placeholder": "https://api.example.com/v1/image/audit",
        },
    )
    image_check_api_key: str = Field(
        default="",
        description="图片审核 API Key",
        json_schema_extra={"label": "图片审核 API Key", "placeholder": "sk-..."},
    )


class InputParseConfig(PluginConfigBase):
    """输入解析配置。"""

    __ui_label__: ClassVar[str] = "输入解析"
    __ui_icon__: ClassVar[str] = "input"
    __ui_order__: ClassVar[int] = 7

    enabled: bool = Field(
        default=True,
        description="是否启用输入解析",
        json_schema_extra={"label": "启用输入解析"},
    )
    merge_window: int = Field(
        default=5,
        ge=1,
        le=30,
        description="多消息合并窗口（秒），同一用户在此时间内的连续消息合并展示",
        json_schema_extra={"label": "合并窗口（秒）", "placeholder": "5"},
    )


class OutputFormatConfig(PluginConfigBase):
    """输出美化配置。"""

    __ui_label__: ClassVar[str] = "输出美化"
    __ui_icon__: ClassVar[str] = "format_paint"
    __ui_order__: ClassVar[int] = 8

    enabled: bool = Field(
        default=True,
        description="是否启用输出美化",
        json_schema_extra={"label": "启用输出美化"},
    )
    max_length: int = Field(
        default=500,
        ge=100,
        le=5000,
        description="长文折叠阈值（字符），超过此长度自动折叠",
        json_schema_extra={"label": "长文折叠阈值", "placeholder": "500"},
    )
    translate_api_url: str = Field(
        default="",
        description="翻译 API 地址，留空禁用。使用 /翻译 命令按需翻译",
        json_schema_extra={
            "label": "翻译 API 地址",
            "placeholder": "https://api.example.com/v1/translate",
        },
    )
    translate_api_key: str = Field(
        default="",
        description="翻译 API Key",
        json_schema_extra={"label": "翻译 API Key", "placeholder": "sk-..."},
    )
    translate_target_lang: str = Field(
        default="en",
        description="翻译目标语言代码",
        json_schema_extra={"label": "翻译目标语言", "placeholder": "en"},
    )


class PersonaConfig(PluginConfigBase):
    """人格切换配置。"""

    __ui_label__: ClassVar[str] = "人格切换"
    __ui_icon__: ClassVar[str] = "person"
    __ui_order__: ClassVar[int] = 9

    enabled: bool = Field(
        default=True,
        description="是否启用人格切换",
        json_schema_extra={"label": "启用人格切换"},
    )
    default_persona: str = Field(
        default="元气",
        description="默认人格名称，可选：元气、毒舌、温柔、学术",
        json_schema_extra={"label": "默认人格", "placeholder": "元气"},
    )
    mood_driven: bool = Field(
        default=True,
        description="是否启用心情驱动人格（LLM 自动根据消息情绪切换人格）",
        json_schema_extra={"label": "心情驱动", "hint": "开启后 LLM 会根据消息情绪自动切换人格"},
    )


class PrivacyConfig(PluginConfigBase):
    """隐私保护配置。"""

    __ui_label__: ClassVar[str] = "隐私保护"
    __ui_icon__: ClassVar[str] = "shield"
    __ui_order__: ClassVar[int] = 10

    enabled: bool = Field(
        default=True,
        description="是否启用隐私保护",
        json_schema_extra={"label": "启用隐私保护"},
    )
    sensitive_patterns: List[str] = Field(
        default_factory=list,
        description="敏感词脱敏正则列表。留空使用内置默认规则（手机号/邮箱/身份证），自定义时每个正则一行",
        json_schema_extra={"label": "脱敏正则", "placeholder": "留空使用默认规则"},
    )
    encrypt_profiles: bool = Field(
        default=False,
        description="是否加密用户画像数据（Base64 编码，非安全加密）",
        json_schema_extra={"label": "画像加密", "hint": "轻量混淆，非真正加密"},
    )


class CommunityEngagementConfig(PluginConfigBase):
    """社区互动增强插件 — 顶层配置模型。"""

    plugin: PluginSectionConfig = Field(default_factory=PluginSectionConfig, description="插件基础配置")
    rhythm: RhythmConfig = Field(default_factory=RhythmConfig, description="节奏控制")
    quality: QualityConfig = Field(default_factory=QualityConfig, description="质量优化")
    entertainment: EntertainmentConfig = Field(default_factory=EntertainmentConfig, description="互动娱乐")
    atmosphere: AtmosphereConfig = Field(default_factory=AtmosphereConfig, description="氛围监测")
    memory: MemoryConfig = Field(default_factory=MemoryConfig, description="记忆增强")
    security: SecurityConfig = Field(default_factory=SecurityConfig, description="风控过滤")
    input_parse: InputParseConfig = Field(default_factory=InputParseConfig, description="输入解析")
    output_format: OutputFormatConfig = Field(default_factory=OutputFormatConfig, description="输出美化")
    persona: PersonaConfig = Field(default_factory=PersonaConfig, description="人格切换")
    privacy: PrivacyConfig = Field(default_factory=PrivacyConfig, description="隐私保护")
