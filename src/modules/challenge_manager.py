"""
StudyPal 挑战管理模块
管理用户的"我的挑战"模块：小学/初中/高中三阶段差异化挑战体系

作者：StudyPal
创建日期：2026-06-29
"""

import json
import os
import sys
import uuid
from datetime import datetime
from src.utils.file_lock import atomic_read_json, atomic_write_json

# 与项目其他模块保持一致的配置加载方式
_config_loaded = False
for p in list(sys.path):
    if not p:
        continue
    if os.path.exists(os.path.join(p, 'config.py')) and 'ai_supervisor' not in p:
        try:
            sys.path.insert(0, p)
            from config import DATA_DIR
            _config_loaded = True
            break
        except ImportError:
            continue

if not _config_loaded:
    DATA_DIR = "data"

CHALLENGE_DATA_FILE = os.path.join(DATA_DIR, "challenges.json")
USER_SETTINGS_FILE = os.path.join(DATA_DIR, "user_settings.json")

# 学段预设配置
GRADE_MODES = ["primary", "middle", "high"]
GRADE_LABELS = {"primary": "小学", "middle": "初中", "high": "高中"}

# 学段默认学科模板
DEFAULT_SUBJECTS = {
    "primary": [
        {"name": "语文城堡", "icon": "🏰", "full_score": 100, "display_mode": "star"},
        {"name": "数学森林", "icon": "🌲", "full_score": 100, "display_mode": "star"},
        {"name": "英语海洋", "icon": "🌊", "full_score": 100, "display_mode": "star"},
        {"name": "科学秘境", "icon": "🔬", "full_score": 100, "display_mode": "star"},
    ],
    "middle": [
        {"name": "语文", "icon": "📝", "full_score": 150, "display_mode": "star"},
        {"name": "数学", "icon": "🔢", "full_score": 150, "display_mode": "star"},
        {"name": "英语", "icon": "🌍", "full_score": 150, "display_mode": "star"},
        {"name": "物理", "icon": "⚛️", "full_score": 100, "display_mode": "star"},
        {"name": "化学", "icon": "🧪", "full_score": 100, "display_mode": "star"},
    ],
    "high": [
        {"name": "语文", "icon": "📝", "full_score": 150, "display_mode": "score"},
        {"name": "数学", "icon": "🔢", "full_score": 150, "display_mode": "score"},
        {"name": "英语", "icon": "🌍", "full_score": 150, "display_mode": "score"},
        {"name": "物理", "icon": "⚛️", "full_score": 100, "display_mode": "score"},
        {"name": "化学", "icon": "🧪", "full_score": 100, "display_mode": "score"},
        {"name": "生物", "icon": "🧬", "full_score": 100, "display_mode": "score"},
    ],
}

# 可选图标库（供用户在前端选择）
ICON_LIBRARY = [
    "📝", "🔢", "🌍", "⚛️", "🧪", "🧬", "📚", "🏰", "🌲", "🌊",
    "🔬", "🎨", "🎵", "⚽", "🏃", "🌟", "🎯", "🧠", "💡", "📐",
]


class ChallengeManager:
    """
    挑战管理类

    功能：
    - 加载/保存挑战数据
    - 切换学段
    - 增删改挑战、学科、里程碑、时间线节点
    - 记录成绩
    - 从旧版考研目标数据迁移
    """

    def __init__(self, data_file=None):
        self.data_file = data_file or CHALLENGE_DATA_FILE
        self.data = self._load_data()

    def _load_data(self):
        """加载挑战数据"""
        default = self._get_default_data()
        loaded = atomic_read_json(self.data_file, default)
        # 兼容旧版空数据
        if not loaded or "challenges" not in loaded:
            return default
        return loaded

    def _get_default_data(self):
        """获取默认数据结构"""
        return {
            "user_grade_mode": "middle",
            "active_challenge_id": None,
            "challenges": [],
        }

    def _save_data(self):
        """保存数据"""
        atomic_write_json(self.data_file, self.data)

    # ============ 学段管理 ============

    def set_grade_mode(self, grade_mode):
        """设置用户学段"""
        if grade_mode not in GRADE_MODES:
            raise ValueError(f"无效学段: {grade_mode}")
        self.data["user_grade_mode"] = grade_mode
        self._save_data()

    def get_grade_mode(self):
        """获取当前学段"""
        return self.data.get("user_grade_mode", "middle")

    # ============ 挑战管理 ============

    def list_challenges(self):
        """列出所有挑战"""
        return self.data.get("challenges", [])

    def get_active_challenge(self):
        """获取当前激活的挑战"""
        active_id = self.data.get("active_challenge_id")
        challenges = self.list_challenges()
        if not challenges:
            return None
        if active_id:
            for ch in challenges:
                if ch["id"] == active_id:
                    return ch
        return challenges[0]

    def set_active_challenge(self, challenge_id):
        """设置当前激活的挑战"""
        self.data["active_challenge_id"] = challenge_id
        self._save_data()

    def get_challenge(self, challenge_id):
        """获取指定挑战"""
        for ch in self.list_challenges():
            if ch["id"] == challenge_id:
                return ch
        return None

    def create_challenge(self, name, grade_mode, challenge_type, deadline, description=""):
        """新建挑战"""
        if grade_mode not in GRADE_MODES:
            raise ValueError(f"无效学段: {grade_mode}")

        challenge_id = f"ch_{uuid.uuid4().hex[:8]}"
        subjects = []
        for tpl in DEFAULT_SUBJECTS.get(grade_mode, []):
            subjects.append({
                "id": f"sub_{uuid.uuid4().hex[:8]}",
                "name": tpl["name"],
                "icon": tpl["icon"],
                "display_mode": tpl["display_mode"],
                "target_score": int(tpl["full_score"] * 0.85),
                "full_score": tpl["full_score"],
                "current_score": 0,
                "current_level": 0,
                "max_level": 5 if grade_mode == "primary" else 10,
                "scores_history": [],
                "weak_points": [],
                "notes": "",
            })

        challenge = {
            "id": challenge_id,
            "name": name,
            "grade_mode": grade_mode,
            "type": challenge_type,
            "deadline": deadline,
            "description": description,
            "status": "active",
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "subjects": subjects,
            "milestones": [],
            "timeline": [],
        }
        self.data["challenges"].append(challenge)
        if not self.data.get("active_challenge_id"):
            self.data["active_challenge_id"] = challenge_id
        self.data["user_grade_mode"] = grade_mode
        self._save_data()
        return challenge

    def update_challenge(self, challenge_id, **kwargs):
        """更新挑战信息"""
        ch = self.get_challenge(challenge_id)
        if not ch:
            return None
        for key in ("name", "grade_mode", "type", "deadline", "description", "status"):
            if key in kwargs:
                ch[key] = kwargs[key]
        self._save_data()
        return ch

    def delete_challenge(self, challenge_id):
        """删除挑战"""
        self.data["challenges"] = [
            ch for ch in self.list_challenges() if ch["id"] != challenge_id
        ]
        if self.data.get("active_challenge_id") == challenge_id:
            self.data["active_challenge_id"] = (
                self.data["challenges"][0]["id"] if self.data["challenges"] else None
            )
        self._save_data()

    # ============ 学科管理 ============

    def add_subject(self, challenge_id, subject):
        """添加学科"""
        ch = self.get_challenge(challenge_id)
        if not ch:
            return None
        new_subject = {
            "id": f"sub_{uuid.uuid4().hex[:8]}",
            "name": subject.get("name", "新学科"),
            "icon": subject.get("icon", "📚"),
            "display_mode": subject.get("display_mode", "score"),
            "target_score": subject.get("target_score", 100),
            "full_score": subject.get("full_score", 100),
            "current_score": subject.get("current_score", 0),
            "current_level": subject.get("current_level", 0),
            "max_level": subject.get("max_level", 10),
            "scores_history": [],
            "weak_points": subject.get("weak_points", []),
            "notes": subject.get("notes", ""),
        }
        ch["subjects"].append(new_subject)
        self._save_data()
        return new_subject

    def update_subject(self, challenge_id, subject_id, **kwargs):
        """更新学科"""
        ch = self.get_challenge(challenge_id)
        if not ch:
            return None
        for sub in ch["subjects"]:
            if sub["id"] == subject_id:
                for key in ("name", "icon", "display_mode", "target_score",
                            "full_score", "current_score", "current_level",
                            "weak_points", "notes"):
                    if key in kwargs:
                        sub[key] = kwargs[key]
                self._save_data()
                return sub
        return None

    def delete_subject(self, challenge_id, subject_id):
        """删除学科"""
        ch = self.get_challenge(challenge_id)
        if not ch:
            return
        ch["subjects"] = [s for s in ch["subjects"] if s["id"] != subject_id]
        self._save_data()

    # ============ 成绩记录 ============

    def add_score_record(self, challenge_id, subject_id, date, score, exam_name="", note=""):
        """记录成绩"""
        ch = self.get_challenge(challenge_id)
        if not ch:
            return None
        for sub in ch["subjects"]:
            if sub["id"] == subject_id:
                sub["scores_history"].append({
                    "date": date,
                    "score": score,
                    "full_score": sub["full_score"],
                    "exam_name": exam_name,
                })
                sub["scores_history"].sort(key=lambda x: x["date"])
                sub["current_score"] = score
                # 更新关卡（小学场景）
                if sub.get("display_mode") == "star" and sub.get("max_level", 0) > 0:
                    ratio = score / sub["full_score"] if sub["full_score"] else 0
                    sub["current_level"] = min(
                        sub["max_level"],
                        max(0, int(ratio * sub["max_level"] + 0.5))
                    )
                self._save_data()
                return sub
        return None

    # ============ 里程碑管理 ============

    def add_milestone(self, challenge_id, milestone):
        """添加对比项"""
        ch = self.get_challenge(challenge_id)
        if not ch:
            return None
        new_ms = {
            "id": f"ms_{uuid.uuid4().hex[:8]}",
            "name": milestone.get("name", "对比项"),
            "value": milestone.get("value", 0),
            "full_score": milestone.get("full_score", 100),
            "type": milestone.get("type", "custom"),
            "comparison_text": milestone.get("comparison_text", ""),
            "visible": milestone.get("visible", True),
        }
        ch["milestones"].append(new_ms)
        self._save_data()
        return new_ms

    def toggle_milestone_visible(self, challenge_id, milestone_id):
        """切换对比项可见性"""
        ch = self.get_challenge(challenge_id)
        if not ch:
            return
        for ms in ch["milestones"]:
            if ms["id"] == milestone_id:
                ms["visible"] = not ms["visible"]
                self._save_data()
                return

    def delete_milestone(self, challenge_id, milestone_id):
        """删除对比项"""
        ch = self.get_challenge(challenge_id)
        if not ch:
            return
        ch["milestones"] = [m for m in ch["milestones"] if m["id"] != milestone_id]
        self._save_data()

    # ============ 时间线节点管理 ============

    def add_timeline_node(self, challenge_id, node):
        """添加时间线节点"""
        ch = self.get_challenge(challenge_id)
        if not ch:
            return None
        new_node = {
            "id": f"tl_{uuid.uuid4().hex[:8]}",
            "name": node.get("name", "新节点"),
            "date": node.get("date", ""),
            "type": node.get("type", "exam"),
            "icon": node.get("icon", "📝"),
            "completed": node.get("completed", False),
            "urgency": node.get("urgency", "medium"),
        }
        ch["timeline"].append(new_node)
        ch["timeline"].sort(key=lambda x: x["date"])
        self._save_data()
        return new_node

    def toggle_timeline_completed(self, challenge_id, node_id):
        """切换时间线节点完成状态"""
        ch = self.get_challenge(challenge_id)
        if not ch:
            return
        for node in ch["timeline"]:
            if node["id"] == node_id:
                node["completed"] = not node["completed"]
                self._save_data()
                return

    def delete_timeline_node(self, challenge_id, node_id):
        """删除时间线节点"""
        ch = self.get_challenge(challenge_id)
        if not ch:
            return
        ch["timeline"] = [n for n in ch["timeline"] if n["id"] != node_id]
        self._save_data()

    # ============ 数据迁移 ============

    def migrate_from_user_settings(self):
        """从旧版 user_settings.json 迁移考研目标数据"""
        if not os.path.exists(USER_SETTINGS_FILE):
            return {"migrated": False, "reason": "user_settings.json 不存在"}

        old_data = atomic_read_json(USER_SETTINGS_FILE, {})
        old_goal = old_data.get("exam_goal") or old_data.get("goal") or {}
        if not old_goal:
            return {"migrated": False, "reason": "旧数据中没有考研目标"}

        # 如果已有挑战，不重复迁移
        if self.data.get("challenges"):
            return {"migrated": False, "reason": "挑战数据已存在，跳过迁移"}

        # 构建迁移后的挑战（标记为高中考研场景）
        school = old_goal.get("school", "")
        major = old_goal.get("major", "")
        target_score = old_goal.get("target_score", 0)
        exam_date = old_goal.get("exam_date", "")

        description_parts = []
        if school:
            description_parts.append(f"目标院校：{school}")
        if major:
            description_parts.append(f"目标专业：{major}")
        description = " / ".join(description_parts) if description_parts else "从旧数据迁移"

        new_challenge = {
            "id": f"ch_mig_{uuid.uuid4().hex[:8]}",
            "name": f"{old_goal.get('name', '考研冲刺')}",
            "grade_mode": "high",
            "type": "考研",
            "deadline": exam_date or "",
            "description": description,
            "status": "active",
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "subjects": [
                {
                    "id": f"sub_mig_{uuid.uuid4().hex[:8]}",
                    "name": "总分",
                    "icon": "🎯",
                    "display_mode": "score",
                    "target_score": target_score or 380,
                    "full_score": 500,
                    "current_score": 0,
                    "current_level": 0,
                    "max_level": 0,
                    "scores_history": [],
                    "weak_points": [],
                    "notes": "已从旧版考研目标迁移",
                }
            ],
            "milestones": [
                {
                    "id": f"ms_mig_{uuid.uuid4().hex[:8]}",
                    "name": "目标分数",
                    "value": target_score or 380,
                    "full_score": 500,
                    "type": "custom",
                    "comparison_text": f"目标：{target_score or 380} 分",
                    "visible": True,
                }
            ] if target_score else [],
            "timeline": [
                {
                    "id": f"tl_mig_{uuid.uuid4().hex[:8]}",
                    "name": "考研日期",
                    "date": exam_date or "",
                    "type": "exam",
                    "icon": "🎓",
                    "completed": False,
                    "urgency": "high",
                }
            ] if exam_date else [],
        }

        self.data["challenges"].append(new_challenge)
        self.data["active_challenge_id"] = new_challenge["id"]
        self.data["user_grade_mode"] = "high"
        self._save_data()
        return {"migrated": True, "challenge_id": new_challenge["id"]}

    # ============ 预设模板查询 ============

    def get_grade_presets(self, grade_mode):
        """获取指定学段的学科预设模板"""
        return DEFAULT_SUBJECTS.get(grade_mode, [])

    def get_icon_library(self):
        """获取图标库"""
        return ICON_LIBRARY


def get_challenge_manager():
    """工厂函数：获取挑战管理器实例"""
    return ChallengeManager()