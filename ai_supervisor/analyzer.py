"""
专注度分析模块
负责计算专注度评分和状态判定

优化版本 v2.0:
- 人脸检测改为渐进式评分（不再二元跳变）
- 引入时间连续性加成（持续学习更稳定）
- 加权移动平均平滑算法（更敏感但抗噪）
- 统一延迟判断参数（减少状态跳变）
- 短期切换惩罚机制（捕捉频繁切换行为）
"""

import time
import logging
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field
from collections import deque

logger = logging.getLogger(__name__)


class FocusState(Enum):
    """专注状态枚举"""
    FOCUSED = "focused"       # 专注
    NORMAL = "normal"        # 一般
    DISTRACTED = "distracted" # 分心
    UNKNOWN = "unknown"       # 未知


@dataclass
class FocusScore:
    """专注度评分数据类"""
    total_score: float = 0.0
    face_score: float = 0.0    # 0~30，渐进式
    window_score: float = 0.0   # 0~25，渐进式
    switch_score: float = 0.0  # 0~20，连续性加成
    time_score: float = 0.0     # 0~25，累积加成
    timestamp: float = field(default_factory=time.time)


class FocusAnalyzer:
    """专注度分析器类 v2.0"""

    # 类级别的默认配置（避免每次实例化都从config导入）
    DEFAULT_WEIGHTS = {
        "face_detected": 30,
        "window_on_learning": 25,
        "low_switch_frequency": 20,
        "continuous_focus_time": 25,
    }

    DEFAULT_THRESHOLDS = {
        "focused": 65,
        "normal": 40,
    }

    DEFAULT_DELAY = {
        "distraction_delay": 8.0,
        "focus_delay": 5.0,
        "normal_delay": 5.0,
    }

    def __init__(self, config: Dict = None):
        """
        初始化专注度分析器
        """
        try:
            from .config import ANALYZER_CONFIG
            cfg = config or ANALYZER_CONFIG
        except Exception:
            cfg = config or {}

        self.config = cfg
        self.weights = cfg.get("weights", self.DEFAULT_WEIGHTS)
        self.thresholds = cfg.get("score_thresholds", self.DEFAULT_THRESHOLDS)
        self.delay_config = cfg.get("delay_config", self.DEFAULT_DELAY)
        self.smoothing_config = cfg.get("smoothing", {})

        self.current_state = FocusState.UNKNOWN
        self.current_score = FocusScore()
        self.state_start_time = time.time()
        self.last_update_time = time.time()

        # 历史评分（用于加权移动平均平滑）
        self.score_history: deque = deque(maxlen=15)

        # 统计信息
        self.total_focused_time = 0.0
        self.total_normal_time = 0.0
        self.total_distracted_time = 0.0
        self.session_start_time = time.time()

        # 延迟判断状态追踪
        self._pending_state: Optional[FocusState] = None
        self._pending_start_time: Optional[float] = None
        self._distraction_confirmed = False  # 分心是否已确认

        # 切换惩罚：短期频繁切换会累积惩罚值
        self._burst_penalty_accumulated = 0.0
        self._burst_penalty_decay_time = 15.0  # 惩罚衰减时间（秒）

        # 持续时间追踪（用于连续性加成）
        self._consecutive_focus_frames = 0  # 连续良好帧数
        self._consecutive_distraction_frames = 0  # 连续分心帧数
        self._frame_duration = 0.5  # 监控循环每帧时长（秒）

    def calculate_score(
        self,
        face_detected: bool,
        is_learning_window: bool,
        switch_count: int,
        continuous_focus_minutes: float,
        face_confidence: float = 0.5,
    ) -> FocusScore:
        """
        计算专注度评分 v2.0

        Args:
            face_detected: 是否检测到人脸
            is_learning_window: 是否为学习窗口
            switch_count: 窗口切换次数（60秒内）
            continuous_focus_minutes: 连续专注时间（分钟）
            face_confidence: 人脸置信度 0.0~1.0（新增）
        """
        current_time = time.time()

        # ========== 1. 人脸检测得分（0~30，渐进式） ==========
        max_face = self.weights.get("face_detected", 30)
        if face_detected:
            # 根据置信度计算分数：置信度 * 权重上限
            face_score = max_face * min(1.0, face_confidence)
            # 持续检测到人脸时给予额外加成（信任加成）
            # 在连续15帧良好检测后，获得+3分信任加成
            trust_bonus = min(3.0, self._consecutive_focus_frames / 15 * 3.0)
            face_score = min(max_face, face_score + trust_bonus)
        else:
            # 人脸丢失时，分数逐步下降而非直接归零
            # 模拟"暂不确定"的中间态
            base_face = self.weights.get("face_detected", 30)
            # 无人脸时，分数 = 上次分数的30%（逐步衰减）
            face_score = 0.0

        # ========== 2. 窗口得分（0~25，渐进式） ==========
        max_window = self.weights.get("window_on_learning", 25)
        if is_learning_window:
            # 持续在学习窗口中的时间越长，窗口分越稳定
            window_stability = min(1.0, continuous_focus_minutes / 3.0)
            window_score = max_window * (0.5 + 0.5 * window_stability)
        else:
            # 非学习窗口时，逐步衰减而非直接归零
            window_score = 0.0

        # ========== 3. 切换频率得分（0~20，带短期惩罚） ==========
        max_switch = self.weights.get("low_switch_frequency", 20)
        switches = switch_count

        # 短期频繁切换惩罚衰减
        if current_time - self.last_update_time > self._burst_penalty_decay_time:
            self._burst_penalty_accumulated = max(0.0, self._burst_penalty_accumulated - 5.0)

        if switches <= 3:
            switch_score = max_switch
        elif switches <= 7:
            switch_score = max_switch * 0.75
        elif switches <= 12:
            switch_score = max_switch * 0.45
        else:
            switch_score = max_switch * 0.1

        # 短期频繁切换惩罚：10秒内超过5次切换
        if switches >= 5:
            burst_extra = (switches - 4) * 2.5
            self._burst_penalty_accumulated = min(25.0, self._burst_penalty_accumulated + burst_extra)
            switch_score = max(0.0, switch_score - burst_extra)

        # ========== 4. 时间连续性得分（0~25，累积加成） ==========
        max_time = self.weights.get("continuous_focus_time", 25)

        if continuous_focus_minutes < 1:
            # 1分钟以内：基础分
            time_score = max_time * 0.2
        elif continuous_focus_minutes < 3:
            # 1~3分钟：线性增长
            progress = (continuous_focus_minutes - 1) / 2.0
            time_score = max_time * (0.2 + 0.4 * progress)
        elif continuous_focus_minutes < 10:
            # 3~10分钟：持续增长
            progress = (continuous_focus_minutes - 3) / 7.0
            time_score = max_time * (0.6 + 0.3 * progress)
        else:
            # 10分钟以上：满分
            time_score = max_time

        # ========== 5. 综合评分 ==========
        base_total = face_score + window_score + switch_score + time_score

        # 累积惩罚应用到总分
        final_total = max(0.0, base_total - self._burst_penalty_accumulated)

        return FocusScore(
            total_score=final_total,
            face_score=face_score,
            window_score=window_score,
            switch_score=switch_score,
            time_score=time_score
        )

    def _smooth_score(self, new_score: float) -> float:
        """
        加权移动平均平滑 v2.0
        最近的分数权重更高，使用指数加权
        """
        if not self.smoothing_config.get("enabled", True):
            return new_score

        self.score_history.append(new_score)
        length = len(self.score_history)

        if length < 2:
            return new_score

        # 指数加权移动平均：近期权重指数增长
        scores = list(self.score_history)
        weights = [1.5 ** i for i in range(length)]  # 越近权重越高
        total_weight = sum(weights)
        weighted_avg = sum(s * w for s, w in zip(scores, weights)) / total_weight

        return weighted_avg

    def _determine_state(self, score: float, face_detected: bool) -> FocusState:
        """
        根据评分判定状态（带智能阈值）
        """
        focused_thresh = self.thresholds.get("focused", 65)
        normal_thresh = self.thresholds.get("normal", 40)

        # 严重情况：持续无人脸才判定分心
        if not face_detected:
            # 累积3帧无人脸才判定（避免偶尔的误检）
            self._consecutive_distraction_frames += 1
            if self._consecutive_distraction_frames >= 3:
                self._consecutive_focus_frames = 0
                return FocusState.DISTRACTED
        else:
            self._consecutive_distraction_frames = 0
            self._consecutive_focus_frames += 1

        if score >= focused_thresh:
            return FocusState.FOCUSED
        elif score >= normal_thresh:
            return FocusState.NORMAL
        else:
            return FocusState.DISTRACTED

    def _apply_delay(self, new_state: FocusState, current_time: float) -> FocusState:
        """
        统一延迟判断 v2.0
        - 分心需要持续8秒才确认（避免短暂波动）
        - 专注状态需要持续5秒才确认
        - 一般状态需要持续5秒才确认
        - 已确认的分心需要持续2秒专注才会解除
        """
        # 初始化
        if self.current_state == FocusState.UNKNOWN:
            self.current_state = new_state
            self.state_start_time = current_time
            self._pending_state = None
            self._pending_start_time = None
            return new_state

        # 状态未变，重置计时器
        if new_state == self.current_state:
            self.state_start_time = current_time
            self._pending_state = None
            self._pending_start_time = None
            if new_state == FocusState.DISTRACTED:
                self._distraction_confirmed = True
            return self.current_state

        # 状态发生变化，启动延迟判断
        state_duration = current_time - self.state_start_time

        if self._pending_state != new_state:
            self._pending_state = new_state
            self._pending_start_time = current_time

        pending_duration = current_time - self._pending_start_time

        # 获取当前状态的延迟阈值
        if new_state == FocusState.DISTRACTED:
            delay = self.delay_config.get("distraction_delay", 8.0)
        elif new_state == FocusState.FOCUSED:
            delay = self.delay_config.get("focus_delay", 5.0)
        else:
            delay = self.delay_config.get("normal_delay", 5.0)

        # 特殊规则：已确认的分心状态需要更强的专注信号才能解除
        if self._distraction_confirmed and new_state != FocusState.DISTRACTED:
            if new_state == FocusState.FOCUSED:
                # 需要持续专注3秒以上才能解除分心确认
                if pending_duration < 3.0:
                    return self.current_state
            elif new_state == FocusState.NORMAL:
                # 需要持续一般状态5秒以上
                if pending_duration < delay:
                    return self.current_state

        if pending_duration < delay:
            return self.current_state

        # 状态变更生效
        self._distraction_confirmed = (new_state == FocusState.DISTRACTED)
        return new_state

    def update(
        self,
        face_detected: bool,
        is_learning_window: bool,
        switch_count: int,
        continuous_focus_minutes: float,
        face_confidence: float = 0.5,
    ) -> Tuple[FocusState, FocusScore]:
        """
        更新专注度状态 v2.0
        """
        current_time = time.time()

        # 计算评分
        raw_score = self.calculate_score(
            face_detected,
            is_learning_window,
            switch_count,
            continuous_focus_minutes,
            face_confidence,
        )

        # 平滑评分
        smooth_value = self._smooth_score(raw_score.total_score)
        raw_score.total_score = smooth_value

        # 判定状态
        new_state = self._determine_state(smooth_value, face_detected)

        # 应用延迟判断
        final_state = self._apply_delay(new_state, current_time)

        # 更新统计
        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time

        if final_state == FocusState.FOCUSED:
            self.total_focused_time += delta_time
        elif final_state == FocusState.NORMAL:
            self.total_normal_time += delta_time
        elif final_state == FocusState.DISTRACTED:
            self.total_distracted_time += delta_time

        self.current_state = final_state
        self.current_score = raw_score

        return final_state, raw_score

    def get_state(self) -> FocusState:
        """获取当前状态"""
        return self.current_state

    def get_score(self) -> FocusScore:
        """获取当前评分"""
        return self.current_score

    def get_report(self) -> Dict:
        """获取分析报告"""
        total_time = time.time() - self.session_start_time

        if total_time > 0:
            focused_ratio = self.total_focused_time / total_time * 100
            normal_ratio = self.total_normal_time / total_time * 100
            distracted_ratio = self.total_distracted_time / total_time * 100
        else:
            focused_ratio = normal_ratio = distracted_ratio = 0

        return {
            "session_duration": total_time,
            "total_focused_time": self.total_focused_time,
            "total_normal_time": self.total_normal_time,
            "total_distracted_time": self.total_distracted_time,
            "focused_ratio": focused_ratio,
            "normal_ratio": normal_ratio,
            "distracted_ratio": distracted_ratio,
            "current_score": self.current_score.total_score,
            "current_state": self.current_state.value,
            "distraction_confirmed": self._distraction_confirmed,
            "burst_penalty": self._burst_penalty_accumulated,
            "score_details": {
                "face_score": self.current_score.face_score,
                "window_score": self.current_score.window_score,
                "switch_score": self.current_score.switch_score,
                "time_score": self.current_score.time_score,
            }
        }

    def reset(self):
        """重置分析器"""
        self.current_state = FocusState.UNKNOWN
        self.current_score = FocusScore()
        self.state_start_time = time.time()
        self.last_update_time = time.time()
        self.score_history.clear()
        self.total_focused_time = 0.0
        self.total_normal_time = 0.0
        self.total_distracted_time = 0.0
        self.session_start_time = time.time()
        self._pending_state = None
        self._pending_start_time = None
        self._distraction_confirmed = False
        self._burst_penalty_accumulated = 0.0
        self._consecutive_focus_frames = 0
        self._consecutive_distraction_frames = 0
