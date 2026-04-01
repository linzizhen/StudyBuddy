"""
StudyBuddy 学习日历模块
记录学习历史、统计学习数据、生成学习报告
"""

import json
import os
from datetime import datetime, timedelta
from config import CALENDAR_DATA_FILE


class StudyCalendar:
    """学习日历类"""
    
    def __init__(self, data_file=None):
        """
        初始化学习日历
        
        参数:
            data_file: 数据文件路径
        """
        self.data_file = data_file or CALENDAR_DATA_FILE
        self.history = {}  # 格式：{"YYYY-MM-DD": total_minutes}
        self._load_history()
    
    def _load_history(self):
        """从文件加载历史数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.history = data.get("history", {})
            except (json.JSONDecodeError, KeyError):
                self.history = {}
    
    def _save_history(self):
        """保存历史数据到文件"""
        data = {
            "history": self.history
        }
        # 确保目录存在
        dir_path = os.path.dirname(self.data_file)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def log_study(self, duration_minutes, date=None):
        """
        记录学习时长
        
        参数:
            duration_minutes: 学习时长（分钟）
            date: 日期字符串 "YYYY-MM-DD"，默认为今天
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        if date in self.history:
            self.history[date] += duration_minutes
        else:
            self.history[date] = duration_minutes
        
        self._save_history()
    
    def get_today_duration(self):
        """获取今日学习时长"""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.history.get(today, 0)
    
    def get_duration(self, date):
        """
        获取指定日期的学习时长
        
        参数:
            date: 日期字符串 "YYYY-MM-DD" 或 datetime 对象
        
        返回:
            学习时长（分钟）
        """
        if isinstance(date, datetime):
            date = date.strftime("%Y-%m-%d")
        return self.history.get(date, 0)
    
    def get_week_duration(self, date=None):
        """
        获取本周学习总时长
        
        参数:
            date: 日期，默认为今天
        
        返回:
            本周学习总时长（分钟）
        """
        if date is None:
            date = datetime.now()
        elif isinstance(date, str):
            date = datetime.strptime(date, "%Y-%m-%d")
        
        # 获取本周第一天（周一）
        weekday = date.weekday()
        monday = date - timedelta(days=weekday)
        
        total = 0
        for i in range(7):
            day = monday + timedelta(days=i)
            day_str = day.strftime("%Y-%m-%d")
            total += self.history.get(day_str, 0)
        
        return total
    
    def get_month_duration(self, year=None, month=None):
        """
        获取指定月份的学习总时长
        
        参数:
            year: 年份
            month: 月份
        
        返回:
            月份学习总时长（分钟）
        """
        if year is None or month is None:
            now = datetime.now()
            year = now.year
            month = now.month
        
        total = 0
        # 获取该月的所有天数
        if month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month + 1, 1)
        
        first_day = datetime(year, month, 1)
        last_day = next_month - timedelta(days=1)
        
        current = first_day
        while current <= last_day:
            day_str = current.strftime("%Y-%m-%d")
            total += self.history.get(day_str, 0)
            current += timedelta(days=1)
        
        return total
    
    def get_streak(self):
        """
        获取连续学习天数
        
        返回:
            连续学习天数
        """
        streak = 0
        today = datetime.now().date()
        
        # 检查今天是否学习了
        today_str = today.strftime("%Y-%m-%d")
        if today_str not in self.history or self.history[today_str] == 0:
            # 今天还没学习，从今天前一天开始算
            today = today - timedelta(days=1)
            today_str = today.strftime("%Y-%m-%d")
            if today_str not in self.history or self.history[today_str] == 0:
                return 0
        
        # 从昨天开始往前数
        current = today
        while True:
            current_str = current.strftime("%Y-%m-%d")
            if current_str in self.history and self.history[current_str] > 0:
                streak += 1
                current = current - timedelta(days=1)
            else:
                break
        
        return streak
    
    def get_stats(self):
        """
        获取学习统计信息
        
        返回:
            统计信息字典
        """
        today = datetime.now()
        
        # 今日时长
        today_duration = self.get_today_duration()
        
        # 本周时长
        week_duration = self.get_week_duration()
        
        # 本月时长
        month_duration = self.get_month_duration()
        
        # 总学习时长
        total_duration = sum(self.history.values())
        
        # 总学习天数
        total_days = len([d for d, m in self.history.items() if m > 0])
        
        # 连续学习天数
        streak = self.get_streak()
        
        # 平均每日学习时长（最近 7 天）
        week_days = 7
        avg_daily = week_duration / week_days if week_days > 0 else 0
        
        return {
            "today": today_duration,
            "week": week_duration,
            "month": month_duration,
            "total": total_duration,
            "total_days": total_days,
            "streak": streak,
            "avg_daily": avg_daily
        }
    
    def get_weekly_data(self, days=7):
        """
        获取最近几天的学习数据
        
        参数:
            days: 天数，默认为 7
        
        返回:
            包含日期和时长的列表
        """
        result = []
        today = datetime.now()
        
        for i in range(days - 1, -1, -1):
            day = today - timedelta(days=i)
            day_str = day.strftime("%Y-%m-%d")
            duration = self.history.get(day_str, 0)
            
            # 星期几的中文名称
            weekday_names = ["一", "二", "三", "四", "五", "六", "日"]
            weekday = weekday_names[day.weekday()]
            
            result.append({
                "date": day_str,
                "weekday": f"周{weekday}",
                "duration": duration
            })
        
        return result
    
    def get_monthly_data(self, year=None, month=None):
        """
        获取指定月份的学习数据
        
        参数:
            year: 年份
            month: 月份
        
        返回:
            包含日期和时长的列表
        """
        if year is None or month is None:
            now = datetime.now()
            year = now.year
            month = now.month
        
        result = []
        
        # 获取该月的所有天数
        if month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month + 1, 1)
        
        first_day = datetime(year, month, 1)
        last_day = next_month - timedelta(days=1)
        
        current = first_day
        while current <= last_day:
            day_str = current.strftime("%Y-%m-%d")
            duration = self.history.get(day_str, 0)
            
            result.append({
                "date": day_str,
                "day": current.day,
                "weekday": current.weekday(),  # 0=周一，6=周日
                "duration": duration
            })
            
            current += timedelta(days=1)
        
        return result
    
    def get_report(self, period="week"):
        """
        生成学习报告
        
        参数:
            period: 周期 (day/week/month)
        
        返回:
            报告字符串
        """
        stats = self.get_stats()
        
        if period == "day":
            return f"今日学习：{stats['today']} 分钟"
        
        elif period == "week":
            return (
                f"📊 本周学习报告\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"本周总时长：{stats['week']} 分钟\n"
                f"平均每日：{stats['avg_daily']:.1f} 分钟\n"
                f"连续学习：{stats['streak']} 天\n"
                f"━━━━━━━━━━━━━━━━"
            )
        
        elif period == "month":
            return (
                f"📊 本月学习报告\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"本月总时长：{stats['month']} 分钟\n"
                f"总学习天数：{stats['total_days']} 天\n"
                f"━━━━━━━━━━━━━━━━"
            )
        
        else:
            return (
                f"📊 学习统计\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"今日：{stats['today']} 分钟\n"
                f"本周：{stats['week']} 分钟\n"
                f"本月：{stats['month']} 分钟\n"
                f"总计：{stats['total']} 分钟\n"
                f"学习天数：{stats['total_days']} 天\n"
                f"连续：{stats['streak']} 天\n"
                f"━━━━━━━━━━━━━━━━"
            )
    
    def clear_history(self):
        """清除所有历史数据"""
        self.history = {}
        self._save_history()
    
    def __str__(self):
        """字符串表示"""
        stats = self.get_stats()
        return f"StudyCalendar: 总计{stats['total']}分钟，连续{stats['streak']}天"
