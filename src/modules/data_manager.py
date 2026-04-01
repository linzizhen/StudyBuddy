"""
StudyBuddy 数据管理模块
管理用户设置、座右铭、学习数据等持久化数据
"""

import json
import os
from datetime import datetime
from config import USER_DATA_FILE, DEFAULT_DAILY_GOAL


class DataManager:
    """数据管理类"""
    
    def __init__(self, data_file=None):
        """
        初始化数据管理器
        
        参数:
            data_file: 数据文件路径
        """
        self.data_file = data_file or USER_DATA_FILE
        self.data = self._load_data()
    
    def _load_data(self):
        """从文件加载数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return self._get_default_data()
        return self._get_default_data()
    
    def _get_default_data(self):
        """获取默认数据"""
        return {
            "motto": "今天也要好好学习！",
            "favorite_quote": "",
            "daily_goal": DEFAULT_DAILY_GOAL,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_data(self):
        """保存数据到文件"""
        self.data["last_updated"] = datetime.now().isoformat()
        
        # 确保目录存在
        dir_path = os.path.dirname(self.data_file)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def get_motto(self):
        """获取座右铭"""
        return self.data.get("motto", "今天也要好好学习！")
    
    def set_motto(self, motto):
        """设置座右铭"""
        self.data["motto"] = motto
        self._save_data()
    
    def get_favorite_quote(self):
        """获取收藏的语录"""
        return self.data.get("favorite_quote", "")
    
    def set_favorite_quote(self, quote):
        """设置收藏的语录"""
        self.data["favorite_quote"] = quote
        self._save_data()
    
    def get_daily_goal(self):
        """获取每日学习目标（分钟）"""
        return self.data.get("daily_goal", DEFAULT_DAILY_GOAL)
    
    def set_daily_goal(self, minutes):
        """设置每日学习目标"""
        self.data["daily_goal"] = int(minutes)
        self._save_data()
    
    def get_all_settings(self):
        """获取所有设置"""
        return {
            "motto": self.get_motto(),
            "favorite_quote": self.get_favorite_quote(),
            "daily_goal": self.get_daily_goal()
        }
    
    def update_settings(self, **kwargs):
        """
        批量更新设置
        
        参数:
            **kwargs: 要更新的设置项
        """
        for key, value in kwargs.items():
            if key in self.data:
                self.data[key] = value
        self._save_data()
    
    def reset(self):
        """重置为默认设置"""
        self.data = self._get_default_data()
        self._save_data()
    
    def get_data(self):
        """获取所有数据"""
        return self.data.copy()


# 全局数据管理器实例
_data_manager = None


def get_data_manager():
    """获取全局数据管理器实例"""
    global _data_manager
    if _data_manager is None:
        _data_manager = DataManager()
    return _data_manager


# 便捷函数
def load_user_settings():
    """加载用户设置"""
    dm = get_data_manager()
    return dm.get_all_settings()


def save_user_settings(settings):
    """保存用户设置"""
    dm = get_data_manager()
    dm.update_settings(**settings)


def get_motto():
    """获取座右铭"""
    dm = get_data_manager()
    return dm.get_motto()


def set_motto(motto):
    """设置座右铭"""
    dm = get_data_manager()
    dm.set_motto(motto)


def get_favorite_quote():
    """获取收藏语录"""
    dm = get_data_manager()
    return dm.get_favorite_quote()


def set_favorite_quote(quote):
    """设置收藏语录"""
    dm = get_data_manager()
    dm.set_favorite_quote(quote)


def get_daily_goal():
    """获取每日目标"""
    dm = get_data_manager()
    return dm.get_daily_goal()


def set_daily_goal(minutes):
    """设置每日目标"""
    dm = get_data_manager()
    dm.set_daily_goal(minutes)
