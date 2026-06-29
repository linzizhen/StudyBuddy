"""
StudyPal 搭子系统
整合搭子档案、记忆、关心引擎的完整搭子

这是整个产品的灵魂模块：
1. 搭子记忆 — 记住关于用户的一切
2. 搭子性格 — 有温度、有态度的搭子
3. 搭子对话 — 场景化、个性化的对话生成
4. 主动关心 — 不只是被动回答

作者：StudyPal
日期：2026-04-27
重构：2026-04-27 v2.0
"""

import re
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from src.buddy.buddy_profile import BuddyProfile, get_buddy_profile
from src.buddy.buddy_memory import BuddyMemory, get_buddy_memory
from src.buddy.caring_engine import CaringEngine, CaringEvent, get_caring_engine
from src.study.study_tracker import StudyTracker, get_study_tracker
from src.diary.diary import Diary, get_diary, EmotionTracker, get_emotion_tracker, DiaryEntry
from src.ai.prompt_templates import get_prompt_templates


def _safe_console_print(text: str):
    """Windows 控制台 GBK 编码下安全打印（含 emoji）"""
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode(encoding, errors="replace").decode(encoding, errors="replace"))


class Buddy:
    """
    StudyPal 搭子类

    三个核心能力：
    1. 记忆能力 — 记住关于用户的一切
    2. 性格能力 — 有温度、有态度的搭子
    3. 关心能力 — 主动发起关心，不只是被动回答
    """

    # 情绪状态定义（保留旧版风格，增强版）
    EMOTIONS = {
        "idle": {"emoji": "😴", "desc": "休息中~", "priority": 0},
        "happy": {"emoji": "😊", "desc": "开心！", "priority": 1},
        "excited": {"emoji": "🎉", "desc": "太棒了！", "priority": 2},
        "proud": {"emoji": "😤", "desc": "为你骄傲！", "priority": 2},
        "thinking": {"emoji": "🤔", "desc": "在思考...", "priority": 1},
        "study": {"emoji": "📚", "desc": "学习中！", "priority": 1},
        "worried": {"emoji": "😟", "desc": "有点担心...", "priority": 1},
        "sad": {"emoji": "😢", "desc": "难过...", "priority": 1},
        "angry": {"emoji": "😡", "desc": "生气！", "priority": 2},
        "sleepy": {"emoji": "😪", "desc": "好困啊...", "priority": 0},
    }

    def __init__(self, supervisor=None):
        # 核心模块
        self.profile: BuddyProfile = get_buddy_profile()
        self.memory: BuddyMemory = get_buddy_memory()
        self.study: StudyTracker = get_study_tracker()
        self.diary: Diary = get_diary()
        self.emotion_tracker: EmotionTracker = get_emotion_tracker()
        self.caring: CaringEngine = get_caring_engine()
        self.prompts = get_prompt_templates()
        self._supervisor = supervisor  # 兼容旧版 Session

        # 当前情绪状态
        self._current_emotion = "idle"
        self._emotion_history: List[Dict] = []

        # 初始化关心引擎的追踪器
        self.caring.set_trackers(
            study_tracker=self.study,
            diary_tracker=self.emotion_tracker,
            memory=self.memory
        )

        # 最后活跃时间
        self._last_active = datetime.now()

        # 初始化时检查时间相关情绪
        self._check_time_emotion()

    # ========== 情绪系统 ==========

    def get_emotion(self) -> str:
        """获取当前情绪名称"""
        return self._current_emotion

    def get_emoji(self) -> str:
        """获取当前情绪的 emoji"""
        return self.EMOTIONS.get(self._current_emotion, {}).get("emoji", "😶")

    def get_emotion_desc(self) -> str:
        """获取当前情绪描述"""
        return self.EMOTIONS.get(self._current_emotion, {}).get("desc", "")

    def set_emotion(self, emotion: str):
        """设置搭子情绪"""
        if emotion in self.EMOTIONS:
            if self._current_emotion != emotion:
                self._emotion_history.append({
                    "from": self._current_emotion,
                    "to": emotion,
                    "time": datetime.now().isoformat()
                })
            self._current_emotion = emotion

    def update_emotion_by_action(self, action: str):
        """根据动作更新情绪"""
        action_map = {
            "ask": "thinking",
            "answer_received": "happy",
            "study_start": "study",
            "study_finish": "excited",
            "achievement": "proud",
            "long_idle": "sad",
            "very_long_idle": "angry",
            "late_night": "sleepy",
            "user_struggle": "worried",
            "user_giving_up": "sad",
        }
        if action in action_map:
            self.set_emotion(action_map[action])
        self._last_active = datetime.now()

    # 兼容旧版接口
    def update_by_action(self, action: str):
        """根据动作更新情绪（兼容旧版）"""
        self.update_emotion_by_action(action)

    def _check_time_emotion(self):
        """检查时间相关情绪"""
        now = datetime.now()
        hour = now.hour

        if 23 <= hour or hour <= 5:
            if self._current_emotion in ["study", "thinking"]:
                self.set_emotion("sleepy")

        elapsed_hours = (now - self._last_active).total_seconds() / 3600
        if elapsed_hours > 4 and self._current_emotion == "idle":
            self.set_emotion("sad")
        elif elapsed_hours > 8:
            self.set_emotion("angry")

    def get_emotion_history(self) -> List[Dict]:
        """获取情绪历史"""
        return self._emotion_history[-10:]

    # ========== 对话系统 ==========

    def chat(
        self,
        message: str,
        conversation_id: str = None,
        game_mode: str = 'auto',
        history_messages: List[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        搭子对话

        这是搭子的核心方法，处理用户消息并返回搭子的回复

        返回：
        {
            "reply": str,           # 搭子回复
            "conversation_id": str, # 对话ID
            "emotion": str,         # 当前情绪
            "emoji": str,           # 情绪emoji
            "memory_hints": []      # 相关记忆提示
        }
        """
        # 更新活跃时间
        self._last_active = datetime.now()
        self.study.record_activity()

        # 分析消息情绪
        emotion_analysis = self._analyze_message_emotion(message)

        # 根据情绪更新搭子表情
        if emotion_analysis["is_negative"]:
            self.update_emotion_by_action("user_struggle")
        elif emotion_analysis["is_positive"]:
            self.set_emotion("happy")
        else:
            self.set_emotion("thinking")

        # 构建 AI 回复
        knowledge_config = self._resolve_knowledge_mode(
            emotion_analysis.get("is_knowledge", False),
            game_mode,
        )
        reply = self._generate_reply(
            message,
            emotion_analysis,
            conversation_id,
            knowledge_config,
            history_messages=history_messages,
        )

        from src.buddy.option_parser import (
            parse_chat_options,
            detect_game_over,
            strip_game_markers,
            is_game_option_message,
        )
        options, option_texts = parse_chat_options(reply)
        is_game_followup = is_game_option_message(message, game_mode)
        in_game_context = knowledge_config.get("use_gamification") or is_game_followup
        game_over = False
        if in_game_context:
            game_over = detect_game_over(reply, options, in_active_game=is_game_followup)
            if game_over or re.search(r'\[(GAME_OVER|END)\]', reply, re.IGNORECASE):
                reply = strip_game_markers(reply)

        # 如果检测到重要事件，记录到记忆
        self._record_memory_from_message(message, reply, emotion_analysis)

        # 重置情绪
        self.set_emotion("idle")

        return {
            "reply": reply,
            "conversation_id": conversation_id,
            "emotion": self.get_emotion(),
            "emoji": self.get_emoji(),
            "emotion_desc": self.get_emotion_desc(),
            "suggestions": self._generate_suggestions(message, emotion_analysis),
            "options": options,
            "option_texts": option_texts,
            "game_over": game_over,
            "game_mode": game_mode,
            "use_gamification": (
                knowledge_config.get("use_gamification", False)
                or (is_game_followup and not game_over)
            ),
            "role_consistency": getattr(self, "_last_role_consistency", None),
        }

    def _resolve_knowledge_mode(self, is_knowledge: bool, game_mode: str) -> Dict[str, Any]:
        """根据用户 game_mode 与搭子性格，决定知识点讲解方式"""
        from src.buddy.buddy_roles import BuddyRoles
        role_key = self.profile.get_buddy_info().get("role_key", "xiaodou")
        game_style = BuddyRoles.get_game_style(role_key)
        mode = (game_mode or 'auto').lower()

        if not is_knowledge:
            return {"use_gamification": False, "style": game_style, "mode": mode}

        if mode == 'direct':
            return {"use_gamification": False, "style": "direct", "mode": mode}
        if mode == 'game':
            style = game_style if game_style != 'direct' else 'battle'
            return {"use_gamification": True, "style": style, "mode": mode}
        # auto
        if game_style == 'direct':
            return {"use_gamification": False, "style": "direct", "mode": mode}
        return {"use_gamification": True, "style": game_style, "mode": mode}

    def _analyze_message_emotion(self, message: str) -> Dict[str, Any]:
        """
        分析用户消息的情绪

        返回：
        {
            "sentiment": str,        # positive/negative/neutral
            "is_negative": bool,
            "is_positive": bool,
            "is_giving_up": bool,   # 想放弃
            "is_anxious": bool,     # 焦虑
            "keywords": [],          # 关键词
            "intent": str,           # 意图
        }
        """
        message_lower = message.lower()

        # 检测负面情绪
        negative_keywords = ["考不上", "放弃", "不想学了", "好难", "崩溃", "绝望",
                            "压力大", "焦虑", "迷茫", "累", "烦", "沮丧", "难熬"]
        is_negative = any(kw in message_lower for kw in negative_keywords)

        # 检测想放弃
        give_up_keywords = ["不想考了", "不考了", "放弃了", "算了吧", "考不上的"]
        is_giving_up = any(kw in message_lower for kw in give_up_keywords)

        # 检测焦虑
        anxious_keywords = ["焦虑", "紧张", "怕", "担心", "慌"]
        is_anxious = any(kw in message_lower for kw in anxious_keywords)

        # 检测正面情绪
        positive_keywords = ["好开心", "太棒了", "完成了", "学会了", "谢谢", "加油",
                           "有进步", "感觉好多了"]
        is_positive = any(kw in message_lower for kw in positive_keywords)

        # 检测意图（知识点优先于泛化的「什么/怎么」）
        knowledge_keywords = [
            "什么是", "是什么", "怎么理解", "解释一下", "给我讲讲",
            "概念", "定义", "含义", "说说",
        ]
        is_knowledge = False
        knowledge_keyword = None
        for kw in knowledge_keywords:
            if kw in message_lower:
                is_knowledge = True
                knowledge_keyword = kw
                break

        intent = "chat"
        if is_knowledge:
            intent = "knowledge"
        elif any(kw in message_lower for kw in ["怎么", "如何", "什么"]):
            intent = "question"
        elif any(kw in message_lower for kw in ["计划", "安排", "复习"]):
            intent = "plan"
        elif any(kw in message_lower for kw in ["学不进去", "拖延"]):
            intent = "struggle"

        _safe_console_print(f"用户消息: {message}")
        _safe_console_print(f"是否知识点: {is_knowledge}")
        _safe_console_print(f"匹配到的关键词: {knowledge_keyword}")

        # 提取关键词
        keywords = []
        for kw in negative_keywords + positive_keywords + ["数学", "英语", "政治",
                    "专业课", "高数", "线代", "概率", "单词", "政治", "真题"]:
            if kw in message_lower:
                keywords.append(kw)

        return {
            "sentiment": "negative" if is_negative else ("positive" if is_positive else "neutral"),
            "is_negative": is_negative,
            "is_positive": is_positive,
            "is_giving_up": is_giving_up,
            "is_anxious": is_anxious,
            "keywords": keywords,
            "intent": intent,
            "is_knowledge": is_knowledge,
            "knowledge_keyword": knowledge_keyword,
        }

    def _generate_reply(
        self,
        message: str,
        emotion_analysis: Dict,
        conversation_id: str = None,
        knowledge_config: Dict = None,
        history_messages: List[Dict[str, str]] = None,
    ) -> str:
        """
        生成搭子回复

        这里调用 AI 模型，结合记忆和上下文生成回复
        包含身份一致性校验：若回复串台，自动重试 1 次，最终 fallback
        """
        # 从旧版 AI 模块获取对话能力
        from src.ai.ai_helper import get_ai_instance
        from src.ai.role_identity import (
            validate_role_consistency,
            build_reinforcement_prompt,
            fallback_reply,
        )
        ai = get_ai_instance()

        knowledge_config = knowledge_config or {}
        is_knowledge = emotion_analysis.get("is_knowledge", False)
        use_gamification = knowledge_config.get("use_gamification", False)

        # 当前角色
        role_key = self.profile.get_buddy_info().get("role_key", "xiaodou")

        # 构建系统提示词
        system_prompt = self._build_system_prompt(
            is_knowledge=is_knowledge,
            knowledge_config=knowledge_config,
        )

        # 构建用户消息
        user_message = self._build_user_message(
            message, emotion_analysis, use_gamification=use_gamification
        )

        try:
            if is_knowledge and use_gamification:
                from src.buddy.buddy_roles import BuddyRoles
                style = knowledge_config.get("style", "battle")
                style_hint = {
                    "battle": "记住：必须用⚡开头、对战竞技式回复，给A/B/C选项带游戏数值。",
                    "simulation": "记住：必须用经营语言，给A/B/C选项带收入/成本数值。",
                    "murder_mystery": "记住：必须用剧本杀语气，给A/B/C剧情分支。",
                }.get(style, "记住：必须先给A/B/C选项，禁止直接讲定义。")
                user_message = f"{user_message}\n\n{style_hint}"

            use_hist = bool(history_messages) and not (is_knowledge and use_gamification)

            # 第一次生成
            current_system_prompt = system_prompt
            result = ai.ask(
                question=user_message,
                conversation_id=None,
                system_prompt=current_system_prompt,
                prompt_mode='user_merged' if (is_knowledge and use_gamification) else 'default',
                use_history=use_hist,
                history_messages=history_messages if use_hist else None,
                temperature=0.9 if (is_knowledge and use_gamification) else None,
                top_p=0.95 if (is_knowledge and use_gamification) else None,
                save_to_history=False,
            )
            reply = result.get("answer", "我在呢，有什么事？")

            # 身份一致性校验
            valid, reason = validate_role_consistency(reply, role_key)
            self._last_role_consistency = {
                "valid": valid,
                "reason": reason,
                "role_key": role_key,
            }

            if valid:
                return reply

            # 校验失败：重试 1 次（追加强化提醒）
            _safe_console_print(f"[搭子身份校验] 失败：{reason}，尝试重试")
            reinforced_prompt = current_system_prompt + build_reinforcement_prompt(role_key)
            result2 = ai.ask(
                question=user_message,
                conversation_id=None,
                system_prompt=reinforced_prompt,
                prompt_mode='user_merged' if (is_knowledge and use_gamification) else 'default',
                use_history=False,   # 重试时不带历史，避免污染
                history_messages=None,
                temperature=0.7,     # 降温度，更稳定
                top_p=0.9,
                save_to_history=False,
            )
            reply2 = result2.get("answer", "")
            valid2, reason2 = validate_role_consistency(reply2, role_key)
            if valid2 and reply2.strip():
                _safe_console_print(f"[搭子身份校验] 重试成功")
                self._last_role_consistency = {
                    "valid": True,
                    "reason": None,
                    "role_key": role_key,
                }
                return reply2

            # 最终兜底
            _safe_console_print(f"[搭子身份校验] 重试仍失败（{reason2}），使用 fallback")
            self._last_role_consistency = {
                "valid": False,
                "reason": reason2 or reason,
                "role_key": role_key,
            }
            return fallback_reply(role_key)
        except Exception as e:
            _safe_console_print(f"[搭子对话] AI 调用失败: {e}")
            return self._fallback_reply(message, emotion_analysis)

    def _build_system_prompt(
        self,
        is_knowledge: bool = False,
        knowledge_config: Dict = None,
    ) -> str:
        """
        构建系统提示词

        新版结构（2026-06-25 改造）：
        1. 基础 prompt（StudyPal 搭子身份 + 回复规则）
        2. 角色身份铁律（来自 role_identity，6 个角色独立）
        3. 知识点模式注入（直接 / 游戏化）
        4. 场景上下文（科目、时长、情绪）
        5. 记忆摘要（去角色化）
        """
        from src.ai.role_identity import build_system_prompt as build_identity_prompt

        knowledge_config = knowledge_config or {}
        use_gamification = knowledge_config.get("use_gamification", False)
        effective_style = knowledge_config.get("style", "direct")
        profile = self.profile.get_user()
        buddy_info = self.profile.get_buddy_info()
        role_key = buddy_info.get("role_key", "xiaodou")
        memory_context = self.memory.build_context_for_ai()
        current_phase = self.profile.get_current_phase()
        study_summary = self.profile.get_study_summary()

        # 获取基础提示词
        base_prompt = self.prompts.get_system_prompt(
            buddy_name=buddy_info.get("name", "小豆"),
            user_name=profile.get("name", ""),
            study_summary=study_summary,
            memory_context="",  # 移到 identity 块里，避免重复
            current_phase=current_phase
        )

        # 场景上下文
        exam_type = profile.get("target_school", "考研") or "考研"
        study_duration = 0
        try:
            stats = self.study.get_stats()
            study_duration = int(stats.get("today_hours", 0) * 60)
        except Exception:
            pass
        user_mood = "未知"
        try:
            today_diary = self.diary.get_today()
            if today_diary:
                user_mood = today_diary.emotion_label or "未知"
        except Exception:
            pass

        # 用新模板构建（含身份铁律 + 场景 + 记忆）
        final_prompt = build_identity_prompt(
            role_key=role_key,
            base_prompt=base_prompt,
            exam_type=exam_type,
            study_duration=study_duration,
            user_mood=user_mood,
            memory_summary=memory_context,
        )

        if is_knowledge:
            from src.buddy.buddy_roles import BuddyRoles, GAME_STYLE_FORCE_RULES
            if use_gamification:
                force_rules = GAME_STYLE_FORCE_RULES.get(
                    effective_style,
                    BuddyRoles.get_game_style_force_rules(role_key),
                )
                final_prompt += "\n\n" + force_rules
                final_prompt += "\n\n【本轮覆盖规则】用户在问知识点，忽略上方「回复2-4句话」限制，必须先给A/B/C/D等选项（至少2个），禁止直接讲定义。游戏化讲解结束时请在回复末尾加 [GAME_OVER]，且不要再给选项。"
            else:
                force_rules = GAME_STYLE_FORCE_RULES.get("direct", "")
                final_prompt += "\n\n" + force_rules
                final_prompt += "\n\n【本轮覆盖规则】用户在问知识点，用简洁结构化方式直接讲解，不要游戏化包装。"

        _safe_console_print("=" * 50)
        _safe_console_print(f"当前搭子: {buddy_info.get('name', '未知')}")
        _safe_console_print(f"是否知识点模式: {is_knowledge}")
        _safe_console_print(f"讲解模式: {knowledge_config.get('mode', 'auto')}, 游戏化: {use_gamification}")
        _safe_console_print("=" * 50)

        return final_prompt

    def _build_user_message(
        self,
        message: str,
        emotion_analysis: Dict,
        use_gamification: bool = False,
    ) -> str:
        """构建用户消息"""
        parts = [message]

        # 添加情绪上下文
        if emotion_analysis["is_giving_up"]:
            parts.append("\n[注意：用户表达了想放弃的情绪，需要重点关心]")
        elif emotion_analysis["is_anxious"]:
            parts.append("\n[注意：用户有些焦虑，需要安慰和理解]")
        elif emotion_analysis["is_negative"]:
            parts.append("\n[注意：用户情绪不太好，需要关心]")

        # 添加知识点询问标记
        if emotion_analysis.get("is_knowledge"):
            if use_gamification:
                game_style = self._get_current_game_style()
                style_names = {
                    "simulation": "模拟经营式",
                    "battle": "对战竞技式",
                    "detective": "侦探推理式",
                    "rpg": "RPG冒险式",
                    "murder_mystery": "剧本杀式",
                    "direct": "直接讲解式"
                }
                parts.append("\n[注意：用户在询问知识点，必须游戏化讲解，先给A/B/C选项，禁止直接讲定义]")
                parts.append(f"\n[游戏风格：{style_names.get(game_style, '直接讲解式')}]")
            else:
                parts.append("\n[注意：用户在询问知识点，请用简洁直接的方式讲解，不要游戏化]")

        # 添加今日上下文
        today_entry = self.diary.get_today()
        if today_entry:
            parts.append(f"\n[今日情绪：{today_entry.emotion_label}]")

        # 添加学习上下文
        stats = self.study.get_stats()
        if stats.get("is_studying"):
            minutes = self.study.get_continuous_study_minutes()
            parts.append(f"\n[用户正在学习中，已学习 {int(minutes)} 分钟]")
        elif stats.get("today_hours", 0) > 0:
            parts.append(f"\n[今日已学习 {stats['today_hours']:.1f} 小时]")

        return "\n".join(parts)
    
    def _get_current_game_style(self) -> str:
        """获取当前搭子的游戏化讲解风格"""
        from src.buddy.buddy_roles import BuddyRoles
        buddy_info = self.profile.get_buddy_info()
        role_key = buddy_info.get("role_key", "xiaodou")
        return BuddyRoles.get_game_style(role_key)

    def _fallback_reply(
        self,
        message: str,
        emotion_analysis: Dict
    ) -> str:
        """备用回复（AI 不可用时）"""
        if emotion_analysis["is_giving_up"]:
            return "我知道你现在很难，但是你不是一个人。不管怎样，我都在这里陪着你。"

        if emotion_analysis["is_anxious"]:
            return "焦虑是很正常的，说明你在乎这件事。深呼吸，我们一起慢慢来。"

        if emotion_analysis["is_negative"]:
            return "听起来你今天不太顺利，想聊聊吗？我一直在。"

        if "怎么学" in message or "如何" in message:
            return "这个问题很好！我们聊聊你的具体情况吧，你现在复习到哪一步了？"

        return "嗯嗯，我听懂了。还有什么想说的吗？"

    def _generate_suggestions(
        self,
        message: str,
        emotion_analysis: Dict
    ) -> List[str]:
        """生成回复建议"""
        suggestions = []

        if emotion_analysis["is_giving_up"]:
            suggestions = [
                "聊聊为什么想放弃",
                "我陪你休息一下",
                "给自己放半天假"
            ]
        elif emotion_analysis["is_anxious"]:
            suggestions = [
                "我帮你分析一下",
                "今天学了什么？",
                "深呼吸，慢慢来"
            ]
        elif emotion_analysis["intent"] == "plan":
            suggestions = [
                "制定今日计划",
                "调整复习安排",
                "看看学习进度"
            ]
        else:
            suggestions = [
                "今天感觉怎么样？",
                "最近学习顺利吗？",
                "有什么想聊的吗？"
            ]

        return suggestions[:3]

    def _record_memory_from_message(
        self,
        message: str,
        reply: str,
        emotion_analysis: Dict
    ):
        """从对话中提取并记录重要记忆"""
        message_lower = message.lower()

        # 检测是否提到具体科目或章节
        subject_keywords = {
            "高数": "高数", "数学": "高数", "线代": "线代", "概率": "概率论",
            "英语": "英语", "单词": "英语", "政治": "政治",
            "专业课": "专业课", "408": "专业课"
        }

        mentioned_subjects = [v for k, v in subject_keywords.items() if k in message_lower]
        if mentioned_subjects:
            self.memory.add_scene(
                summary=f"聊到了{','.join(mentioned_subjects)}",
                scene_type="conversation",
                details=message[:100],
                tags=mentioned_subjects
            )

        # 检测是否提到情绪
        if emotion_analysis["is_negative"]:
            self.memory.set_profile_note(
                "recent_feeling",
                emotion_analysis.get("sentiment", "negative")
            )

        # 检测重要意图
        if "目标" in message or "想考" in message:
            self.memory.add_scene(
                summary=f"讨论了考研目标",
                scene_type="conversation",
                details=message[:100],
                tags=["目标"]
            )

    # ========== 关心系统 ==========

    def check_caring_events(self) -> List[CaringEvent]:
        """检查并返回需要触发的关心事件"""
        return self.caring.check_all()

    def trigger_achievement(
        self,
        achievement_type: str,
        sub_key: str = None,
        context: Dict = None
    ) -> Optional[CaringEvent]:
        """触发成就庆祝关心"""
        return self.caring.trigger_achievement(achievement_type, sub_key, context)

    def trigger_emotion_support(
        self,
        emotion: str,
        emotion_level: int
    ) -> CaringEvent:
        """触发情绪支持关心"""
        return self.caring.trigger_emotion_support(emotion, emotion_level)

    # ========== 档案与记忆 API ==========

    def get_profile(self) -> Dict[str, Any]:
        """获取用户档案"""
        profile = self.profile.get_profile()
        profile["days_remaining"] = self.profile.get_days_remaining()
        profile["current_phase"] = self.profile.get_current_phase()
        profile["emotion"] = self.get_emotion()
        profile["emoji"] = self.get_emoji()
        return profile

    def update_profile(self, **kwargs) -> bool:
        """更新用户档案"""
        self.profile.update_user(**kwargs)
        return True

    def get_memory_context(self, topic: str = None) -> str:
        """获取记忆上下文"""
        return self.memory.build_context_for_ai(topic)

    def search_memory(self, keyword: str) -> List[Dict]:
        """搜索记忆"""
        return self.memory.recall(keyword)

    def add_memory_scene(
        self,
        summary: str,
        scene_type: str,
        details: str = "",
        tags: List[str] = None
    ) -> str:
        """添加场景记忆"""
        return self.memory.add_scene(
            summary=summary,
            scene_type=scene_type,
            details=details,
            tags=tags
        )

    # ========== 学习状态 ==========

    def get_study_status(self) -> Dict[str, Any]:
        """获取学习状态"""
        return {
            "is_studying": self.study.is_studying(),
            "today_hours": self.study.get_today_hours(),
            "streak_days": self.study.get_streak_days(),
            "week_hours": self.study.get_week_hours(),
            "continuous_minutes": self.study.get_continuous_study_minutes()
        }

    def start_study(self, subject: str = "学习") -> bool:
        """开始学习"""
        success = self.study.start_session(subject)
        if success:
            self.set_emotion("study")
            self.update_emotion_by_action("study_start")
        return success

    def stop_study(self, subject: str = "学习") -> float:
        """结束学习"""
        duration = self.study.end_session(subject)
        if duration >= 25:
            self.set_emotion("excited")
            # 触发成就关心
            self.trigger_achievement("streak", f"task_done")
        else:
            self.set_emotion("happy")
        return duration

    # ========== 日记 API ==========

    def get_today_diary(self) -> Optional[Dict]:
        """获取今日日记"""
        entry = self.diary.get_today()
        return entry.to_dict() if entry else None

    def add_diary_entry(
        self,
        emotion_level: int,
        study_feeling: str = "",
        biggest_event: str = "",
        words_to_buddy: str = ""
    ) -> Dict:
        """添加日记"""
        stats = self.study.get_stats()
        entry = self.diary.add_entry(
            emotion_level=emotion_level,
            study_feeling=study_feeling,
            study_hours=stats.get("today_hours", 0),
            biggest_event=biggest_event,
            words_to_buddy=words_to_buddy
        )

        # 如果情绪低，触发关心
        if emotion_level <= 2:
            caring_event = self.trigger_emotion_support(
                DiaryEntry.EMOTION_LABELS.get(emotion_level, ""),
                emotion_level
            )
            if caring_event:
                return {
                    "entry": entry.to_dict(),
                    "buddy_caring": caring_event.message
                }

        return {"entry": entry.to_dict()}

    def get_emotion_curve(self, days: int = 7) -> Dict:
        """获取情绪曲线"""
        return self.diary.get_emotion_curve(days)

    # ========== 状态获取 ==========

    def get_full_status(self) -> Dict[str, Any]:
        """获取完整状态（用于首页展示）"""
        self._check_time_emotion()

        profile = self.get_profile()
        study_status = self.get_study_status()
        today_diary = self.get_today_diary()
        emotion_curve = self.get_emotion_curve(7)

        return {
            "buddy": {
                "name": self.profile.get_buddy_info().get("name", "小豆"),
                "emotion": self.get_emotion(),
                "emoji": self.get_emoji(),
                "emotion_desc": self.get_emotion_desc(),
            },
            "profile": {
                "target_school": profile.get("user", {}).get("target_school", ""),
                "target_major": profile.get("user", {}).get("target_major", ""),
                "days_remaining": profile.get("days_remaining", -1),
                "current_phase": profile.get("current_phase", "未设置"),
                "is_setup": self.profile.is_setup_complete(),
            },
            "study": {
                **study_status,
                "goal_progress": self.study.get_daily_goal_progress(
                    (profile.get("user", {}).get("daily_goal_hours", 8) or 8) * 60
                )
            },
            "diary": {
                "has_today": today_diary is not None,
                "today_emotion": today_diary.get("emotion_label", "") if today_diary else None,
            },
            "emotion_curve": emotion_curve,
            "caring_events": [
                {
                    "type": e.type,
                    "message": e.message,
                    "priority": e.priority
                }
                for e in self.check_caring_events()[:2]
            ],
        }

    def reset(self):
        """重置搭子状态"""
        self._current_emotion = "idle"
        self._emotion_history = []
        self._last_active = datetime.now()
        self.set_emotion("idle")

    def switch_role(self, role_key: str) -> bool:
        """
        切换搭子角色

        参数:
            role_key: 角色标识符，如 'xiaodou', 'aran', 'senior' 等

        返回:
            bool: 切换是否成功
        """
        from src.buddy.buddy_roles import BUDDY_ROLES

        if role_key not in BUDDY_ROLES:
            return False

        role = BUDDY_ROLES[role_key]
        # 更新 profile 中的搭子配置
        self.profile.update_buddy(
            name=role['name'],
            emoji=role['emoji'],
            trait=role['personality'],
            role_key=role_key,
        )

        # 更新当前情绪
        self.set_emotion("happy")

        return True


    # ========== 兼容属性 ==========

    @property
    def task_manager(self):
        """兼容旧版 task_manager 引用"""
        return self.study

    @property
    def ai_memory(self):
        """兼容旧版 ai_memory"""
        from src.modules.ai_memory import get_ai_memory
        return get_ai_memory()

    # ========== 兼容方法 ==========

    def get_study_stats(self) -> Dict[str, Any]:
        """旧版统计接口"""
        return self.study.get_stats()

    def check_time_based_emotion(self):
        """检查时间相关情绪（兼容旧版）"""
        self._check_time_emotion()

    def get_emotion_description(self) -> str:
        """获取情绪描述（兼容旧版）"""
        return self.get_emotion_desc()

    def update_by_supervisor(self, status: Dict):
        """根据监督器状态更新情绪（兼容旧版）"""
        pass

    def update_by_focus(self, score, state):
        """根据专注度更新情绪（兼容旧版）"""
        pass

    def get_focus_stats(self) -> Dict[str, Any]:
        """获取专注度统计（兼容旧版）"""
        return {}

    def log_study_session(self, duration: float):
        """记录学习时段（兼容旧版）"""
        pass

    def get_calendar_stats(self) -> Dict[str, Any]:
        """获取日历统计（兼容旧版）"""
        return self.study.get_stats()

    def on_pomodoro_complete(self):
        """番茄钟完成回调"""
        self.set_emotion("excited")

    def on_task_complete(self, task_title: str = ""):
        """任务完成回调"""
        self.set_emotion("happy")

    def on_goal_reached(self):
        """目标达成回调"""
        self.set_emotion("proud")


# 全局单例
_buddy_instance: Optional[Buddy] = None


def get_buddy() -> Buddy:
    """获取 Buddy 实例（单例模式）"""
    global _buddy_instance
    if _buddy_instance is None:
        _buddy_instance = Buddy()
    return _buddy_instance


# 兼容旧接口
class BuddyCompat(Buddy):
    """兼容旧版 Buddy 接口（已废弃，请使用 Buddy 或 get_buddy）"""

    def __init__(self, supervisor=None):
        super().__init__()
        self._supervisor = supervisor
