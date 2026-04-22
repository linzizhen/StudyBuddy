"""
配置文件
包含所有可配置的阈值和参数
"""

import os
from pathlib import Path

# ============ 项目路径配置 ============
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

# ============ 摄像头配置 ============
CAMERA_CONFIG = {
    "camera_index": 0,              # 摄像头编号（通常为0）
    "fps": 30,                       # 目标帧率
    "frame_width": 640,             # 帧宽度
    "frame_height": 480,            # 帧高度
    "haarcascade_path": None,        # 人脸检测模型路径（None使用OpenCV内置）
}

# ============ 人脸检测配置 ============
FACE_DETECTION_CONFIG = {
    "min_face_size": (20, 20),       # 最小人脸尺寸（减小以提高灵敏度）
    "scale_factor": 1.05,            # 图像缩放因子（减小以提高精度）
    "min_neighbors": 3,              # 最小邻居数（减小以提高召回率）
    "face_missing_threshold": 5,     # 连续无人脸帧数阈值（触发离开）
    "face_present_threshold": 2,     # 连续有人脸帧数阈值（判定在场）
}

# ============ 行为检测配置 ============
BEHAVIOR_CONFIG = {
    # 学习软件白名单（窗口标题关键词，不区分大小写）
    "learning_apps": [
        # 编程开发工具
        "pycharm", "visual studio code", "vscode", "notepad",
        "notepad++", "sublime", "atom", "vim", "emacs",
        "eclipse", "intellij", "webstorm", "phpstorm",
        "goland", "clion", "rider", "datagrip",
        "android studio", "xcode", "unity", "unreal",
        "jupyter", "spyder", "jupyterlab", "ipython",
        "anaconda", "conda", "virtual studio",

        # 代码相关窗口
        "cursor", "ide", "编辑器", "编辑", "code",
        "terminal", "cmd", "powershell", "bash",
        "git", "github", "gitlab", "gitee",
        "docker", "kubernetes", "vmware",

        # 浏览器（通常用于学习）
        "chrome", "edge", "firefox", "safari", "opera", "brave",

        # 办公软件
        "word", "excel", "powerpoint", "wps",
        "文档", "表格", "演示", "office",

        # PDF和阅读
        "pdf", "adobe", "foxit", " SumatraPDF", "calibre",
        "kindle", "多看", "微信阅读",

        # 笔记软件
        "markdown", "typora", "obsidian", "notion",
        "有道云笔记", "印象笔记", "evernote",
        "onenote", "bear", "simplenote",
        "飞书", "钉钉", "slack",

        # 学习平台
        "learn", "study", "course", "class", "课程", "学习", "教育",
        "bilibili", "youtube", "网易云课堂", "慕课",
        "腾讯课堂", "中国大学MOOC", "mooc",
        "知乎", "简书", "csdn", "掘金", "segmentfault",
        "stackoverflow", "stack exchange",

        # 知识管理
        "anki", "anki记忆卡", "super memo",
        "marginnote", "liquidtext", "readwise",

        # 其他学习相关
        "dict", "词典", "翻译", "translator",
        "terminal", "命令", "shell", "console",
        "python", "java", "javascript", "typescript",
        "rust", "go", "c++", "c#", "php", "ruby",
    ],

    # 忽略的窗口标题关键词（完全忽略，不计入切换）
    "ignore_titles": [
        "welcome", "新建标签页", "new tab", "about:",
        "download", "下载", "downloads",
        "settings", "设置", "preferences",
        "about", "关于", "帮助", "help",
        "this empty page", "空白页", "new page",
    ],

    # 检测间隔（秒）
    "check_interval": 1.0,

    # 窗口切换检测窗口大小（用于计算切换频率）
    "switch_window_seconds": 60,

    # 分心切换阈值（60秒内切换次数超过此值视为分心）
    "distraction_switch_threshold": 15,  # 提高阈值，减少误判

    # 分心软件黑名单（命中后直接判定为分心，优先级高于白名单）
    "distraction_apps": [
        # 视频娱乐
        "bilibili", "哔哩哔哩", "抖音", "快手", "抖音", "火山", "西瓜视频",
        "腾讯视频", "爱奇艺", "优酷", "芒果TV", "人人视频",
        "youtube", "netflix", "twitch", "虎牙", "斗鱼", "哔哩哔哩",
        "potplayer", "vlc", "mpv", "暴风影音", "QQ音乐", "网易云音乐",

        # 游戏
        "steam", "epic", "origin", "uplay", "wegame", "battle.net",
        "minecraft", "mc", "原神", "genshin", "王者荣耀", "英雄联盟",
        "League of Legends", "Dota", "csgo", "pubg", "绝地求生",
        "我的世界", "迷你世界", "网易游戏", "游戏", "game",

        # 社交娱乐
        "微信", "wechat", "qq", "TIM", "QQ", "微博", "twitter",
        "instagram", "telegram", "discord", "reddit",

        # 新闻资讯
        "今日头条", "腾讯新闻", "网易新闻", "澎湃新闻",
    ],
}

# ============ 时间分析配置 ============
TIME_ANALYSIS_CONFIG = {
    "check_interval": 1.0,          # 检查间隔（秒）
    "short_break_seconds": 60,      # 短暂休息不算中断（增加到60秒）
    "long_break_seconds": 300,      # 5分钟以上离开算中断
    "focused_streak_bonus": 10,     # 连续专注奖励分数（每分钟）
}

# ============ 专注度评估配置 ============
ANALYZER_CONFIG = {
    # 评分权重（总和应为100）
    "weights": {
        "face_detected": 30,         # 人脸检测权重（提高）
        "window_on_learning": 25,    # 学习窗口权重（降低）
        "low_switch_frequency": 20,  # 低切换频率权重
        "continuous_focus_time": 25, # 连续专注时间权重
    },

    # 评分阈值（调整以更合理）
    "score_thresholds": {
        "focused": 65,              # 专注阈值（降低到65，更容易达到）
        "normal": 40,               # 一般阈值（降低到40）
    },

    # 延迟判断配置（增加延迟，减少跳变）
    "delay_config": {
        "distraction_delay": 8,      # 分心判定延迟（增加到8秒）
        "focus_delay": 5,            # 专注判定延迟（增加到5秒）
        "normal_delay": 5,          # 一般判定延迟
    },

    # 状态平滑配置
    "smoothing": {
        "enabled": True,            # 是否启用平滑
        "window_size": 5,           # 平滑窗口大小
    },
}

# ============ 系统配置 ============
SYSTEM_CONFIG = {
    "save_report_interval": 300,    # 保存报告间隔（秒）
    "log_level": "INFO",            # 日志级别
}

# ============ 提醒配置 ============
NOTIFIER_CONFIG = {
    "enable_sound": True,          # 是否启用声音提醒
    "enable_desktop": True,         # 是否启用桌面通知
    "state_change_reminder": True,  # 状态变化提醒
    "report_reminder": True,        # 定时报告提醒
    "reminder_interval": 300,       # 提醒间隔（秒）
}
