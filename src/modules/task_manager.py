"""
StudyBuddy 任务管理模块
管理今日任务、截止时间和提醒功能
"""

import json
import os
from datetime import datetime, timedelta
from config import TASK_DATA_FILE, REMINDER_BEFORE_MINUTES


class Task:
    """单个任务类"""
    
    def __init__(self, title, description="", deadline=None):
        """
        初始化任务
        
        参数:
            title: 任务标题
            description: 任务描述
            deadline: 截止时间 (datetime 对象或字符串格式 "YYYY-MM-DD HH:MM")
        """
        self.id = id(self)  # 简单 ID 生成
        self.title = title
        self.description = description
        self.completed = False
        
        # 处理截止时间
        if deadline is None:
            self.deadline = None
        elif isinstance(deadline, str):
            try:
                self.deadline = datetime.strptime(deadline, "%Y-%m-%d %H:%M")
            except ValueError:
                try:
                    self.deadline = datetime.strptime(deadline, "%Y-%m-%d")
                except ValueError:
                    self.deadline = None
        else:
            self.deadline = deadline
        
        self.created_at = datetime.now()
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "deadline": self.deadline.strftime("%Y-%m-%d %H:%M") if self.deadline else None,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M")
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建"""
        task = cls(
            title=data["title"],
            description=data.get("description", ""),
            deadline=data.get("deadline")
        )
        task.id = data.get("id", id(task))
        task.completed = data.get("completed", False)
        if "created_at" in data:
            task.created_at = datetime.strptime(data["created_at"], "%Y-%m-%d %H:%M")
        return task
    
    def mark_complete(self):
        """标记为完成"""
        self.completed = True
    
    def get_time_remaining(self):
        """获取剩余时间（如果设置了截止时间）"""
        if self.deadline is None:
            return None
        remaining = self.deadline - datetime.now()
        return remaining
    
    def is_overdue(self):
        """是否已过期"""
        if self.deadline is None:
            return False
        return datetime.now() > self.deadline
    
    def is_near_deadline(self):
        """是否快到截止时间"""
        if self.deadline is None:
            return False
        remaining = self.get_time_remaining()
        if remaining is None:
            return False
        # 检查是否在提醒时间范围内
        reminder_threshold = timedelta(minutes=REMINDER_BEFORE_MINUTES)
        return timedelta(0) < remaining < reminder_threshold
    
    def get_time_string(self):
        """获取截止时间的字符串表示"""
        if self.deadline is None:
            return "无截止时间"
        
        if self.is_overdue():
            return "已过期"
        
        remaining = self.get_time_remaining()
        hours = int(remaining.total_seconds() / 3600)
        mins = int(remaining.total_seconds() % 3600 / 60)
        
        if hours > 0:
            return f"{hours}小时{mins}分钟后"
        else:
            return f"{mins}分钟后"
    
    def __str__(self):
        """字符串表示"""
        status = "✓" if self.completed else "○"
        
        result = f"[{status}] {self.title}"
        
        if self.deadline:
            if self.is_overdue():
                result += f" ⚠️ 已过期！"
            elif self.is_near_deadline():
                result += f" ⏰ 快截止了！({self.get_time_string()})"
            else:
                result += f" ⏰ {self.deadline.strftime('%m-%d %H:%M')}"
        
        return result


class TaskManager:
    """任务管理器类"""
    
    def __init__(self, data_file=None):
        """
        初始化任务管理器
        
        参数:
            data_file: 数据文件路径
        """
        self.data_file = data_file or TASK_DATA_FILE
        self.tasks = []
        self._load_tasks()
    
    def _load_tasks(self):
        """从文件加载任务"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 检查是否是新的一天
                    last_date = data.get("last_date", "")
                    today = datetime.now().strftime("%Y-%m-%d")
                    
                    if last_date != today:
                        # 新的一天，清空未完成的任务（或保留）
                        # 这里选择保留所有任务，但更新日期
                        pass
                    
                    self.tasks = [Task.from_dict(t) for t in data.get("tasks", [])]
            except (json.JSONDecodeError, KeyError):
                self.tasks = []
    
    def _save_tasks(self):
        """保存任务到文件"""
        data = {
            "last_date": datetime.now().strftime("%Y-%m-%d"),
            "tasks": [t.to_dict() for t in self.tasks]
        }
        # 确保目录存在
        dir_path = os.path.dirname(self.data_file)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_task(self, title, description="", deadline=None):
        """
        添加新任务
        
        参数:
            title: 任务标题
            description: 任务描述
            deadline: 截止时间
        
        返回:
            创建的任务对象
        """
        task = Task(title, description, deadline)
        self.tasks.append(task)
        self._save_tasks()
        return task
    
    def get_task(self, task_id):
        """根据 ID 获取任务"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def update_task(self, task_id, **kwargs):
        """
        更新任务
        
        参数:
            task_id: 任务 ID
            **kwargs: 要更新的字段
        
        返回:
            更新后的任务对象，如果不存在则返回 None
        """
        task = self.get_task(task_id)
        if task:
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            self._save_tasks()
        return task
    
    def delete_task(self, task_id):
        """
        删除任务
        
        参数:
            task_id: 任务 ID
        
        返回:
            是否删除成功
        """
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                self.tasks.pop(i)
                self._save_tasks()
                return True
        return False
    
    def mark_complete(self, task_id):
        """标记任务为完成"""
        task = self.get_task(task_id)
        if task:
            task.mark_complete()
            self._save_tasks()
            return True
        return False
    
    def get_tasks(self, status="all"):
        """
        获取任务列表
        
        参数:
            status: 任务状态 (all/pending/completed/overdue/near_deadline)
        
        返回:
            任务列表
        """
        result = self.tasks
        
        # 按状态过滤
        if status == "pending":
            result = [t for t in result if not t.completed]
        elif status == "completed":
            result = [t for t in result if t.completed]
        elif status == "overdue":
            result = [t for t in result if t.is_overdue() and not t.completed]
        elif status == "near_deadline":
            result = [t for t in result if t.is_near_deadline() and not t.completed]
        
        # 排序：未完成在前，按截止时间排序
        result.sort(key=lambda t: (t.completed, t.deadline or datetime.max))
        
        return result
    
    def get_reminders(self):
        """
        获取需要提醒的任务
        
        返回:
            包含即将截止和已过期的任务列表
        """
        reminders = {
            "overdue": [],
            "near_deadline": []
        }
        
        for task in self.tasks:
            if task.completed:
                continue
            if task.is_overdue():
                reminders["overdue"].append(task)
            elif task.is_near_deadline():
                reminders["near_deadline"].append(task)
        
        return reminders
    
    def check_reminders(self, callback=None):
        """
        检查并返回提醒信息
        
        参数:
            callback: 可选的回调函数
        
        返回:
            提醒信息字典
        """
        reminders = self.get_reminders()
        
        messages = []
        for task in reminders["overdue"]:
            msg = f"⚠️ 任务「{task.title}」已过期！"
            messages.append(msg)
            if callback:
                callback(msg)
        
        for task in reminders["near_deadline"]:
            remaining = task.get_time_remaining()
            hours = int(remaining.total_seconds() / 3600)
            mins = int(remaining.total_seconds() % 3600 / 60)
            msg = f"⏰ 任务「{task.title}」还有 {hours}小时{mins}分钟 截止！"
            messages.append(msg)
            if callback:
                callback(msg)
        
        return {
            "has_reminders": len(messages) > 0,
            "messages": messages,
            "overdue_count": len(reminders["overdue"]),
            "near_deadline_count": len(reminders["near_deadline"])
        }
    
    def get_stats(self):
        """
        获取任务统计信息
        
        返回:
            统计信息字典
        """
        total = len(self.tasks)
        completed = len([t for t in self.tasks if t.completed])
        pending = total - completed
        overdue = len([t for t in self.tasks if t.is_overdue() and not t.completed])
        
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "overdue": overdue,
            "completion_rate": (completed / total * 100) if total > 0 else 0
        }
    
    def clear_completed(self):
        """清除已完成的任务"""
        self.tasks = [t for t in self.tasks if not t.completed]
        self._save_tasks()
    
    def reset_today(self):
        """重置今日任务（保留历史记录）"""
        self.tasks = []
        self._save_tasks()
    
    def __len__(self):
        """返回任务总数"""
        return len(self.tasks)
    
    def __str__(self):
        """字符串表示"""
        stats = self.get_stats()
        return f"TaskManager: {stats['completed']}/{stats['total']} 完成 ({stats['completion_rate']:.0f}%)"
