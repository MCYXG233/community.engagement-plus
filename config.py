"""社区互动增强插件 — 配置模型"""

from typing import ClassVar, List

from maibot_sdk import Field, PluginConfigBase


class PluginSectionConfig(PluginConfigBase):
    """插件基础配置。"""

    __ui_label__: ClassVar[str] = "基础设置"
    config_version: str = Field(default="1.0.0", description="配置版本号")
    enabled: bool = Field(default=True, description="是否启用社区互动增强插件")


class RhythmConfig(PluginConfigBase):
    """节奏控制配置。"""

    __ui_label__: ClassVar[str] = "节奏控制"
    enabled: bool = Field(default=True, description="是否启用节奏控制")
    throttle_interval: int = Field(default=3, description="发言节流间隔（秒）")
    flood_threshold: int = Field(default=5, description="刷屏阈值（条/10秒）")
    repeat_detection_count: int = Field(default=2, description="复读检测阈值（人）")
    silence_reminder_minutes: int = Field(default=30, description="冷场提醒阈值（分钟）")


class QualityConfig(PluginConfigBase):
    """质量优化配置。"""

    __ui_label__: ClassVar[str] = "质量优化"
    enabled: bool = Field(default=True, description="是否启用质量优化")
    dedup_window: int = Field(default=60, description="去重窗口（秒）")


class EntertainmentConfig(PluginConfigBase):
    """互动娱乐配置。"""

    __ui_label__: ClassVar[str] = "互动娱乐"
    enabled: bool = Field(default=True, description="是否启用互动娱乐")


class AtmosphereConfig(PluginConfigBase):
    """氛围监测配置。"""

    __ui_label__: ClassVar[str] = "氛围监测"
    enabled: bool = Field(default=True, description="是否启用氛围监测")
    welcome_enabled: bool = Field(default=True, description="是否启用新人欢迎")


class MemoryConfig(PluginConfigBase):
    """记忆增强配置。"""

    __ui_label__: ClassVar[str] = "记忆增强"
    enabled: bool = Field(default=True, description="是否启用记忆增强")
    profile_fields: List[str] = Field(
        default_factory=lambda: ["活跃时段", "常用表情", "发言主题"],
        description="用户画像统计字段",
    )


class SecurityConfig(PluginConfigBase):
    """风控过滤配置。"""

    __ui_label__: ClassVar[str] = "风控过滤"
    enabled: bool = Field(default=True, description="是否启用风控过滤")
    blocked_words: List[str] = Field(default_factory=list, description="屏蔽词列表")
    fishing_url_patterns: List[str] = Field(default_factory=list, description="钓鱼链接正则模式")


class InputParseConfig(PluginConfigBase):
    """输入解析配置。"""

    __ui_label__: ClassVar[str] = "输入解析"
    enabled: bool = Field(default=True, description="是否启用输入解析")


class OutputFormatConfig(PluginConfigBase):
    """输出美化配置。"""

    __ui_label__: ClassVar[str] = "输出美化"
    enabled: bool = Field(default=True, description="是否启用输出美化")
    max_length: int = Field(default=500, description="长文折叠阈值（字符）")


class PersonaConfig(PluginConfigBase):
    """人格切换配置。"""

    __ui_label__: ClassVar[str] = "人格切换"
    enabled: bool = Field(default=True, description="是否启用人格切换")
    default_persona: str = Field(default="元气", description="默认人格名称")


class PrivacyConfig(PluginConfigBase):
    """隐私保护配置。"""

    __ui_label__: ClassVar[str] = "隐私保护"
    enabled: bool = Field(default=True, description="是否启用隐私保护")
    sensitive_patterns: List[str] = Field(default_factory=list, description="敏感词脱敏正则模式")


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
