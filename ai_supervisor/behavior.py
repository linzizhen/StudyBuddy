"""
行为检测模块
负责检测窗口活动和切换行为
"""

import time
import logging
import os
from typing import Optional, List, Dict, Tuple
from collections import deque
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)

# 延迟导入psutil
psutil = None


def _get_psutil():
    """延迟加载psutil"""
    global psutil
    if psutil is None:
        try:
            import psutil as _psutil
            psutil = _psutil
        except ImportError:
            logger.warning("psutil未安装，部分功能可能受限")
    return psutil


@dataclass
class WindowInfo:
    """窗口信息数据类"""
    title: str
    process_name: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class FocusResult:
    """专注度评估结果"""
    state: str          # 专注 / 一般 / 分心
    score: int           # 综合评分 0~100
    reasons: List[str]  # 各维度扣分/加分原因
    details: Dict = field(default_factory=dict)  # 各维度详细分数


@dataclass
class FocusExplanation:
    """
    当前状态的自然语言解释
    """
    summary: str                          # 一句话总结
    factors: List[str]                    # 影响状态的因素列表
    suggestions: List[str]                # 改善建议（仅分心状态时提供）
    is_distraction_confirmed: bool        # 分心是否已确认（延迟判断生效）


class ReminderService:
    """
    提醒服务：检测到持续分心状态时触发提醒（print模拟）
    """

    def __init__(self):
        self._last_remind_time: Optional[float] = None
        self._cooldown_seconds: float = 30.0    # 同类提醒间隔
        self._last_state: Optional[str] = None  # 上次提醒的状态
        self._remind_count: int = 0             # 累计提醒次数

    def _print_remind(self, message: str, state: str):
        """统一 print 模拟提醒输出"""
        prefix_map = {
            "distraction": "[分心提醒]",
            "focused": "[专注鼓励]",
            "normal": "[专注提示]",
        }
        prefix = prefix_map.get(state, "[提醒]")
        print(f"\n{'='*50}")
        print(f"{prefix} {message}")
        print(f"{'='*50}\n")

    def _should_remind(self, current_state: str, current_time: float) -> bool:
        """判断是否应该触发提醒（冷却控制）"""
        # 状态发生变化时重置冷却
        if self._last_state != current_state:
            self._last_state = current_state
            self._last_remind_time = current_time
            return True
        # 同状态在冷却期内不提醒
        if (
            self._last_remind_time is not None
            and current_time - self._last_remind_time < self._cooldown_seconds
        ):
            return False
        self._last_remind_time = current_time
        return True

    def trigger(self, explanation: FocusExplanation, current_time: float = None):
        """
        根据状态解释触发提醒

        Args:
            explanation: 状态解释对象
            current_time: 当前时间戳（None则用time.time()）
        """
        if current_time is None:
            current_time = time.time()

        state = explanation.summary
        is_confirmed = explanation.is_distraction_confirmed

        # 仅在分心状态已确认时触发提醒
        if is_confirmed and self._should_remind("distraction", current_time):
            self._remind_count += 1
            self._print_remind(
                f"检测到持续分心！已连续提醒 {self._remind_count} 次。\n"
                + "可能原因：\n  " + "\n  ".join(explanation.factors) + "\n"
                + "建议：\n  " + "\n  ".join(explanation.suggestions),
                state="distraction",
            )
            return True

        return False

    def reset(self):
        """重置提醒状态"""
        self._last_remind_time = None
        self._last_state = None
        self._remind_count = 0


class BehaviorDetector:
    """
    行为检测器类
    """

    def __init__(self, check_interval: float = None):
        """
        初始化行为检测器

        Args:
            check_interval: 检测间隔（秒）
        """
        # 配置（延迟加载避免循环导入）
        self.check_interval = check_interval or 1.0

        # 白名单配置
        self.learning_apps: List[str] = []
        self.ignore_titles: List[str] = []
        self.distraction_apps: List[str] = []
        self._init_config()

        # 窗口切换记录
        self.window_history: deque = deque(maxlen=1000)  # 最多记录1000条
        self.switch_times: deque = deque(maxlen=100)     # 切换时间戳

        # 当前状态
        self.current_window: Optional[WindowInfo] = None
        self.last_check_time = time.time()

        # 切换统计
        self.switch_count = 0
        self.total_switch_time_window = 60  # 默认60秒
        self.distraction_threshold = 10     # 默认10次

        # 连续学习时间跟踪
        self._study_start_time: Optional[float] = None  # 当前学习时段开始时间
        self._last_update_time: float = time.time()      # 上次更新时间（用于检测离线）
        self._offline_threshold: float = 5.0             # 超过此秒数视为离线/失焦

        # 状态平滑：最近5次score缓存
        self._score_history: deque = deque(maxlen=5)

        # 延迟判断：跟踪分心持续时间
        self._distraction_start_time: Optional[float] = None  # 分心状态开始时间
        self._distraction_persist_seconds: float = 5.0        # 分心必须持续N秒才生效

        # 提醒服务
        self.reminder = ReminderService()

        # 初始化窗口检测器
        self._init_window_detector()
    
    def _init_config(self):
        """初始化配置"""
        try:
            from .config import BEHAVIOR_CONFIG, TIME_ANALYSIS_CONFIG
            self.check_interval = BEHAVIOR_CONFIG.get("check_interval", 1.0)

            # 学习窗口白名单（优先级：黑名单 > 白名单 > 其他）
            learning_apps = [app.lower() for app in BEHAVIOR_CONFIG.get("learning_apps", [])]

            # 分心软件黑名单（命中后直接判定为分心）
            distraction_apps = [app.lower() for app in BEHAVIOR_CONFIG.get("distraction_apps", [])]

            # 从白名单中移除已在黑名单中的软件（避免歧义）
            distraction_set = set(distraction_apps)
            learning_apps = [app for app in learning_apps if app not in distraction_set]

            self.learning_apps = learning_apps
            self.ignore_titles = [title.lower() for title in BEHAVIOR_CONFIG.get("ignore_titles", [])]
            self.distraction_apps = distraction_apps
            self.total_switch_time_window = BEHAVIOR_CONFIG.get("switch_window_seconds", 60)
            self.distraction_threshold = BEHAVIOR_CONFIG.get("distraction_switch_threshold", 10)
        except:
            # 默认配置
            self.learning_apps = [
                "pycharm", "visual studio code", "vscode", "notepad",
                "notepad++", "sublime", "atom", "vim", "emacs",
                "eclipse", "intellij", "webstorm", "phpstorm",
                "goland", "clion", "rider", "datagrip",
                "android studio", "xcode", "unity", "unreal",
                "jupyter", "spyder", "jupyterlab", "ipython",
                "anaconda", "conda", "virtual studio",
                "cursor", "ide", "编辑器", "编辑", "code",
                "terminal", "cmd", "powershell", "bash",
                "git", "github", "gitlab", "gitee",
                "docker", "kubernetes", "vmware",
                "chrome", "edge", "firefox", "safari", "opera", "brave",
                "word", "excel", "powerpoint", "wps",
                "文档", "表格", "演示", "office",
                "pdf", "adobe", "foxit", "sumatrapdf", "calibre",
                "kindle", "多看", "微信阅读",
                "markdown", "typora", "obsidian", "notion",
                "有道云笔记", "印象笔记", "evernote",
                "onenote", "bear", "simplenote",
                "飞书", "钉钉", "slack",
                "learn", "study", "course", "class", "课程", "学习", "教育",
                "bilibili", "youtube", "网易云课堂", "慕课",
                "腾讯课堂", "中国大学MOOC", "mooc",
                "知乎", "简书", "csdn", "掘金", "segmentfault",
                "stackoverflow", "stack exchange",
                "anki", "anki记忆卡", "super memo",
                "marginnote", "liquidtext", "readwise",
                "dict", "词典", "翻译", "translator",
                "terminal", "命令", "shell", "console",
                "python", "java", "javascript", "typescript",
                "rust", "go", "c++", "c#", "php", "ruby",
            ]
            self.ignore_titles = [
                "welcome", "新建标签页", "new tab", "about:",
                "download", "下载", "downloads",
                "settings", "设置", "preferences",
                "about", "关于", "帮助", "help",
                "this empty page", "空白页", "new page",
            ]
            self.distraction_apps = [
                "bilibili", "哔哩哔哩", "抖音", "快手", "火山", "西瓜视频",
                "腾讯视频", "爱奇艺", "优酷", "芒果TV", "人人视频",
                "youtube", "netflix", "twitch", "虎牙", "斗鱼",
                "potplayer", "vlc", "mpv", "暴风影音", "QQ音乐", "网易云音乐",
                "steam", "epic", "origin", "uplay", "wegame", "battle.net",
                "minecraft", "mc", "原神", "genshin", "王者荣耀", "英雄联盟",
                "League of Legends", "Dota", "csgo", "pubg", "绝地求生",
                "我的世界", "迷你世界", "网易游戏", "game",
                "微信", "wechat", "qq", "TIM", "QQ", "微博", "twitter",
                "instagram", "telegram", "discord", "reddit",
                "今日头条", "腾讯新闻", "网易新闻", "澎湃新闻",
            ]
            self.total_switch_time_window = 60
            self.distraction_threshold = 10

        # 专注度评估配置
        self._focus_weights = {
            "window_type": 0.40,
            "face": 0.20,
            "switch_freq": 0.20,
            "study_time": 0.20,
        }
        self._focus_state_thresholds = {
            "focused": 70,
            "normal": 40,
        }
    
    def _init_window_detector(self):
        """初始化窗口检测器"""
        self._get_foreground_window = None
        
        try:
            import win32gui
            import win32process
            
            def get_foreground_window_info():
                """获取前台窗口信息"""
                try:
                    hwnd = win32gui.GetForegroundWindow()
                    if hwnd == 0:
                        return None
                    
                    title = win32gui.GetWindowText(hwnd)
                    if not title:
                        title = ""
                    
                    try:
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    except:
                        pid = 0
                    
                    _psutil = _get_psutil()
                    process_name = ""
                    if _psutil:
                        try:
                            process = _psutil.Process(pid)
                            process_name = process.name().lower()
                        except:
                            pass
                    
                    return WindowInfo(
                        title=title,
                        process_name=process_name,
                        timestamp=time.time()
                    )
                except Exception as e:
                    logger.debug(f"获取窗口信息失败: {e}")
                    return None
            
            self._get_foreground_window = get_foreground_window_info
            logger.info("Windows窗口检测器初始化成功")
            
        except ImportError:
            logger.warning("win32gui/win32process 未安装，使用替代方案")
            
            _psutil = _get_psutil()
            if _psutil:
                def get_foreground_window_info():
                    """使用psutil获取前台窗口"""
                    try:
                        for proc in _psutil.process_iter(['name']):
                            try:
                                pinfo = proc.info
                                name = pinfo.get('name', '')
                                windows = pinfo.get('windows', '')
                                if windows:
                                    return WindowInfo(
                                        title=str(windows[0]) if windows else '',
                                        process_name=name.lower(),
                                        timestamp=time.time()
                                    )
                            except:
                                pass
                        return None
                    except:
                        return None
                
                self._get_foreground_window = get_foreground_window_info
                logger.info("使用psutil窗口检测器")
    
    def _is_learning_related(self, window: WindowInfo) -> bool:
        """
        判断窗口是否与学习相关

        Args:
            window: 窗口信息

        Returns:
            是否与学习相关
        """
        if window is None:
            return False

        title_lower = window.title.lower()
        process_lower = window.process_name.lower()

        # 检查是否在忽略列表中
        for ignore in self.ignore_titles:
            if ignore in title_lower:
                return False

        # 检查是否在白名单中
        for app in self.learning_apps:
            if app in title_lower or app in process_lower:
                return True

        return False

    def _is_distraction_related(self, window: WindowInfo) -> bool:
        """
        判断窗口是否属于分心软件（黑名单，优先级高于白名单）

        Args:
            window: 窗口信息

        Returns:
            是否为分心软件窗口
        """
        if window is None:
            return False

        title_lower = window.title.lower()
        process_lower = window.process_name.lower()

        for app in self.distraction_apps:
            if app in title_lower or app in process_lower:
                return True

        return False

    def is_distraction_window(self) -> bool:
        """
        判断当前窗口是否为分心软件

        Returns:
            是否为分心窗口
        """
        self.update()
        return self._is_distraction_related(self.current_window)

    def get_window_status(self) -> Dict:
        """
        获取当前窗口状态（结构化返回）

        返回：
            - window_name: 当前窗口名称（标题）
            - is_learning: 是否为学习软件
            - is_distraction: 是否为分心软件
            - switch_count_10s: 近10秒内窗口切换次数
            - process_name: 进程名
            - raw_window: 原始窗口对象（可能为None）
        """
        self.update()
        win = self.current_window

        window_name = win.title if win else ""
        process_name = win.process_name if win else ""
        is_learning = self._is_learning_related(win) if win else False
        is_distraction = self._is_distraction_related(win) if win else False
        switch_count_10s = self.get_switch_count(time_window=10.0)

        return {
            "window_name": window_name,
            "is_learning": is_learning,
            "is_distraction": is_distraction,
            "switch_count_10s": switch_count_10s,
            "process_name": process_name,
            "raw_window": win,
        }
    
    def _detect_switch(self, new_window: WindowInfo) -> bool:
        """
        检测是否发生了窗口切换
        
        Args:
            new_window: 新窗口信息
            
        Returns:
            是否发生了切换
        """
        if self.current_window is None:
            return new_window is not None
        
        if new_window is None:
            return self.current_window is not None
        
        # 比较窗口是否发生变化
        return (self.current_window.title != new_window.title or
                self.current_window.process_name != new_window.process_name)
    
    def update(self) -> bool:
        """
        更新当前窗口状态

        Returns:
            当前是否为学习窗口
        """
        current_time = time.time()

        # 检查是否需要更新
        if current_time - self.last_check_time < self.check_interval:
            if self.current_window is None:
                return False
            return self._is_learning_related(self.current_window)

        self.last_check_time = current_time

        if self._get_foreground_window is None:
            return False

        new_window = self._get_foreground_window()

        if self._detect_switch(new_window):
            self.switch_count += 1
            self.switch_times.append(current_time)

            if self.current_window is not None:
                self.window_history.append(self.current_window)

        self.current_window = new_window

        # 跟踪连续学习时间
        is_learning = self._is_learning_related(new_window)
        time_since_last = current_time - self._last_update_time

        if is_learning:
            if self._study_start_time is None:
                self._study_start_time = current_time - self.check_interval
            if time_since_last > self._offline_threshold:
                self._study_start_time = current_time - self.check_interval
        else:
            self._study_start_time = None

        self._last_update_time = current_time
        return is_learning
    
    def is_learning_window(self) -> bool:
        """
        判断当前窗口是否为学习窗口
        
        Returns:
            是否为学习窗口
        """
        return self.update()
    
    def get_switch_frequency(self, time_window: float = None) -> float:
        """
        获取窗口切换频率
        
        Args:
            time_window: 时间窗口（秒）
            
        Returns:
            切换频率（次/时间窗口）
        """
        time_window = time_window or self.total_switch_time_window
        current_time = time.time()
        
        # 清理过期记录
        cutoff_time = current_time - time_window
        while self.switch_times and self.switch_times[0] < cutoff_time:
            self.switch_times.popleft()
        
        return len(self.switch_times)
    
    def is_high_switch_frequency(self) -> bool:
        """
        判断切换频率是否过高
        
        Returns:
            是否过高
        """
        frequency = self.get_switch_frequency()
        return frequency > self.distraction_threshold
    
    def get_switch_count(self, time_window: float = None) -> int:
        """
        获取时间窗口内的切换次数

        Args:
            time_window: 时间窗口（秒）

        Returns:
            切换次数
        """
        time_window = time_window or self.total_switch_time_window
        current_time = time.time()

        # 清理过期记录
        cutoff_time = current_time - time_window
        while self.switch_times and self.switch_times[0] < cutoff_time:
            self.switch_times.popleft()

        return len(self.switch_times)

    def _calc_window_score(self) -> Tuple[float, str]:
        """
        计算当前窗口类型的得分（40%）

        优先级：黑名单 > 白名单 > 其他

        Returns:
            (得分, 原因描述)
        """
        if self.current_window is None:
            return 0.0, "无法获取窗口信息"

        # 优先检查黑名单（分心软件直接0分）
        if self._is_distraction_related(self.current_window):
            return 0.0, f"当前窗口为分心软件: {self.current_window.title or self.current_window.process_name}"

        if self._is_learning_related(self.current_window):
            return 100.0, f"当前使用学习软件: {self.current_window.title or self.current_window.process_name}"
        else:
            return 0.0, f"当前窗口与学习无关: {self.current_window.title or self.current_window.process_name}"

    def _calc_face_score(self, face_state: Optional[str] = None) -> Tuple[float, str]:
        """
        计算人脸检测得分（20%）

        Args:
            face_state: 人脸状态，来自外部传入；None 表示无数据

        Returns:
            (得分, 原因描述)
        """
        if face_state is None:
            return 50.0, "人脸检测: 无数据"

        face_state = face_state.lower()
        if face_state in ("focused", "present", "专注", "正常"):
            return 100.0, "人脸检测: 检测到专注"
        elif face_state in ("looking_away", "away", "离开", "未检测到"):
            return 0.0, "人脸检测: 未检测到人脸或视线离开"
        elif face_state in ("sleeping", "sleep", "睡觉", "睡着"):
            return 0.0, "人脸检测: 检测到睡觉"
        else:
            return 50.0, f"人脸检测: 状态未知({face_state})"

    def _calc_switch_score(self) -> Tuple[float, str]:
        """
        计算窗口切换频率得分（20%）
        0次切换=100分，超过阈值=0分，中间线性插值
        同时检测短期频繁切换（10秒内超过5次）给予额外惩罚

        Returns:
            (得分, 原因描述)
        """
        switches = self.get_switch_count()
        threshold = self.distraction_threshold

        # 检测短期频繁切换（10秒内超过5次视为频繁）
        burst_switches = self.get_switch_count(time_window=10.0)
        burst_threshold = 5
        is_burst = burst_switches >= burst_threshold

        if switches == 0 and not is_burst:
            return 100.0, "窗口切换: 无切换"
        elif switches >= threshold:
            return 0.0, f"窗口切换: 过于频繁({switches}次)"
        elif is_burst:
            # 短期频繁，额外扣分
            burst_penalty = 20.0 * (burst_switches - burst_threshold + 1)
            score = max(0.0, 80.0 - burst_penalty)
            return score, f"窗口切换: 近期频繁切换({burst_switches}次/10秒)，扣分警告"
        else:
            score = 100.0 * (1.0 - switches / threshold)
            return score, f"窗口切换: {switches}次，频率正常"

    def _calc_study_time_score(self) -> Tuple[float, str]:
        """
        计算连续学习时间得分（20%）
        <1分钟=20分，1~5分钟线性增长，>5分钟=100分

        Returns:
            (得分, 原因描述)
        """
        if self._study_start_time is None:
            return 0.0, "学习时间: 未开始学习"

        elapsed = time.time() - self._study_start_time

        if elapsed < 60:
            return 20.0, f"学习时间: {int(elapsed)}秒，刚进入状态"
        elif elapsed < 300:
            score = 20.0 + 80.0 * (elapsed - 60) / 240
            return score, f"学习时间: {int(elapsed)}秒，逐渐专注"
        else:
            return 100.0, f"学习时间: {int(elapsed // 60)}分钟，持续专注"

    def evaluate_focus(self, face_state: Optional[str] = None) -> FocusResult:
        """
        评估当前专注度（带平滑和延迟判断）

        机制说明：
            1. 状态平滑：保存最近5次原始score，取平均值作为最终判断
            2. 延迟判断：分心状态必须持续5秒以上才生效，短暂波动不影响状态

        权重分配:
            * 当前窗口是否为学习软件: 40%
            * 人脸检测: 20%
            * 窗口切换频率: 20%
            * 连续学习时间: 20%

        Args:
            face_state: 人脸状态，可选值:
                - "focused"/"present"/"专注"/"正常"  → 100分
                - "looking_away"/"away"/"离开"/"未检测到" → 0分
                - "sleeping"/"sleep"/"睡觉"/"睡着"   → 0分
                - None → 50分（无数据）

        Returns:
            FocusResult: 包含 state(专注/一般/分心), score(0~100), reasons(原因列表), details(各维度分数)
        """
        # 先更新一次窗口状态
        self.update()

        w_score, w_reason = self._calc_window_score()
        f_score, f_reason = self._calc_face_score(face_state)
        s_score, s_reason = self._calc_switch_score()
        t_score, t_reason = self._calc_study_time_score()

        weights = self._focus_weights
        raw_score = round(
            w_score * weights["window_type"]
            + f_score * weights["face"]
            + s_score * weights["switch_freq"]
            + t_score * weights["study_time"]
        )

        # 限制在 0~100
        raw_score = max(0, min(100, raw_score))

        # --- 机制1：状态平滑 ---
        # 将本次原始分存入历史
        self._score_history.append(raw_score)
        # 取最近N次的平均值作为最终分（不满N次时用当前值）
        avg_score = round(sum(self._score_history) / len(self._score_history))

        # --- 机制2：延迟判断（分心必须持续5秒才生效） ---
        current_time = time.time()
        is_distraction = avg_score < self._focus_state_thresholds["normal"]

        # 短期频繁切换检测
        burst_switches = self.get_switch_count(time_window=10.0)
        is_burst = burst_switches >= 5

        if is_distraction:
            # 记录分心开始时间
            if self._distraction_start_time is None:
                self._distraction_start_time = current_time
            elapsed = current_time - self._distraction_start_time
            if elapsed < self._distraction_persist_seconds:
                # 未达到持续阈值，按"一般"状态处理（短暂波动不改变状态）
                final_state = "一般"
                delay_note = f"（延迟判断：分心状态持续{int(elapsed)}秒，还需{int(self._distraction_persist_seconds - elapsed)}秒生效）"
            else:
                final_state = "分心"
                delay_note = "（延迟判断：分心持续已满）"
        else:
            # 非分心状态，重置计时器
            self._distraction_start_time = None
            delay_note = ""
            if avg_score >= self._focus_state_thresholds["focused"]:
                final_state = "专注"
            else:
                final_state = "一般"

        reasons = [r for r in [w_reason, f_reason, s_reason, t_reason] if r]
        if delay_note:
            reasons.append(delay_note)

        details = {
            "raw_score": raw_score,
            "smoothed_score": avg_score,
            "score_history_count": len(self._score_history),
            "window_score": round(w_score, 1),
            "face_score": round(f_score, 1),
            "switch_score": round(s_score, 1),
            "study_time_score": round(t_score, 1),
            "burst_switches_10s": burst_switches,  # 短期频繁切换次数（10秒内）
        }

        result = FocusResult(
            state=final_state,
            score=avg_score,
            reasons=reasons,
            details=details,
        )

        # 自动触发提醒（分心确认时）
        exp = self.explain_state(result, face_state)
        self.reminder.trigger(exp, current_time)

        return result

    def explain_state(self, result: FocusResult = None, face_state: Optional[str] = None) -> FocusExplanation:
        """
        生成当前状态的自然语言解释

        Args:
            result: 已有的评估结果（None则重新评估）
            face_state: 人脸状态

        Returns:
            FocusExplanation: 包含总结、因素、建议
        """
        if result is None:
            result = self.evaluate_focus(face_state)

        win = self.current_window
        switches = self.get_switch_count()
        is_distraction_confirmed = (
            result.state == "分心"
            and self._distraction_start_time is not None
            and time.time() - self._distraction_start_time >= self._distraction_persist_seconds
        )

        # 收集影响因素
        factors: List[str] = []
        suggestions: List[str] = []

        # 1. 分心软件黑名单（优先检查，黑名单直接给出最强提示）
        is_distraction_app = win and self._is_distraction_related(win)
        if is_distraction_app:
            factors.append(f"检测到分心软件：{win.process_name or win.title}")
            suggestions.append("关闭娱乐软件，专注学习")

        # 2. 窗口类型（排除已处理过的分心软件）
        window_score = result.details.get("window_score", 0)
        if window_score < 50 and not is_distraction_app:
            win_name = win.title if win else "未知窗口"
            # 安全处理窗口名编码
            try:
                win_name = win_name.encode('gbk', errors='ignore').decode('gbk', errors='ignore')
                win_name = ''.join(c for c in win_name if ord(c) > 31 or c in '\n ')
            except:
                win_name = "未知窗口"
            factors.append(f"当前窗口不是学习软件（{win_name}）")
            suggestions.append("切换到学习软件或打开相关学习内容")

        # 3. 窗口切换
        switch_score = result.details.get("switch_score", 0)
        burst_switches = result.details.get("burst_switches_10s", 0)
        if switch_score < 50:
            if burst_switches >= 5:
                factors.append(f"检测到短期频繁切换（{burst_switches}次/10秒），已被额外扣分")
            else:
                factors.append(f"检测到频繁切换窗口（近{self.total_switch_time_window}秒内 {switches} 次）")
            suggestions.append("减少窗口切换，保持在一个窗口内学习")

        # 4. 人脸检测
        face_score = result.details.get("face_score", 0)
        if face_score < 50:
            factors.append("未检测到人脸或视线离开")
            suggestions.append("保持面向屏幕，不要离开座位")

        # 5. 学习时间
        study_time_score = result.details.get("study_time_score", 0)
        if study_time_score < 50:
            factors.append("连续学习时间较短")
            suggestions.append("尝试持续学习至少5分钟再休息")

        # 生成总结
        if is_distraction_confirmed:
            summary = "当前处于分心状态"
        elif result.state == "专注":
            summary = f"专注状态良好（{result.score}分）"
        elif result.state == "一般":
            summary = f"专注度一般（{result.score}分），有提升空间"
        else:
            summary = f"分心状态（{result.score}分），持续{self._distraction_persist_seconds}秒后生效"

        return FocusExplanation(
            summary=summary,
            factors=factors,
            suggestions=suggestions,
            is_distraction_confirmed=is_distraction_confirmed,
        )
    
    def get_current_window_info(self) -> Optional[Dict]:
        """
        获取当前窗口信息
        
        Returns:
            窗口信息字典
        """
        if self.current_window is None:
            return None
        
        return {
            "title": self.current_window.title,
            "process": self.current_window.process_name,
            "is_learning": self._is_learning_related(self.current_window),
            "timestamp": self.current_window.timestamp
        }
    
    def get_statistics(self) -> Dict:
        """
        获取行为统计信息
        
        Returns:
            统计信息字典
        """
        return {
            "switch_count": self.switch_count,
            "switch_frequency": self.get_switch_frequency(),
            "is_high_frequency": self.is_high_switch_frequency(),
            "current_window": self.get_current_window_info(),
            "history_count": len(self.window_history)
        }
    
    def reset_statistics(self):
        """重置统计数据"""
        self.switch_count = 0
        self.switch_times.clear()
        self.window_history.clear()
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        pass
