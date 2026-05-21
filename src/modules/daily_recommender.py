"""
StudyPal 每日任务推荐模块
基于学习计划和用户状态推荐每日任务
"""

import random
from datetime import datetime
from typing import Dict, Any, List, Optional


class DailyTaskRecommender:
    """
    每日任务推荐器

    根据学习计划、用户状态、当前阶段推荐每日任务
    """

    # 每日推荐模板
    RECOMMENDATION_TEMPLATES = {
        "morning": [
            "早起复习昨天学的内容",
            "背英语单词 30 分钟",
            "做数学基础题 5 道",
        ],
        "afternoon": [
            "看专业课视频课程",
            "整理上午的学习笔记",
            "做英语阅读理解 2 篇",
        ],
        "evening": [
            "复习今天学的新内容",
            "整理错题本",
            "预习明天的内容",
            "做一套小测试",
        ],
        "flexible": [
            "查漏补缺薄弱科目",
            "复习之前学过的章节",
            "整理知识点框架",
        ]
    }

    # 各科目学习建议
    SUBJECT_SUGGESTIONS = {
        "数学": [
            "复习极限章节",
            "练习微分方程",
            "整理线代公式",
            "做概率论习题",
            "回顾错题集",
        ],
        "英语": [
            "背单词 50 个",
            "做阅读理解 2 篇",
            "练习作文模板",
            "听力训练 30 分钟",
            "翻译练习",
        ],
        "政治": [
            "看政治视频课程",
            "整理政治框架",
            "做选择题练习",
            "背诵重要知识点",
        ],
        "专业课": [
            "复习专业课重点章节",
            "整理专业课笔记",
            "做专业课真题",
            "梳理知识脉络",
        ],
    }

    def __init__(self):
        self._study_tracker = None
        self._plan_generator = None
        self._task_manager = None

    def set_modules(self, study_tracker=None, plan_generator=None, task_manager=None):
        """设置相关模块"""
        self._study_tracker = study_tracker
        self._plan_generator = plan_generator
        self._task_manager = task_manager

    def get_daily_recommendations(self) -> Dict[str, Any]:
        """
        获取每日任务推荐

        返回包含推荐任务和建议的字典
        """
        recommendations = []
        suggestions = []

        # 获取当前时间
        hour = datetime.now().hour

        # 根据时间推荐
        if 6 <= hour < 12:
            time_slot = "morning"
            time_label = "上午"
        elif 12 <= hour < 18:
            time_slot = "afternoon"
            time_label = "下午"
        else:
            time_slot = "evening"
            time_label = "晚上"

        # 获取今日已完成的学科
        completed_subjects = self._get_completed_subjects() if self._study_tracker else []

        # 获取未完成的任务
        pending_tasks = self._get_pending_tasks() if self._task_manager else []

        # 基于学习计划推荐
        plan_tasks = self._get_plan_tasks() if self._plan_generator else []

        # 生成推荐
        recommendations.extend(self._generate_time_based_recommendations(time_slot, completed_subjects))
        recommendations.extend(self._generate_subject_recommendations(completed_subjects))
        recommendations.extend(self._generate_from_pending_tasks(pending_tasks))
        recommendations.extend(self._generate_from_plan(plan_tasks))

        # 添加灵活任务
        recommendations.extend(self._generate_flexible_tasks())

        # 去重
        seen = set()
        unique_recommendations = []
        for r in recommendations:
            if r["task"] not in seen:
                seen.add(r["task"])
                unique_recommendations.append(r)

        # 生成建议
        suggestions = self._generate_suggestions(unique_recommendations, completed_subjects, hour)

        return {
            "time_slot": time_slot,
            "time_label": time_label,
            "recommendations": unique_recommendations[:5],
            "suggestions": suggestions,
            "completed_subjects": completed_subjects,
            "pending_tasks_count": len(pending_tasks),
            "date": datetime.now().strftime("%Y-%m-%d")
        }

    def _get_completed_subjects(self) -> List[str]:
        """获取今日已学习的科目"""
        if not self._study_tracker:
            return []
        stats = self._study_tracker.get_today_subjects()
        return [s for s, mins in stats.items() if mins > 0]

    def _get_pending_tasks(self) -> List[Dict]:
        """获取待完成的任务"""
        if not self._task_manager:
            return []
        tasks = self._task_manager.get_tasks(status="pending")
        return [t.to_dict() if hasattr(t, 'to_dict') else t for t in tasks]

    def _get_plan_tasks(self) -> List[str]:
        """获取学习计划中的任务"""
        if not self._plan_generator:
            return []
        plans = self._plan_generator.get_active_plans()
        tasks = []
        for plan in plans:
            if hasattr(plan, 'tasks') and plan.tasks:
                for task in plan.tasks:
                    if isinstance(task, dict):
                        tasks.append(task.get('task', ''))
                    else:
                        tasks.append(str(task))
        return tasks

    def _generate_time_based_recommendations(
        self,
        time_slot: str,
        completed_subjects: List[str]
    ) -> List[Dict[str, Any]]:
        """基于时间段生成推荐"""
        templates = self.RECOMMENDATION_TEMPLATES.get(time_slot, [])
        return [
            {
                "task": task,
                "reason": f"{time_slot} 推荐",
                "priority": "normal",
                "category": "routine"
            }
            for task in templates
        ]

    def _generate_subject_recommendations(
        self,
        completed_subjects: List[str]
    ) -> List[Dict[str, Any]]:
        """基于科目生成推荐"""
        recommendations = []
        all_subjects = list(self.SUBJECT_SUGGESTIONS.keys())

        # 选择未学习的科目
        for subject in all_subjects:
            if subject not in completed_subjects:
                suggestions = self.SUBJECT_SUGGESTIONS[subject]
                task = random.choice(suggestions)
                recommendations.append({
                    "task": f"{subject}：{task}",
                    "reason": f"今日还未学习 {subject}",
                    "priority": "high",
                    "category": "subject",
                    "subject": subject
                })

        return recommendations

    def _generate_from_pending_tasks(
        self,
        pending_tasks: List[Dict]
    ) -> List[Dict[str, Any]]:
        """从待完成任务生成推荐"""
        recommendations = []
        for task in pending_tasks[:3]:
            title = task.get('title', '')
            if title:
                recommendations.append({
                    "task": title,
                    "reason": "待完成任务",
                    "priority": "high",
                    "category": "task",
                    "task_id": task.get('id')
                })
        return recommendations

    def _generate_from_plan(self, plan_tasks: List[str]) -> List[Dict[str, Any]]:
        """从学习计划生成推荐"""
        recommendations = []
        for task in plan_tasks[:2]:
            if task:
                recommendations.append({
                    "task": task,
                    "reason": "学习计划任务",
                    "priority": "normal",
                    "category": "plan"
                })
        return recommendations

    def _generate_flexible_tasks(self) -> List[Dict[str, Any]]:
        """生成灵活任务"""
        templates = self.RECOMMENDATION_TEMPLATES.get("flexible", [])
        task = random.choice(templates) if templates else "查漏补缺"
        return [{
            "task": task,
            "reason": "灵活任务",
            "priority": "low",
            "category": "flexible"
        }]

    def _generate_suggestions(
        self,
        recommendations: List[Dict],
        completed_subjects: List[str],
        hour: int
    ) -> List[str]:
        """生成建议"""
        suggestions = []

        # 根据时间
        if hour < 9:
            suggestions.append("早点开始学习，一天之计在于晨！")
        elif hour < 12:
            suggestions.append("上午精力充沛，适合做有挑战的任务。")
        elif hour < 14:
            suggestions.append("午休很重要，休息好才能效率高。")
        elif hour < 18:
            suggestions.append("下午继续保持专注！")
        else:
            suggestions.append("晚上了，注意不要熬太晚哦。")

        # 根据完成情况
        if not completed_subjects:
            suggestions.append("今天还没开始学习呢，赶紧动起来吧！")
        elif len(completed_subjects) >= 3:
            suggestions.append("今天学习了很多，很棒！但也要注意休息。")

        return suggestions


# 全局单例
_recommender_instance: Optional[DailyTaskRecommender] = None


def get_daily_recommender() -> DailyTaskRecommender:
    """获取每日任务推荐器实例"""
    global _recommender_instance
    if _recommender_instance is None:
        _recommender_instance = DailyTaskRecommender()
    return _recommender_instance
