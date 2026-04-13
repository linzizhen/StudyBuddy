"""
StudyPal 成就徽章系统
学习激励与成就解锁机制

作者：StudyPal
创建日期：2026-04-13
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from config import ACHIEVEMENTS_FILE


class Achievement:
    """
    单个成就类
    
    属性：
    - id: 成就唯一标识
    - name: 成就名称
    - description: 成就描述
    - icon: 成就图标 (emoji)
    - condition_type: 条件类型
    - condition_value: 条件值
    - reward: 奖励积分
    """

    def __init__(self, achievement_id: str, name: str, description: str,
                 icon: str, condition_type: str, condition_value: Any,
                 reward: int = 10):
        """
        初始化成就

        参数:
            achievement_id: 成就唯一标识
            name: 成就名称
            description: 成就描述
            icon: 成就图标 (emoji)
            condition_type: 条件类型
            condition_value: 条件值
            reward: 奖励积分
        """
        self.id = achievement_id
        self.name = name
        self.description = description
        self.icon = icon
        self.condition_type = condition_type
        self.condition_value = condition_value
        self.reward = reward

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "condition_type": self.condition_type,
            "condition_value": self.condition_value,
            "reward": self.reward
        }

    def check_unlocked(self, user_stats: Dict) -> bool:
        """
        检查是否满足解锁条件

        参数:
            user_stats: 用户统计数据

        返回:
            是否满足解锁条件
        """
        current_value = user_stats.get(self.condition_type, 0)

        if self.condition_type == "streak_days":
            return current_value >= self.condition_value
        elif self.condition_type == "total_pomodoros":
            return current_value >= self.condition_value
        elif self.condition_type == "total_study_minutes":
            return current_value >= self.condition_value
        elif self.condition_type == "tasks_completed":
            return current_value >= self.condition_value
        elif self.condition_type == "single_day_minutes":
            return current_value >= self.condition_value
        elif self.condition_type == "ai_questions":
            return current_value >= self.condition_value
        elif self.condition_type == "conversations_count":
            return current_value >= self.condition_value
        elif self.condition_type == "goals_reached":
            return current_value >= self.condition_value

        return False


# 预定义的所有成就
ALL_ACHIEVEMENTS = [
    # 番茄钟成就
    Achievement("first_pomodoro", "初出茅庐", "完成第一个番茄钟",
                "🌱", "total_pomodoros", 1, 10),
    Achievement("five_pomodoros", "小有所成", "累计完成5个番茄钟",
                "🌿", "total_pomodoros", 5, 20),
    Achievement("ten_pomodoros", "渐入佳境", "累计完成10个番茄钟",
                "🌳", "total_pomodoros", 10, 30),
    Achievement("twenty_pomodoros", "专注达人", "累计完成20个番茄钟",
                "⭐", "total_pomodoros", 20, 50),
    Achievement("fifty_pomodoros", "番茄大师", "累计完成50个番茄钟",
                "🏆", "total_pomodoros", 50, 100),
    Achievement("hundred_pomodoros", "番茄传奇", "累计完成100个番茄钟",
                "👑", "total_pomodoros", 100, 200),

    # 连续学习成就
    Achievement("three_day_streak", "三天打鱼", "连续学习3天",
                "📅", "streak_days", 3, 15),
    Achievement("seven_day_streak", "一周不辍", "连续学习7天",
                "🔥", "streak_days", 7, 35),
    Achievement("fourteen_day_streak", "双周坚持", "连续学习14天",
                "💪", "streak_days", 14, 70),
    Achievement("thirty_day_streak", "月度之星", "连续学习30天",
                "🌟", "streak_days", 30, 150),

    # 学习时长成就
    Achievement("hour_study", "一小时", "累计学习满60分钟",
                "⏰", "total_study_minutes", 60, 15),
    Achievement("ten_hours_study", "十小时", "累计学习满600分钟",
                "📚", "total_study_minutes", 600, 50),
    Achievement("fifty_hours_study", "五十小时", "累计学习满3000分钟",
                "🎓", "total_study_minutes", 3000, 150),
    Achievement("hundred_hours_study", "百小时", "累计学习满6000分钟",
                "🏅", "total_study_minutes", 6000, 300),

    # 单日学习成就
    Achievement("one_hour_day", "单日一小时", "单日学习超过60分钟",
                "☀️", "single_day_minutes", 60, 20),
    Achievement("two_hours_day", "单日两小时", "单日学习超过120分钟",
                "🌤️", "single_day_minutes", 120, 40),
    Achievement("three_hours_day", "单日三小时", "单日学习超过180分钟",
                "🌈", "single_day_minutes", 180, 80),

    # 任务完成成就
    Achievement("first_task", "任务新手", "完成第一个任务",
                "✅", "tasks_completed", 1, 10),
    Achievement("ten_tasks", "任务达人", "累计完成10个任务",
                "📝", "tasks_completed", 10, 30),
    Achievement("fifty_tasks", "任务大师", "累计完成50个任务",
                "📋", "tasks_completed", 50, 100),

    # AI 对话成就
    Achievement("first_question", "初次提问", "向AI提出第一个问题",
                "💬", "ai_questions", 1, 5),
    Achievement("ten_questions", "好奇宝宝", "累计提问10次",
                "🤔", "ai_questions", 10, 20),
    Achievement("fifty_questions", "问题少年", "累计提问50次",
                "❓", "ai_questions", 50, 50),
    Achievement("hundred_questions", "问题大师", "累计提问100次",
                "🎯", "ai_questions", 100, 100),

    # 对话会话成就
    Achievement("five_conversations", "多会话", "创建5个不同的AI对话",
                "💭", "conversations_count", 5, 25),
    Achievement("twenty_conversations", "会话达人", "创建20个不同的AI对话",
                "🧠", "conversations_count", 20, 60),

    # 目标达成成就
    Achievement("first_goal", "达成目标", "首次达成每日学习目标",
                "🎯", "goals_reached", 1, 30),
    Achievement("seven_goals", "目标周", "累计达成7次每日目标",
                "🏆", "goals_reached", 7, 70),
]


class AchievementManager:
    """
    成就管理器类
    
    功能：
    - 成就解锁
    - 积分管理
    - 等级计算
    - 成就统计
    """

    def __init__(self, data_file=None):
        """
        初始化成就管理器

        参数:
            data_file: 数据文件路径
        """
        self.data_file = data_file or ACHIEVEMENTS_FILE
        self.unlocked_ids: List[str] = []
        self.total_points: int = 0
        self._load_data()

    def _load_data(self):
        """从文件加载数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.unlocked_ids = data.get("unlocked_ids", [])
                    self.total_points = data.get("total_points", 0)
            except (json.JSONDecodeError, IOError):
                self.unlocked_ids = []
                self.total_points = 0
        else:
            self.unlocked_ids = []
            self.total_points = 0

    def _save_data(self):
        """保存数据到文件"""
        data = {
            "unlocked_ids": self.unlocked_ids,
            "total_points": self.total_points,
            "last_updated": datetime.now().isoformat()
        }
        dir_path = os.path.dirname(self.data_file)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def is_unlocked(self, achievement_id: str) -> bool:
        """
        检查成就是否已解锁

        参数:
            achievement_id: 成就ID

        返回:
            是否已解锁
        """
        return achievement_id in self.unlocked_ids

    def unlock(self, achievement_id: str) -> bool:
        """
        解锁成就

        参数:
            achievement_id: 成就ID

        返回:
            是否成功解锁（false表示已存在）
        """
        if achievement_id in self.unlocked_ids:
            return False

        # 查找成就信息
        achievement = self._get_achievement_by_id(achievement_id)
        if not achievement:
            return False

        self.unlocked_ids.append(achievement_id)
        self.total_points += achievement.reward
        self._save_data()
        return True

    def _get_achievement_by_id(self, achievement_id: str) -> Optional[Achievement]:
        """根据ID获取成就对象"""
        for achievement in ALL_ACHIEVEMENTS:
            if achievement.id == achievement_id:
                return achievement
        return None

    def get_unlocked_achievements(self) -> List[Dict]:
        """
        获取已解锁的成就列表

        返回:
            成就列表
        """
        result = []
        for achievement_id in self.unlocked_ids:
            achievement = self._get_achievement_by_id(achievement_id)
            if achievement:
                result.append(achievement.to_dict())
        return result

    def get_all_achievements(self) -> List[Dict]:
        """
        获取所有成就列表（包含解锁状态）

        返回:
            成就列表
        """
        result = []
        for achievement in ALL_ACHIEVEMENTS:
            item = achievement.to_dict()
            item["unlocked"] = achievement.id in self.unlocked_ids
            result.append(item)
        return result

    def get_locked_achievements(self) -> List[Dict]:
        """
        获取未解锁的成就列表

        返回:
            成就列表
        """
        result = []
        for achievement in ALL_ACHIEVEMENTS:
            if achievement.id not in self.unlocked_ids:
                result.append(achievement.to_dict())
        return result

    def check_and_unlock(self, user_stats: Dict) -> List[Dict]:
        """
        检查用户统计并解锁符合条件的成就

        参数:
            user_stats: 用户统计数据

        返回:
            新解锁的成就列表
        """
        newly_unlocked = []

        for achievement in ALL_ACHIEVEMENTS:
            if achievement.id not in self.unlocked_ids:
                if achievement.check_unlocked(user_stats):
                    if self.unlock(achievement.id):
                        item = achievement.to_dict()
                        item["just_unlocked"] = True
                        newly_unlocked.append(item)

        return newly_unlocked

    def get_progress(self, achievement_id: str, user_stats: Dict) -> Dict:
        """
        获取成就进度

        参数:
            achievement_id: 成就ID
            user_stats: 用户统计数据

        返回:
            进度信息
        """
        achievement = self._get_achievement_by_id(achievement_id)
        if not achievement:
            return {"error": "成就不存在"}

        current_value = user_stats.get(achievement.condition_type, 0)
        progress = min(100, (current_value / achievement.condition_value) * 100)

        return {
            "id": achievement.id,
            "name": achievement.name,
            "current": current_value,
            "target": achievement.condition_value,
            "progress": progress,
            "unlocked": achievement.id in self.unlocked_ids
        }

    def get_points(self) -> int:
        """获取总积分"""
        return self.total_points

    def get_level(self) -> Dict:
        """
        根据积分计算等级

        返回:
            等级信息
        """
        points = self.total_points

        levels = [
            {"name": "学习小白", "min_points": 0, "icon": "🌱"},
            {"name": "学习新手", "min_points": 50, "icon": "🌿"},
            {"name": "学习少年", "min_points": 150, "icon": "🌳"},
            {"name": "学习达人", "min_points": 300, "icon": "⭐"},
            {"name": "学习精英", "min_points": 500, "icon": "🌟"},
            {"name": "学习大师", "min_points": 800, "icon": "🏆"},
            {"name": "学习传奇", "min_points": 1200, "icon": "👑"},
        ]

        current_level = levels[0]
        next_level = None

        for i, level in enumerate(levels):
            if points >= level["min_points"]:
                current_level = level
                next_level = levels[i + 1] if i < len(levels) - 1 else None

        progress = 100
        if next_level:
            current_min = current_level["min_points"]
            next_min = next_level["min_points"]
            progress = ((points - current_min) / (next_min - current_min)) * 100

        return {
            "level": current_level,
            "next_level": next_level,
            "points": points,
            "progress": min(100, progress)
        }

    def get_stats(self) -> Dict:
        """
        获取成就统计

        返回:
            统计信息
        """
        return {
            "total_achievements": len(ALL_ACHIEVEMENTS),
            "unlocked_count": len(self.unlocked_ids),
            "locked_count": len(ALL_ACHIEVEMENTS) - len(self.unlocked_ids),
            "total_points": self.total_points,
            "completion_rate": len(self.unlocked_ids) / len(ALL_ACHIEVEMENTS) * 100
        }


# 全局实例
_achievement_manager: Optional[AchievementManager] = None


def get_achievement_manager() -> AchievementManager:
    """获取成就管理器实例"""
    global _achievement_manager
    if _achievement_manager is None:
        _achievement_manager = AchievementManager()
    return _achievement_manager


def get_achievements_data() -> Dict:
    """
    获取所有成就数据

    返回:
        成就数据字典
    """
    manager = get_achievement_manager()
    level_info = manager.get_level()

    return {
        "achievements": manager.get_all_achievements(),
        "stats": manager.get_stats(),
        "level": level_info,
        "unlocked": manager.get_unlocked_achievements()
    }


def unlock_achievement(achievement_id: str) -> bool:
    """
    解锁成就

    参数:
        achievement_id: 成就ID

    返回:
        是否成功
    """
    manager = get_achievement_manager()
    return manager.unlock(achievement_id)


def check_achievements(user_stats: Dict) -> List[Dict]:
    """
    检查并解锁成就

    参数:
        user_stats: 用户统计数据

    返回:
        新解锁的成就列表
    """
    manager = get_achievement_manager()
    return manager.check_and_unlock(user_stats)
