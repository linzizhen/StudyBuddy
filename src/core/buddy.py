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
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from src.buddy.buddy_profile import BuddyProfile, get_buddy_profile
from src.buddy.buddy_memory import BuddyMemory, get_buddy_memory
from src.buddy.caring_engine import CaringEngine, CaringEvent, get_caring_engine
from src.study.study_tracker import StudyTracker, get_study_tracker
from src.diary.diary import Diary, get_diary, EmotionTracker, get_emotion_tracker, DiaryEntry
from src.ai.prompt_templates import get_prompt_templates


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

    def chat(self, message: str, conversation_id: str = None) -> Dict[str, Any]:
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
        reply = self._generate_reply(message, emotion_analysis, conversation_id)

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
            "suggestions": self._generate_suggestions(message, emotion_analysis)
        }

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

        # 检测意图
        intent = "chat"
        if any(kw in message_lower for kw in ["怎么", "如何", "什么"]):
            intent = "question"
        elif any(kw in message_lower for kw in ["计划", "安排", "复习"]):
            intent = "plan"
        elif any(kw in message_lower for kw in ["学不进去", "拖延"]):
            intent = "struggle"

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
            "intent": intent
        }

    def _generate_reply(
        self,
        message: str,
        emotion_analysis: Dict,
        conversation_id: str = None
    ) -> str:
        """
        生成搭子回复

        这里调用 AI 模型，结合记忆和上下文生成回复
        """
        # 从旧版 AI 模块获取对话能力
        from src.ai.ai_helper import get_ai_instance
        ai = get_ai_instance()

        # 构建系统提示词
        system_prompt = self._build_system_prompt()

        # 构建用户消息
        user_message = self._build_user_message(message, emotion_analysis)

        try:
            # 调用 AI
            result = ai.ask(
                question=user_message,
                conversation_id=conversation_id,
                system_prompt=system_prompt
            )
            return result.get("answer", "我在呢，有什么事？")
        except Exception as e:
            # 如果 AI 调用失败，使用模板回复
            return self._fallback_reply(message, emotion_analysis)

    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
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
            memory_context=memory_context,
            current_phase=current_phase
        )

        # 获取角色风格规则（这是搭子差异化的核心！）
        from src.buddy.buddy_roles import BuddyRoles
        role_style_rules = BuddyRoles.get_role_style_rules(role_key)

        # 拼接基础提示词 + 角色风格规则
        if role_style_rules:
            final_prompt = base_prompt + "\n\n" + role_style_rules
        else:
            final_prompt = base_prompt

        # 调试日志（生产环境可在日志级别控制）
        print(f"[搭子对话] 当前搭子: {role_key} ({buddy_info.get('name', '未知')})")
        print(f"[搭子对话] SystemPrompt长度: {len(final_prompt)} 字")
        print(f"[搭子对话] SystemPrompt前200字: {final_prompt[:200]}")

        return final_prompt

    def _build_user_message(
        self,
        message: str,
        emotion_analysis: Dict
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
