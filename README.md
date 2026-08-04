# 社区互动增强插件 v1.0.0

> **插件说明**：CommunityEngagementPlus 是 MaiBot 第三方社区互动增强插件，提供 10 大功能模块。
>
> 作者：[MCYXG233](https://github.com/MCYXG233)
>
> 仓库：[community.engagement-plus](https://github.com/MCYXG233/community.engagement-plus)

---

## 功能说明

- **节奏控制**：发言节流、刷屏拦截、复读检测、冷场提醒
- **质量优化**：表情去重、复读合并、链接去重
- **互动娱乐**：投票、抽奖、打卡、早安晚安、接龙
- **氛围监测**：群温度计、活跃榜、新人欢迎、潜水党召回
- **记忆增强**：用户画像聚合、共同记忆回顾
- **风控过滤**：关键词屏蔽、钓鱼链接拦截、诱导分享检测
- **输入解析**：@ 检测、回复上下文提取、引用追溯
- **输出美化**：分段发送、长文折叠、表情插入
- **人格切换**：元气/毒舌/温柔/学术 四套预设人格
- **隐私保护**：敏感词脱敏、数据导出、注销清理

---

## 快速开始

1. 安装 SDK：`pip install maibot-plugin-sdk>=2.7.1`
2. 将 `CommunityEngagementPlus` 放入 MaiBot 插件目录（`plugins/` 文件夹）。
   ```bash
   cd plugins
   git clone git@github.com:MCYXG233/community.engagement-plus.git CommunityEngagementPlus
   ```
3. 启动 MaiBot，插件会自动加载。
4. 在群聊中发送 `/社区帮助` 查看所有可用命令。

---

## 插件配置

配置文件：`CommunityEngagementPlus/config.toml`（首次加载后自动生成）

### plugin 基础配置

- `enabled`：是否启用插件，默认 `true`。

### rhythm 节奏控制

- `enabled`：是否启用，默认 `true`。
- `throttle_interval`：发言节流间隔（秒），默认 `3`。
- `flood_threshold`：刷屏阈值（条/10秒），默认 `5`。
- `repeat_detection_count`：复读检测阈值（人），默认 `2`。
- `silence_reminder_minutes`：冷场提醒阈值（分钟），默认 `30`。

### quality 质量优化

- `enabled`：是否启用，默认 `true`。
- `dedup_window`：去重窗口（秒），默认 `60`。

### entertainment 互动娱乐

- `enabled`：是否启用，默认 `true`。

### atmosphere 氛围监测

- `enabled`：是否启用，默认 `true`。
- `welcome_enabled`：新人欢迎开关，默认 `true`。

### memory 记忆增强

- `enabled`：是否启用，默认 `true`。
- `profile_fields`：画像统计字段列表，默认 `["活跃时段", "常用表情", "发言主题"]`。

### security 风控过滤

- `enabled`：是否启用，默认 `true`。
- `blocked_words`：屏蔽词列表，默认为空。
- `fishing_url_patterns`：钓鱼链接正则，默认内置常见短链接。

### input_parse 输入解析

- `enabled`：是否启用，默认 `true`。

### output_format 输出美化

- `enabled`：是否启用，默认 `true`。
- `max_length`：长文折叠阈值（字符），默认 `500`。

### persona 人格切换

- `enabled`：是否启用，默认 `true`。
- `default_persona`：默认人格名称，默认 `元气`。

### privacy 隐私保护

- `enabled`：是否启用，默认 `true`。
- `sensitive_patterns`：脱敏正则列表，默认内置手机号/邮箱/身份证。

---

## 命令列表

### 互动娱乐

| 命令 | 说明 |
|------|------|
| `/投票 <选项1> <选项2> ...` | 发起投票 |
| `/投票1` `/投票2` ... | 对应选项投票 |
| `/投票结果` | 查看投票结果 |
| `/结束投票` | 结束当前投票 |
| `/抽奖 [人数]` | 随机抽取幸运用户 |
| `/打卡` | 每日签到打卡 |
| `/连续打卡` | 查看连续打卡天数 |
| `/早安` | 早安问候（LLM 生成） |
| `/晚安` | 晚安问候（LLM 生成） |
| `/接龙 <内容>` | 发起接龙 |
| `/加入接龙 <内容>` | 参与接龙 |

### 氛围监测

| 命令 | 说明 |
|------|------|
| `/活跃榜 [天数]` | 查看活跃排行 |
| `/群温度` | 查看群活跃温度 |
| `/潜水 [天数]` | 查看潜水用户 |

### 记忆增强

| 命令 | 说明 |
|------|------|
| `/画像 [用户]` | 查看用户画像 |
| `/回顾` | 共同记忆回顾 |

### 人格切换

| 命令 | 说明 |
|------|------|
| `/切换人格 <名称>` | 切换人格（元气/毒舌/温柔/学术） |
| `/当前人格` | 查看当前人格 |

### 隐私保护

| 命令 | 说明 |
|------|------|
| `/导出数据` | 导出用户数据 |
| `/注销` | 注销并清理数据 |

### 通用

| 命令 | 说明 |
|------|------|
| `/社区帮助` | 查看所有命令帮助 |

---

## 使用建议

- 强烈建议在更新插件前备份当前插件文件，以免意外丢失。
- 风控过滤的屏蔽词和钓鱼链接正则可在配置文件中自定义。
- 人格切换仅影响当前聊天流，不同群可设置不同人格。
- 打卡数据和投票数据存储在 MaiBot 数据库中，卸载插件不会丢失。

---

## 隐私与数据说明

本插件默认**不**向外部发送任何数据。以下功能在启用后会将用户数据发送到第三方 API，**需管理员自行配置 API 地址和密钥**（默认留空即禁用）：

| 功能 | 配置项 | 发送的数据 | 说明 |
|------|--------|-----------|------|
| 图片鉴黄 | `security.image_check_api_url` | 消息中的图片 base64 | 发送到配置的审核 API，用于检测违规图片 |
| 情绪分析 | `atmosphere.sentiment_api_url` | 最近 20 条消息文本 | 发送到配置的情绪分析 API，用于生成情绪仪表盘 |
| 翻译备注 | `output_format.translate_api_url` | 输出消息文本 | 发送到配置的翻译 API，自动附加翻译备注 |

**请注意：**
- 以上 API 地址和密钥由管理员在 MaiBot WebUI 中配置，插件不会自动启用
- 启用前请确认第三方 API 的隐私政策和数据处理方式
- 图片 base64 数据体积较大，建议配置内网或可信 API
- 所有数据仅在 API 调用时传输，插件不存储外部 API 的响应数据

---

## 更新日志

### 版本 1.1.0

**功能补全**

- 冷场提醒：跟踪每个群的最后消息时间，超过阈值时触发提醒
- 周年纪念：检测用户首次发言日期，匹配时生成周年祝福
- 节日彩蛋：7 个节日（新年/情人节/劳动节/儿童节/国庆/圣诞/跨年）
- 情绪仪表盘：调用外部 API 分析群聊情绪
- 翻译备注：调用外部 API 自动附加翻译
- 图片鉴黄：调用外部 API 审核违规图片
- 关键词高亮：配置的关键词添加 【】 标记
- 多消息合并：缓冲窗口期内同一用户的连续消息
- 跨会话记忆同步：LLM 提取关键信息并同步到其他会话
- 心情驱动人格：LLM 情感分析自动切换人格
- 画像加密：Base64 编码保护用户画像数据
- 撤回检测：检测消息撤回并通知
- /节日、/周年、/情绪、/心情 命令

**代码修复**

- 导入修复：`HookMode`/`HookOrder`/`ToolParameterInfo`/`ToolParamType` 改从 `maibot_sdk.types` 导入
- 隐私修复：`delete_user_data` 限定只删 `community_engagement_` 前缀的数据
- 隐私修复：`/注销` 同时清理 PluginData 表和 entertainment.json
- 配置修复：`scope` 比较使用 `CONFIG_RELOAD_SCOPE_SELF` 常量
- Tool 修复：所有 `@Tool` 使用 `brief_description`（文档推荐）
- 持久化修复：`load_persistent_data` 恢复投票和接龙状态到内存
- 性能修复：`_calc_streak` 用 `count` 替代 `get`，遇中断即停止
- 多 Bot 协调：非 @ 非命令消息跳过节奏控制
- 管道接入：`quality.check_outgoing`、`input_parse.parse`、`output_format.split_long_message` 全部接入 HookHandler
- 移除空壳：`check_silence` 空实现、`hook_input_parse` 空钩子

**配置扩展**

- 新增外部 API 配置：图片审核、情绪分析、翻译（用户自填 URL + Key）
- 新增功能开关：心情驱动、跨会话同步、画像加密、关键词高亮、多消息合并
- 配置版本升级至 1.1.0

**文档与合规**

- README 新增「隐私与数据说明」章节，列出外部 API 数据流向
- 移除未使用的 `_locales` 目录和 manifest `i18n` 块
- manifest capabilities 从 30 项精简到 11 项（仅实际使用）
- 所有 Command 处理函数补全返回三元组 `(success, response, weight)`

### 版本 1.0.0

- 完成 10 大功能模块开发：节奏控制、质量优化、互动娱乐、氛围监测、记忆增强、风控过滤、输入解析、输出美化、人格切换、隐私保护
- 使用 `@Tool`/`@Command`/`@EventHandler`/`@HookHandler` 装饰器
- 使用 `PluginConfigBase` 定义强类型配置（11 个配置节）
- 实现三个必需的生命周期方法：`on_load()`、`on_unload()`、`on_config_update()`
- 添加 `create_plugin()` 工厂函数
- 通过 `ctx.*` 能力代理复用 MaiBot 原生能力（db/llm/person/message/maisaka/emoji/frequency）
- 22 个 Command + 2 个 EventHandler + 2 个 HookHandler + 4 个 Tool
- 投票/接龙数据持久化，打卡记录存入数据库

---

## 致谢

- MaiBot 团队：[Mai-with-u/maibot](https://github.com/MaiM-with-u/maibot)
- MaiBot Plugin SDK：[maibot-plugin-sdk](https://github.com/Mai-with-u/maibot-plugin-sdk)
