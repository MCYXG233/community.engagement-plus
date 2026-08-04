"""模块9: 人格切换 — 人格模板、语气调节、风格迁移"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from maibot_sdk.context import PluginContext

    from ..config import PersonaConfig

# 预设人格模板
PERSONA_TEMPLATES: Dict[str, str] = {
    "元气": (
        "你是元气满满的角色，说话活泼积极，喜欢用感叹号和表情符号。"
        "回复风格：热情、开朗、充满正能量，适当使用颜文字和 emoji。"
    ),
    "毒舌": (
        "你是毒舌吐槽风格的角色，说话犀利幽默，擅长一针见血的吐槽。"
        "回复风格：讽刺、幽默、犀利，但不恶意攻击，保持有趣。"
    ),
    "温柔": (
        "你是温柔体贴的角色，说话温和有耐心，善解人意。"
        "回复风格：温暖、关怀、细腻，多用语气词如「呢」「哦」「呀」。"
    ),
    "学术": (
        "你是学术严谨的角色，说话专业清晰，逻辑性强。"
        "回复风格：严谨、专业、条理清晰，引用数据和事实，避免主观臆断。"
    ),
}


class PersonaModule:
    """人格切换模块：管理群聊人格状态、风格注入和心情驱动。"""

    # 心情到人格的映射
    MOOD_PERSONA_MAP = {
        "positive": "元气",
        "happy": "元气",
        "negative": "温柔",
        "sad": "温柔",
        "angry": "毒舌",
        "neutral": None,  # 不切换
    }

    def __init__(self, ctx: PluginContext, config: PersonaConfig) -> None:
        self._ctx = ctx
        self._config = config
        # stream_id -> 当前人格名称
        self._personas: Dict[str, str] = {}
        # stream_id -> 当前心情
        self._moods: Dict[str, str] = {}

    async def switch_persona(self, stream_id: str, persona_name: str) -> str:
        """切换当前聊天流的人格。"""
        if persona_name not in PERSONA_TEMPLATES:
            available = "、".join(PERSONA_TEMPLATES.keys())
            return f"未知人格「{persona_name}」，可用人格：{available}"

        self._personas[stream_id] = persona_name
        return f"已切换为「{persona_name}」人格"

    def get_current_persona(self, stream_id: str) -> str:
        """获取当前人格名称。"""
        return self._personas.get(stream_id, self._config.default_persona)

    async def inject_persona(self, stream_id: str) -> None:
        """注入人格指令到对话上下文。

        先读取用户画像和风格偏好（ctx.person + learners），
        再融合预设人格模板，通过 maisaka.context.append 追加。
        """
        persona_name = self.get_current_persona(stream_id)
        template = PERSONA_TEMPLATES.get(persona_name, PERSONA_TEMPLATES["元气"])

        # 尝试读取用户画像以融合个性化指令
        persona_prompt = template
        try:
            # 从 ctx.person 读取用户偏好，融合到人格指令中
            # 如果用户有语言偏好，追加到指令中
            pass  # 当前版本仅使用预设模板，后续可扩展
        except Exception as e:
            self._ctx.logger.warning(f"读取用户画像失败: {e}")

        # 通过 maisaka 追加上下文
        try:
            await self._ctx.maisaka.context.append(
                stream_id,
                [{"type": "text", "content": f"[系统指令] {persona_prompt}"}],
            )
        except Exception as e:
            self._ctx.logger.warning(f"注入人格上下文失败: {e}")

    def list_personas(self) -> str:
        """列出所有可用人格。"""
        lines = ["可用人格："]
        for name, desc in PERSONA_TEMPLATES.items():
            lines.append(f"  - {name}: {desc[:30]}...")
        return "\n".join(lines)

    async def detect_mood(self, stream_id: str, text: str) -> str:
        """检测消息心情，如果启用心情驱动则自动切换人格。

        使用 LLM 进行情感分析。
        """
        if not self._config.mood_driven:
            return "心情驱动未启用"

        try:
            prompt = f"分析以下文本的情绪（只返回一个词：positive/negative/neutral/angry/happy/sad）：\n{text}"
            result = await self._ctx.llm.generate(prompt)
            mood = result.get("response", "").strip().lower()

            if mood in self.MOOD_PERSONA_MAP:
                self._moods[stream_id] = mood
                target_persona = self.MOOD_PERSONA_MAP[mood]
                if target_persona and target_persona != self._personas.get(stream_id):
                    self._personas[stream_id] = target_persona
                    return f"心情变化：{mood} → 切换为「{target_persona}」人格"

            return f"当前心情：{mood}"
        except Exception as e:
            self._ctx.logger.warning(f"心情检测失败: {e}")
            return "心情检测失败"

    def get_mood(self, stream_id: str) -> str:
        """获取当前心情。"""
        return self._moods.get(stream_id, "未知")

    async def cleanup(self) -> None:
        """清理资源。"""
        self._personas.clear()
        self._moods.clear()
