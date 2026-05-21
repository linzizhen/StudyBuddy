"""
StudyPal 主动关心引擎
管理搭子的主动关心行为

功能：
- 关心触发规则检测
- 主动消息生成
- 关心冷却管理
- 行为感知（替代摄像头监督）

作者：StudyPal
日期：2026-04-27
"""

import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from src.ai.prompt_templates import get_prompt_templates


class CaringEvent:
    """
    关心事件类
    """

    def __init__(
        self,
        event_type: str,
        message: str,
        priority: str = "normal",
        context: Dict[str, Any] = None
    ):
        self.type = event_type
        self.message = message
        self.priority = priority  # high, normal, low
        self.context = context or {}
        self.created_at = datetime.now()


class CaringEngine:
    """
    主动关心引擎

    不只是被动回答用户问题，而是主动发起关心和互动。
    通过行为感知（基于打卡数据）判断用户状态，替代摄像头监督。
    """

    # 关心类型定义
    CARING_TYPES = {
        "morning_greeting": {"cooldown_hours": 24, "priority": "normal"},
        "study_reminder": {"cooldown_hours": 2, "priority": "normal"},
        "emotion_check": {"cooldown_hours": 24, "priority": "low"},
        "achievement_celebration": {"cooldown_hours": 0, "priority": "high"},
        "tough_time_support": {"cooldown_hours": 6, "priority": "high"},
        "sleep_reminder": {"cooldown_hours": 12, "priority": "normal"},
        "break_reminder": {"cooldown_hours": 2, "priority": "low"},
        "progress_check": {"cooldown_hours": 24, "priority": "low"},
        "no_diary_reminder": {"cooldown_hours": 24, "priority": "low"},
        # 第三轮新增关心类型
        "midnight_encouragement": {"cooldown_hours": 12, "priority": "normal"},
        "streak_celebration": {"cooldown_hours": 0, "priority": "high"},
        "emotion_support_deep": {"cooldown_hours": 24, "priority": "high"},
        "weekly_reflection": {"cooldown_hours": 168, "priority": "normal"},
        "phase_encouragement": {"cooldown_hours": 0, "priority": "high"},
    }

    # 关心的消息模板
    MESSAGE_TEMPLATES = {
        "morning_greeting": [
            "早！今天感觉怎么样？要开始学习了吗？",
            "早上好~今天有什么学习计划？",
            "新的一天开始了，今天也要加油哦！",
            "早安！准备好开始今天的战斗了吗？",
        ],
        "study_reminder": [
            "今天还没开始学习呢，我等你很久了...",
            "要不要开始学习？我陪你~",
            "感觉你今天还没来打卡呢？",
            "学习这件事，开始了就成功了一半哦~",
        ],
        "emotion_check": [
            "今天心情怎么样？要不要聊聊？",
            "感觉你今天状态如何？",
            "有什么想说的吗？我在听。",
        ],
        "sleep_reminder": [
            "已经23点多了，早点休息吧，明天还要早起呢。",
            "夜深了，别熬太晚，身体最重要。",
            "你今天已经学习很久了，早点睡吧~",
        ],
        "break_reminder": [
            "学了好久了吧，站起来活动活动~",
            "眼睛该休息一下了，离开屏幕看看远方吧。",
            "辛苦了，要不要休息一会儿？",
        ],
        "no_diary_reminder": [
            "今天还没记录心情呢~ 今天怎么样？",
            "今晚要不要记录一下今天的心情？",
            "今天是充实的一天吗？来写写日记吧。",
        ],
        "tough_time_support": [
            "我在这里呢。不管发生什么，你不是一个人。",
            "没关系的，每个人都有难熬的时候。",
            "不管结果怎样，你努力的样子就已经很棒了。",
        ],
        "achievement_celebration": {
            "streak_3": "哇！连续学习3天了！你真的很认真！",
            "streak_7": "太厉害了！连续7天！你是我见过最坚持的人之一！",
            "streak_30": "一个月！你是怎么做到的？！我真的佩服你！",
            "task_done": "任务完成！你看，一步一步来就能做到的。",
            "goal_reached": "今天的学习目标完成啦！给自己点个赞~",
            "first_study": "第一次开始学习！你已经迈出第一步了！",
        },
        "late_night": [
            "都这么晚了还在学习，你真的很努力，但也要注意身体哦。",
            "凌晨了还在拼搏，这种劲头我很欣赏，但别太晚睡~",
        ],
        "overwork": [
            "今天学习时间已经很长了，适当休息一下也很重要哦。",
            "你今天真的很拼！但别把自己逼太紧，适当休息效率更高~",
        ],
        "progress_check": [
            "这一路走来，你比刚开始时进步了很多呢。",
            "坚持这么久，真的很不容易，为你骄傲。",
            "回头看看，你已经走了很远了，继续加油！",
        ],
        # 第三轮新增关心消息模板
        "midnight_encouragement": [
            "凌晨了还在努力，这种精神让我佩服，但也要注意身体啊。",
            "夜深了，你还在坚持，我陪你。",
            "这么晚还不休息，一定是有重要的事吧？加油！",
        ],
        "streak_celebration": {
            "7": "连续学习7天！你真的很棒，这种坚持让人感动！",
            "14": "两周了！你是我见过最坚持的人，继续加油！",
            "30": "一个月！这种自律太厉害了，为你骄傲！",
            "100": "一百天！你已经走过了最艰难的路，继续冲刺！",
        },
        "weekly_reflection": [
            "这周辛苦了，周末好好休息一下吧~",
            "一周结束啦，回顾一下这周的收获吧。",
            "周日了，要不要和小豆聊聊这周的感受？",
        ],
        "phase_encouragement": {
            "basics": "基础阶段开始啦！万事开头难，迈出第一步就是成功。",
            "strengthen": "强化阶段来了！查漏补缺，攻克难点的时候到了。",
            "sprint": "冲刺阶段！最后关头，坚持就是胜利！",
        },
    }

    def __init__(self):
        self.cooldowns: Dict[str, datetime] = {}
        self.pending_events: List[CaringEvent] = []
        self._study_tracker = None
        self._diary_tracker = None
        self._memory = None
        self._last_phase: Optional[str] = None  # 上一阶段

    def set_trackers(self, study_tracker=None, diary_tracker=None, memory=None):
        """设置数据追踪器"""
        self._study_tracker = study_tracker
        self._diary_tracker = diary_tracker
        self._memory = memory

    def _check_cooldown(self, caring_type: str) -> bool:
        """
        检查关心是否在冷却中

        返回 True 表示可以触发，False 表示在冷却中
        """
        if caring_type not in self.CARING_TYPES:
            return True

        if caring_type not in self.cooldowns:
            return True

        cooldown_info = self.CARING_TYPES[caring_type]
        cooldown_hours = cooldown_info.get("cooldown_hours", 0)

        if cooldown_hours == 0:
            return True

        last_time = self.cooldowns[caring_type]
        elapsed = (datetime.now() - last_time).total_seconds() / 3600

        return elapsed >= cooldown_hours

    def _set_cooldown(self, caring_type: str):
        """设置关心冷却"""
        self.cooldowns[caring_type] = datetime.now()

    def _get_random_message(self, caring_type: str, sub_key: str = None) -> str:
        """获取随机关心的消息"""
        if caring_type == "achievement_celebration" and sub_key:
            templates = self.MESSAGE_TEMPLATES.get("achievement_celebration", {})
            return templates.get(sub_key, "恭喜你！太棒了！")

        templates = self.MESSAGE_TEMPLATES.get(caring_type, [])
        if templates:
            return random.choice(templates)
        return "今天怎么样？"

    def _get_caring_priority(self, caring_type: str) -> str:
        """获取关心优先级"""
        return self.CARING_TYPES.get(caring_type, {}).get("priority", "normal")

    def check_all(self) -> List[CaringEvent]:
        """
        检查所有关心规则，触发符合条件的

        返回待发送的关心事件列表
        """
        events = []
        now = datetime.now()

        # 1. 早安问候（7-9点）
        if 7 <= now.hour <= 9:
            if self._check_cooldown("morning_greeting"):
                if self._should_morning_greeting():
                    message = self._generate_morning_greeting()
                    if message:
                        events.append(CaringEvent(
                            "morning_greeting",
                            message,
                            self._get_caring_priority("morning_greeting"),
                            {"time": now.strftime("%H:%M")}
                        ))
                        self._set_cooldown("morning_greeting")

        # 2. 学习提醒（检测长时间未学习）
        if self._check_cooldown("study_reminder"):
            event = self._check_study_reminder()
            if event:
                events.append(event)
                self._set_cooldown("study_reminder")

        # 3. 情绪打卡提醒（晚9-10点）
        if 21 <= now.hour <= 22:
            if self._check_cooldown("emotion_check"):
                if self._should_emotion_check():
                    message = self._get_random_message("emotion_check")
                    events.append(CaringEvent(
                        "emotion_check",
                        message,
                        self._get_caring_priority("emotion_check")
                    ))
                    self._set_cooldown("emotion_check")

        # 4. 日记记录提醒（晚9点后）
        if now.hour >= 21:
            if self._check_cooldown("no_diary_reminder"):
                if self._should_diary_reminder():
                    message = self._get_random_message("no_diary_reminder")
                    events.append(CaringEvent(
                        "no_diary_reminder",
                        message,
                        self._get_caring_priority("no_diary_reminder")
                    ))
                    self._set_cooldown("no_diary_reminder")

        # 5. 睡眠提醒（23点后）
        if now.hour >= 23:
            if self._check_cooldown("sleep_reminder"):
                event = self._check_sleep_reminder()
                if event:
                    events.append(event)
                    self._set_cooldown("sleep_reminder")

        # 6. 休息提醒（连续学习4小时）
        if self._check_cooldown("break_reminder"):
            event = self._check_break_reminder()
            if event:
                events.append(event)
                self._set_cooldown("break_reminder")

        # 7. 过度学习提醒（一天学习超过12小时）
        if self._check_cooldown("overwork"):
            event = self._check_overwork()
            if event:
                events.append(event)
                self._set_cooldown("overwork")

        # 8. 深夜鼓励（23:00-01:00）
        if self._check_cooldown("midnight_encouragement"):
            event = self._check_midnight()
            if event:
                events.append(event)
                self._set_cooldown("midnight_encouragement")

        # 9. 周复盘（周日晚上 20:00-23:00）
        if self._check_cooldown("weekly_reflection"):
            event = self._check_weekly_reflection()
            if event:
                events.append(event)
                self._set_cooldown("weekly_reflection")

        # 10. 阶段鼓励（检测阶段变化）
        if self._check_cooldown("phase_encouragement"):
            event = self._check_phase_change()
            if event:
                events.append(event)
                self._set_cooldown("phase_encouragement")

        # 按优先级排序
        priority_order = {"high": 0, "normal": 1, "low": 2}
        events.sort(key=lambda e: priority_order.get(e.priority, 1))

        return events

    def _should_morning_greeting(self) -> bool:
        """判断是否应该发送早安问候"""
        if not self._study_tracker:
            return True
        yesterday_hours = self._study_tracker.get_yesterday_hours()
        return yesterday_hours > 0

    def _generate_morning_greeting(self) -> str:
        """生成个性化的早安问候"""
        if not self._study_tracker:
            return self._get_random_message("morning_greeting")

        yesterday_hours = self._study_tracker.get_yesterday_hours()
        streak_days = self._study_tracker.get_streak_days()
        yesterday_tasks = self._study_tracker.get_yesterday_tasks()

        templates = get_prompt_templates()
        prompt = templates.get_morning_greeting_prompt(
            yesterday_hours=yesterday_hours,
            yesterday_tasks=yesterday_tasks,
            streak_days=streak_days,
            days_remaining=0
        )

        return self._get_random_message("morning_greeting")

    def _check_study_reminder(self) -> Optional[CaringEvent]:
        """检查是否需要提醒学习"""
        if not self._study_tracker:
            return None

        hours_since_study = self._study_tracker.get_hours_since_last_session()
        if hours_since_study is None:
            return None

        if hours_since_study >= 4:
            message = self._get_random_message("study_reminder")
            return CaringEvent(
                "study_reminder",
                message,
                self._get_caring_priority("study_reminder"),
                {"hours": hours_since_study}
            )
        return None

    def _should_emotion_check(self) -> bool:
        """判断是否应该进行情绪确认"""
        if not self._diary_tracker:
            return True
        return not self._diary_tracker.has_today()

    def _check_sleep_reminder(self) -> Optional[CaringEvent]:
        """检查是否需要催睡觉"""
        if not self._study_tracker:
            message = self._get_random_message("sleep_reminder")
            return CaringEvent(
                "sleep_reminder",
                message,
                self._get_caring_priority("sleep_reminder")
            )

        today_hours = self._study_tracker.get_today_hours()
        today_minutes = self._study_tracker.get_last_active_minutes()

        if today_hours >= 10:
            message = f"你今天已经学习了 {today_hours:.1f} 小时了！真的辛苦了，早点休息吧。"
        elif today_minutes >= 30:
            message = "都这么晚了，还在坚持吗？身体最重要，早点睡吧~"
        else:
            message = self._get_random_message("sleep_reminder")

        return CaringEvent(
            "sleep_reminder",
            message,
            self._get_caring_priority("sleep_reminder")
        )

    def _check_break_reminder(self) -> Optional[CaringEvent]:
        """检查是否需要提醒休息"""
        if not self._study_tracker:
            return None

        if self._study_tracker.is_studying():
            continuous_minutes = self._study_tracker.get_continuous_study_minutes()
            if continuous_minutes >= 120:
                message = self._get_random_message("break_reminder")
                return CaringEvent(
                    "break_reminder",
                    message,
                    self._get_caring_priority("break_reminder"),
                    {"minutes": continuous_minutes}
                )
        return None

    def _check_overwork(self) -> Optional[CaringEvent]:
        """检查是否过度学习"""
        if not self._study_tracker:
            return None

        today_hours = self._study_tracker.get_today_hours()
        if today_hours >= 14:
            message = self._get_random_message("overwork")
            return CaringEvent(
                "overwork",
                message,
                self._get_caring_priority("overwork"),
                {"hours": today_hours}
            )
        return None

    def _check_midnight(self) -> Optional[CaringEvent]:
        """检查是否需要深夜鼓励"""
        hour = datetime.now().hour
        if hour >= 23 or hour < 1:
            if self._study_tracker and self._study_tracker.is_studying():
                message = self._get_random_message("midnight_encouragement")
                return CaringEvent(
                    "midnight_encouragement",
                    message,
                    self._get_caring_priority("midnight_encouragement"),
                    {"hour": hour}
                )
        return None

    def _check_weekly_reflection(self) -> Optional[CaringEvent]:
        """检查是否需要周复盘提醒（周日晚上）"""
        now = datetime.now()
        if now.weekday() == 6 and 20 <= now.hour <= 23:
            message = self._get_random_message("weekly_reflection")
            return CaringEvent(
                "weekly_reflection",
                message,
                self._get_caring_priority("weekly_reflection"),
                {"weekday": "周日"}
            )
        return None

    def _check_phase_change(self) -> Optional[CaringEvent]:
        """检查阶段变化"""
        if not self._memory:
            return None

        phase_key = self._memory.get_preference("current_phase")
        if phase_key and phase_key != self._last_phase:
            message = self.MESSAGE_TEMPLATES.get("phase_encouragement", {}).get(phase_key)
            if message:
                self._last_phase = phase_key
                return CaringEvent(
                    "phase_encouragement",
                    message,
                    self._get_caring_priority("phase_encouragement"),
                    {"phase": phase_key}
                )
        return None

    def trigger_streak_celebration(self, streak_days: int) -> Optional[CaringEvent]:
        """触发连续学习里程碑庆祝"""
        milestone_key = None
        if streak_days == 7:
            milestone_key = "7"
        elif streak_days == 14:
            milestone_key = "14"
        elif streak_days == 30:
            milestone_key = "30"
        elif streak_days == 100:
            milestone_key = "100"

        if milestone_key:
            message = self.MESSAGE_TEMPLATES.get("streak_celebration", {}).get(milestone_key)
            if message:
                return CaringEvent(
                    "streak_celebration",
                    message,
                    "high",
                    {"streak_days": streak_days}
                )
        return None

    def _should_diary_reminder(self) -> bool:
        """判断是否应该提醒写日记"""
        if not self._diary_tracker:
            return True
        return not self._diary_tracker.has_today()

    def trigger_achievement(
        self,
        achievement_type: str,
        sub_key: str = None,
        context: Dict[str, Any] = None
    ) -> Optional[CaringEvent]:
        """
        触发成就庆祝关心

        当用户完成某个里程碑时调用
        """
        message = self._get_random_message("achievement_celebration", sub_key)
        if not message:
            return None

        return CaringEvent(
            "achievement_celebration",
            message,
            self._get_caring_priority("achievement_celebration"),
            context or {}
        )

    def trigger_emotion_support(
        self,
        emotion: str,
        emotion_level: int
    ) -> CaringEvent:
        """
        触发情绪支持关心

        当用户情绪低落时调用
        """
        templates = get_prompt_templates()
        prompt = templates.get_emotion_support_prompt(emotion, emotion_level)

        return CaringEvent(
            "tough_time_support",
            prompt,
            "high",
            {"emotion": emotion, "level": emotion_level}
        )

    def get_pending_events(self) -> List[CaringEvent]:
        """获取待处理的关心事件"""
        return self.pending_events

    def clear_pending(self):
        """清空待处理事件"""
        self.pending_events = []


# 全局单例
_caring_engine_instance: Optional[CaringEngine] = None


def get_caring_engine() -> CaringEngine:
    """获取主动关心引擎实例"""
    global _caring_engine_instance
    if _caring_engine_instance is None:
        _caring_engine_instance = CaringEngine()
    return _caring_engine_instance
