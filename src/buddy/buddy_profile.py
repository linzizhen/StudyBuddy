"""
StudyPal 搭子档案模块
管理用户档案和搭子基本信息

包含：
- 用户考研目标信息
- 搭子基本信息（名字、性格设定）
- 备考阶段管理

作者：StudyPal
日期：2026-04-27
重构日期：2026-04-30（文件锁保护）
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from src.utils.file_lock import atomic_read_json, atomic_write_json


class BuddyProfile:
    """
    搭子档案类
    
    管理用户档案和搭子基本信息
    """

    DEFAULT_DATA = {
        "user": {
            "name": "",
            "target_school": "",
            "target_major": "",
            "target_score": 0,
            "exam_date": "",
            "study_type": "normal",
            "daily_goal_hours": 8,
            "weak_subjects": [],
            "strong_subjects": [],
            "created_at": ""
        },
        "buddy": {
            "name": "小豆",
            "emoji": "🌸",
            "personality": "温柔但有原则",
            "introduction": "我是小豆，会陪你走完这段考研路",
            "role_id": "xiaodou",
            "level": 1,
            "custom_name": None,
            "total_interactions": 0,
            "created_at": ""
        }
    }

    def __init__(self, data_file: str = "data/buddy_profile.json"):
        self.data_file = data_file
        self.data: Dict[str, Any] = {}
        self._load()

    def _load(self):
        """从文件加载数据"""
        data = atomic_read_json(self.data_file, self.DEFAULT_DATA.copy())
        self.data = data
        if "user" not in self.data:
            self.data["user"] = self.DEFAULT_DATA["user"].copy()
        if "buddy" not in self.data:
            self.data["buddy"] = self.DEFAULT_DATA["buddy"].copy()
        else:
            defaults = self.DEFAULT_DATA["buddy"]
            buddy = self.data["buddy"]
            if "role_id" not in buddy:
                buddy["role_id"] = defaults["role_id"]
            if "level" not in buddy:
                buddy["level"] = defaults["level"]
            if "custom_name" not in buddy:
                buddy["custom_name"] = defaults["custom_name"]
            if "total_interactions" not in buddy:
                buddy["total_interactions"] = defaults["total_interactions"]
            if "emoji" not in buddy:
                buddy["emoji"] = defaults["emoji"]

    def _save(self):
        """保存数据到文件"""
        atomic_write_json(self.data_file, self.data)

    def get_profile(self) -> Dict[str, Any]:
        """获取完整档案"""
        profile = self.data.copy()
        # 合并数据库用户配置
        db_user = self._get_db_user()
        if db_user:
            profile["user"]["ai_model_key"] = db_user.ai_model_key
            profile["user"]["ai_custom_config"] = db_user.ai_custom_config
            profile["user"]["current_role_id"] = db_user.current_role_id
            profile["user"]["daily_goal_hours"] = db_user.daily_goal_hours
            profile["user"]["target_school"] = db_user.target_school
            profile["user"]["target_major"] = db_user.target_major
            profile["user"]["target_score"] = db_user.target_score
            profile["buddy"]["role_id"] = db_user.current_role_id
            if db_user.custom_buddy_name:
                profile["buddy"]["name"] = db_user.custom_buddy_name
        return profile

    def _get_db_user(self):
        """从数据库获取当前登录用户"""
        try:
            from flask import g, current_app
            if hasattr(g, 'current_user'):
                return g.current_user
            if hasattr(current_app, '_user'):
                return current_app._user
        except Exception:
            pass
        return None

    def get_user(self) -> Dict[str, Any]:
        """获取用户信息"""
        return self.data.get("user", {}).copy()

    def get_buddy_info(self) -> Dict[str, Any]:
        """获取搭子信息"""
        return self.data.get("buddy", {}).copy()

    def is_setup_complete(self) -> bool:
        """检查档案是否设置完整"""
        user = self.data.get("user", {})
        return bool(
            user.get("target_school") and
            user.get("target_major") and
            user.get("exam_date")
        )

    def update_user(self, **kwargs):
        """更新用户信息"""
        if "user" not in self.data:
            self.data["user"] = {}
        for key, value in kwargs.items():
            if key in [
                "name", "target_school", "target_major", "target_score",
                "exam_date", "study_type", "daily_goal_hours",
                "weak_subjects", "strong_subjects"
            ]:
                self.data["user"][key] = value
        self._save()

    def update_buddy(self, **kwargs):
        """更新搭子信息"""
        if "buddy" not in self.data:
            self.data["buddy"] = {}
        allowed_fields = ["name", "personality", "introduction", "role_id", "level", "custom_name", "emoji"]
        for key, value in kwargs.items():
            if key in allowed_fields:
                self.data["buddy"][key] = value
        self._save()

    def get_buddy_role_id(self) -> str:
        """获取当前搭子角色ID"""
        return self.data.get("buddy", {}).get("role_id", "xiaodou")

    def get_buddy_level(self) -> int:
        """获取搭子等级"""
        return self.data.get("buddy", {}).get("level", 1)

    def increment_interactions(self):
        """增加交互次数"""
        if "buddy" not in self.data:
            self.data["buddy"] = {}
        self.data["buddy"]["total_interactions"] = self.data["buddy"].get("total_interactions", 0) + 1
        self._save()

    def get_days_remaining(self) -> int:
        """获取距离考试的天数"""
        exam_date = self.data.get("user", {}).get("exam_date")
        if not exam_date:
            return -1
        try:
            exam = datetime.strptime(exam_date, "%Y-%m-%d")
            today = datetime.now()
            return max(0, (exam - today).days)
        except (ValueError, TypeError):
            return -1

    def get_current_phase(self) -> str:
        """获取当前备考阶段"""
        days = self.get_days_remaining()
        if days < 0:
            return "未设置目标"
        elif days <= 30:
            return "冲刺阶段"
        elif days <= 90:
            return "强化阶段"
        else:
            return "基础阶段"

    def get_study_summary(self) -> str:
        """获取学习概况摘要（用于AI提示词）"""
        user = self.data.get("user", {})
        days = self.get_days_remaining()

        parts = []
        if user.get("target_school"):
            parts.append(f"目标：{user['target_school']}")
        if user.get("target_major"):
            parts.append(f"{user['target_major']}")
        if user.get("target_score"):
            parts.append(f"目标分数：{user['target_score']}分")
        if days >= 0:
            parts.append(f"距离考试：{days}天")

        phase = self.get_current_phase()
        if phase != "未设置目标":
            parts.append(f"当前阶段：{phase}")

        return "，".join(parts) if parts else "尚未设置目标"

    def reset(self):
        """重置档案"""
        self.data = self.DEFAULT_DATA.copy()
        self.data["user"]["created_at"] = datetime.now().isoformat()
        self._save()


# 全局单例
_profile_instance: Optional[BuddyProfile] = None


def get_buddy_profile() -> BuddyProfile:
    """获取搭子档案实例"""
    global _profile_instance
    if _profile_instance is None:
        _profile_instance = BuddyProfile()
    return _profile_instance
