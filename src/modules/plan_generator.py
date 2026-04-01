"""
StudyBuddy AI 学习计划生成模块
根据考试日期、科目和可用时间，生成个性化学习计划
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StudyPlan:
    """单个学习计划"""
    
    def __init__(self, subject: str, exam_date: str, daily_hours: float = 2.0):
        """
        初始化学习计划
        
        参数:
            subject: 科目名称
            exam_date: 考试日期 (YYYY-MM-DD 格式)
            daily_hours: 每日建议学习时长（小时）
        """
        self.subject = subject
        self.exam_date = datetime.strptime(exam_date, "%Y-%m-%d") if isinstance(exam_date, str) else exam_date
        self.daily_hours = daily_hours
        self.created_at = datetime.now()
        self.tasks = []  # 生成的子任务列表
        self.total_hours = 0  # 总学习时长
        self.completed = False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": id(self),
            "subject": self.subject,
            "exam_date": self.exam_date.strftime("%Y-%m-%d") if self.exam_date else None,
            "daily_hours": self.daily_hours,
            "total_hours": self.total_hours,
            "tasks": self.tasks,
            "completed": self.completed,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M")
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StudyPlan':
        """从字典创建"""
        plan = cls(
            subject=data["subject"],
            exam_date=data["exam_date"],
            daily_hours=data.get("daily_hours", 2.0)
        )
        plan.id = data.get("id", id(plan))
        plan.tasks = data.get("tasks", [])
        plan.total_hours = data.get("total_hours", 0)
        plan.completed = data.get("completed", False)
        if "created_at" in data:
            plan.created_at = datetime.strptime(data["created_at"], "%Y-%m-%d %H:%M")
        return plan
    
    def add_task(self, task: Dict[str, Any]):
        """添加子任务"""
        self.tasks.append(task)
    
    def mark_complete(self):
        """标记为完成"""
        self.completed = True
    
    def get_days_remaining(self) -> int:
        """获取距离考试的天数"""
        if not self.exam_date:
            return 0
        delta = self.exam_date - datetime.now()
        return max(0, delta.days)
    
    def __str__(self) -> str:
        """字符串表示"""
        days = self.get_days_remaining()
        status = "✓" if self.completed else "○"
        return f"[{status}] {self.subject} - 考试还有 {days} 天"


class PlanGenerator:
    """学习计划生成器"""
    
    def __init__(self, ai_helper=None):
        """
        初始化计划生成器
        
        参数:
            ai_helper: AI 助手实例（可选）
        """
        self.ai_helper = ai_helper
        self.plans: List[StudyPlan] = []
        self.data_file = "data/study_plans.json"
        self._load_plans()
    
    def _load_plans(self):
        """从文件加载计划"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.plans = [StudyPlan.from_dict(p) for p in data.get("plans", [])]
            except (json.JSONDecodeError, KeyError):
                self.plans = []
    
    def _save_plans(self):
        """保存计划到文件"""
        data = {
            "plans": [p.to_dict() for p in self.plans]
        }
        dir_path = os.path.dirname(self.data_file)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def generate_plan_ai(self, subject: str, exam_date: str, 
                         daily_hours: float = 2.0, 
                         difficulty: str = "medium",
                         current_level: str = "beginner") -> StudyPlan:
        """
        使用 AI 生成学习计划
        
        参数:
            subject: 科目名称
            exam_date: 考试日期
            daily_hours: 每日学习时长
            difficulty: 难度等级 (easy/medium/hard)
            current_level: 当前水平 (beginner/intermediate/advanced)
        
        返回:
            生成的学习计划
        """
        if not self.ai_helper:
            return self.generate_plan_basic(subject, exam_date, daily_hours)
        
        try:
            # 构建 AI 提示词
            days_remaining = (datetime.strptime(exam_date, "%Y-%m-%d") - datetime.now()).days
            if days_remaining < 0:
                days_remaining = 0
            
            prompt = f"""请为我的考试生成一个详细的学习计划。

考试信息：
- 科目：{subject}
- 考试日期：{exam_date}
- 距离考试：{days_remaining} 天
- 每日可用时间：{daily_hours} 小时
- 当前水平：{current_level}
- 难度等级：{difficulty}

请按照以下格式返回 JSON 格式的学习计划：
{{
    "plan_overview": "计划概述，简短描述",
    "phases": [
        {{
            "phase_name": "阶段名称",
            "duration_days": 天数，
            "focus": "这个阶段的重点",
            "daily_tasks": ["任务 1", "任务 2", "任务 3"]
        }}
    ],
    "tips": ["学习建议 1", "学习建议 2", "学习建议 3"],
    "estimated_total_hours": 总学习时长
}}

请确保计划合理可行，任务具体可执行。"""
            
            # 调用 AI
            answer = self.ai_helper.ask_ai_sync(prompt)
            
            # 解析 AI 回答（尝试提取 JSON）
            import re
            json_match = re.search(r'\{[\s\S]*\}', answer)
            if json_match:
                plan_data = json.loads(json_match.group())
            else:
                # 如果解析失败，使用基础生成
                return self.generate_plan_basic(subject, exam_date, daily_hours)
            
            # 创建学习计划
            plan = StudyPlan(subject, exam_date, daily_hours)
            plan.total_hours = plan_data.get("estimated_total_hours", daily_hours * days_remaining)
            
            # 添加阶段任务
            for phase in plan_data.get("phases", []):
                phase_task = {
                    "phase": phase.get("phase_name", "学习阶段"),
                    "duration": phase.get("duration_days", 1),
                    "focus": phase.get("focus", ""),
                    "tasks": phase.get("daily_tasks", [])
                }
                plan.add_task(phase_task)
            
            # 添加学习建议
            plan.tips = plan_data.get("tips", [])
            plan.plan_overview = plan_data.get("plan_overview", "")
            
            self.plans.append(plan)
            self._save_plans()
            
            logger.info(f"✅ AI 生成学习计划：{subject}")
            return plan
            
        except Exception as e:
            logger.error(f"❌ AI 生成计划失败：{e}")
            return self.generate_plan_basic(subject, exam_date, daily_hours)
    
    def generate_plan_basic(self, subject: str, exam_date: str, 
                           daily_hours: float = 2.0) -> StudyPlan:
        """
        基础学习计划生成（不使用 AI）
        
        参数:
            subject: 科目名称
            exam_date: 考试日期
            daily_hours: 每日学习时长
        
        返回:
            生成的学习计划
        """
        exam_dt = datetime.strptime(exam_date, "%Y-%m-%d") if isinstance(exam_date, str) else exam_date
        days_remaining = (exam_dt - datetime.now()).days
        if days_remaining < 0:
            days_remaining = 0
        
        plan = StudyPlan(subject, exam_date, daily_hours)
        
        # 根据剩余天数生成阶段
        if days_remaining <= 0:
            plan.tasks = [{
                "phase": "紧急复习",
                "duration": 1,
                "focus": "重点复习核心内容",
                "tasks": [
                    f"复习{subject}核心知识点",
                    "做历年真题",
                    "整理错题集"
                ]
            }]
        elif days_remaining <= 3:
            plan.tasks = [{
                "phase": "冲刺阶段",
                "duration": days_remaining,
                "focus": "重点突破",
                "tasks": [
                    f"每天复习{subject}重点章节",
                    "做 2-3 套模拟题",
                    "整理易错点"
                ]
            }]
        elif days_remaining <= 7:
            plan.tasks = [
                {
                    "phase": "基础复习",
                    "duration": max(1, days_remaining // 2),
                    "focus": "系统复习基础知识",
                    "tasks": [
                        f"通读{subject}教材重点章节",
                        "整理知识框架",
                        "完成课后习题"
                    ]
                },
                {
                    "phase": "强化训练",
                    "duration": max(1, days_remaining - days_remaining // 2),
                    "focus": "做题巩固",
                    "tasks": [
                        "做历年真题",
                        "整理错题",
                        "查漏补缺"
                    ]
                }
            ]
        else:
            # 超过一周，分三个阶段
            phase1_days = days_remaining // 3
            phase2_days = days_remaining // 3
            phase3_days = days_remaining - phase1_days - phase2_days
            
            plan.tasks = [
                {
                    "phase": "基础阶段",
                    "duration": phase1_days,
                    "focus": "系统学习基础知识",
                    "tasks": [
                        f"学习{subject}第一章到第五章",
                        "完成对应习题",
                        "整理笔记"
                    ]
                },
                {
                    "phase": "强化阶段",
                    "duration": phase2_days,
                    "focus": "深入理解和练习",
                    "tasks": [
                        f"学习{subject}第六章到第十章",
                        "做章节练习题",
                        "总结重点难点"
                    ]
                },
                {
                    "phase": "冲刺阶段",
                    "duration": phase3_days,
                    "focus": "模拟测试和查漏补缺",
                    "tasks": [
                        "做历年真题",
                        "模拟考试",
                        "复习错题集"
                    ]
                }
            ]
        
        plan.total_hours = days_remaining * daily_hours
        self.plans.append(plan)
        self._save_plans()
        
        logger.info(f"✅ 生成学习计划：{subject} ({days_remaining}天)")
        return plan
    
    def get_plan(self, plan_id: int) -> Optional[StudyPlan]:
        """根据 ID 获取计划"""
        for plan in self.plans:
            if id(plan) == plan_id:
                return plan
        return None
    
    def delete_plan(self, plan_id: int) -> bool:
        """删除计划"""
        for i, plan in enumerate(self.plans):
            if id(plan) == plan_id:
                self.plans.pop(i)
                self._save_plans()
                return True
        return False
    
    def get_active_plans(self) -> List[StudyPlan]:
        """获取进行中的计划"""
        return [p for p in self.plans if not p.completed and p.get_days_remaining() > 0]
    
    def get_completed_plans(self) -> List[StudyPlan]:
        """获取已完成的计划"""
        return [p for p in self.plans if p.completed]
    
    def get_expiring_plans(self, days: int = 7) -> List[StudyPlan]:
        """获取即将考试的计划"""
        return [p for p in self.plans if p.get_days_remaining() <= days and not p.completed]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        total = len(self.plans)
        completed = len([p for p in self.plans if p.completed])
        active = len([p for p in self.plans if not p.completed])
        
        # 计算总学习时长
        total_hours = sum(p.total_hours for p in self.plans)
        
        return {
            "total_plans": total,
            "active_plans": active,
            "completed_plans": completed,
            "total_study_hours": total_hours
        }
    
    def clear_completed(self):
        """清除已完成的计划"""
        self.plans = [p for p in self.plans if not p.completed]
        self._save_plans()
    
    def __len__(self) -> int:
        """返回计划总数"""
        return len(self.plans)
    
    def __str__(self) -> str:
        """字符串表示"""
        stats = self.get_stats()
        return f"PlanGenerator: {stats['active_plans']} 个进行中，{stats['completed_plans']} 个已完成"


# 兼容旧版本的函数接口
_plan_generator: Optional[PlanGenerator] = None

def get_plan_generator() -> PlanGenerator:
    """获取计划生成器实例（单例模式）"""
    global _plan_generator
    if _plan_generator is None:
        _plan_generator = PlanGenerator()
    return _plan_generator


def generate_study_plan(subject: str, exam_date: str, 
                        daily_hours: float = 2.0,
                        use_ai: bool = True) -> StudyPlan:
    """
    生成学习计划（便捷函数）
    
    参数:
        subject: 科目名称
        exam_date: 考试日期
        daily_hours: 每日学习时长
        use_ai: 是否使用 AI 生成
    
    返回:
        生成的学习计划
    """
    generator = get_plan_generator()
    
    if use_ai and generator.ai_helper:
        return generator.generate_plan_ai(subject, exam_date, daily_hours)
    else:
        return generator.generate_plan_basic(subject, exam_date, daily_hours)
