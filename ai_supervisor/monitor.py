"""
监控器主模块
整合所有检测和分析模块，提供统一的监控接口
"""

import time
import logging
import threading
from typing import Optional, Dict
from enum import Enum

from .camera import CameraDetector
from .behavior import BehaviorDetector
from .analyzer import FocusAnalyzer, FocusState
from .notifier import Notifier
from .config import TIME_ANALYSIS_CONFIG, SYSTEM_CONFIG
from typing import Tuple

logger = logging.getLogger(__name__)


class MonitorStatus(Enum):
    """监控器状态"""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"


class Monitor:
    """
    学习专注度监测器
    
    主要功能：
    1. 整合摄像头检测和行为检测
    2. 综合分析专注度评分
    3. 输出状态和报告
    4. 发送提醒
    """
    
    def __init__(self, config: Dict = None):
        """
        初始化监控器
        
        Args:
            config: 自定义配置（可选）
        """
        self.config = config or {}
        
        # 状态
        self.status = MonitorStatus.STOPPED
        
        # 各模块实例
        self.camera: Optional[CameraDetector] = None
        self.behavior: Optional[BehaviorDetector] = None
        self.analyzer: Optional[FocusAnalyzer] = None
        self.notifier: Optional[Notifier] = None
        
        # 运行时数据
        self.start_time: Optional[float] = None
        self.pause_time: Optional[float] = None
        self.total_paused_time = 0.0
        
        # 当前人脸位置（用于可视化）
        self.current_face_rects = None

        # 控制线程
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # 回调函数
        self._on_state_change_callback = None
        self._on_report_callback = None
        
        # 初始化各模块
        self._init_modules()
    
    def _init_modules(self):
        """初始化各检测模块"""
        try:
            # 初始化摄像头检测器
            self.camera = CameraDetector()
            logger.info("摄像头检测器初始化完成")
        except Exception as e:
            logger.warning(f"摄像头检测器初始化失败: {e}")
            self.camera = None
        
        try:
            # 初始化行为检测器
            self.behavior = BehaviorDetector()
            logger.info("行为检测器初始化完成")
        except Exception as e:
            logger.warning(f"行为检测器初始化失败: {e}")
            self.behavior = None
        
        # 初始化分析器
        self.analyzer = FocusAnalyzer()
        logger.info("专注度分析器初始化完成")
        
        # 初始化提醒器
        self.notifier = Notifier()
        logger.info("提醒器初始化完成")
    
    def set_callback(self, event: str, callback):
        """
        设置回调函数
        
        Args:
            event: 事件类型 ('state_change', 'report')
            callback: 回调函数
        """
        if event == "state_change":
            self._on_state_change_callback = callback
        elif event == "report":
            self._on_report_callback = callback
    
    def start(self):
        """开始监控"""
        if self.status == MonitorStatus.RUNNING:
            logger.warning("监控器已在运行中")
            return
        
        self.status = MonitorStatus.RUNNING
        self.start_time = time.time()
        self.total_paused_time = 0.0
        self._stop_event.clear()
        
        # 打开摄像头
        if self.camera and not self.camera.open():
            logger.warning("摄像头打开失败，将继续运行（人脸检测功能受限）")
        
        # 启动监控线程
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        
        logger.info("监控器已启动")
        print("\n专注度监测已启动，按 Ctrl+C 停止...\n")
    
    def stop(self):
        """停止监控"""
        if self.status == MonitorStatus.STOPPED:
            return
        
        self.status = MonitorStatus.STOPPED
        self._stop_event.set()
        
        # 等待线程结束
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=2)
        
        # 释放资源
        if self.camera:
            self.camera.release()
        
        logger.info("监控器已停止")
        print("\n监控已停止")
    
    def pause(self):
        """暂停监控"""
        if self.status != MonitorStatus.RUNNING:
            return
        
        self.status = MonitorStatus.PAUSED
        self.pause_time = time.time()
        logger.info("监控器已暂停")
    
    def resume(self):
        """恢复监控"""
        if self.status != MonitorStatus.PAUSED:
            return
        
        if self.pause_time:
            self.total_paused_time += time.time() - self.pause_time
        
        self.status = MonitorStatus.RUNNING
        self.pause_time = None
        logger.info("监控器已恢复")
    
    def _monitor_loop(self):
        """监控主循环 v2.0"""
        old_state = None
        last_report_time = time.time()
        report_interval = SYSTEM_CONFIG.get("save_report_interval", 300)

        while not self._stop_event.is_set():
            try:
                # 收集各模块数据（升级：获取人脸置信度）
                has_face, face_count, face_confidence = self._get_face_status_v2()
                is_learning_window = self._get_window_status()
                switch_count = self._get_switch_count()

                # 计算连续专注时间
                continuous_time = self._get_continuous_focus_time()
                continuous_minutes = continuous_time / 60

                # 更新分析器（传递人脸置信度）
                state, score = self.analyzer.update(
                    face_detected=has_face,
                    is_learning_window=is_learning_window,
                    switch_count=switch_count,
                    continuous_focus_minutes=continuous_minutes,
                    face_confidence=face_confidence,
                )

                # 状态变化处理
                if old_state != state.value:
                    if old_state is not None:
                        self.notifier.notify_state_change(old_state, state.value, score.total_score)
                    old_state = state.value

                    if self._on_state_change_callback:
                        self._on_state_change_callback(state.value, score.total_score)

                # 定时输出报告
                current_time = time.time()
                if current_time - last_report_time >= report_interval:
                    report = self.get_report()
                    self.notifier.notify_report(report)
                    last_report_time = current_time

                    if self._on_report_callback:
                        self._on_report_callback(report)

                time.sleep(0.5)

            except Exception as e:
                logger.error(f"监控循环出错: {e}")
                time.sleep(1)
    
    def _get_face_rects(self):
        """获取当前人脸位置列表"""
        return self.current_face_rects

    def get_camera_frame(self):
        """获取当前摄像头帧"""
        if self.camera is None:
            return None
        return self.camera.get_frame()

    def _get_face_status(self) -> Tuple[bool, any]:
        """获取人脸检测状态和人脸位置"""
        if self.camera is None:
            return True, None

        frame = self.camera.read_frame()
        if frame is None:
            return True, None

        has_face, face_count = self.camera.detect_face(frame)

        face_rects = None
        if self.camera.face_cascade is not None:
            try:
                _cv2 = self.camera._get_cv2()
                if _cv2 is not None:
                    gray = _cv2.cvtColor(frame, _cv2.COLOR_BGR2GRAY)
                    face_rects = self.camera.face_cascade.detectMultiScale(
                        gray, 1.3, 5,
                        minSize=(30, 30)
                    )
            except:
                pass

        return has_face, face_rects

    def _get_face_status_v2(self) -> Tuple[bool, any, float]:
        """
        获取人脸检测状态、人脸位置和置信度 v2.0

        Returns:
            (是否检测到人脸, 人脸数量或位置, 置信度 0.0~1.0)
        """
        if self.camera is None:
            return True, None, 0.5

        frame = self.camera.read_frame()
        if frame is None:
            return True, None, 0.5

        has_face, face_count, confidence = self.camera.detect_face_with_confidence(frame)

        face_rects = None
        if has_face and self.camera.face_cascade is not None:
            try:
                _cv2 = self.camera._get_cv2()
                if _cv2 is not None:
                    gray = _cv2.cvtColor(frame, _cv2.COLOR_BGR2GRAY)
                    face_rects = self.camera.face_cascade.detectMultiScale(
                        gray, 1.3, 5,
                        minSize=(30, 30)
                    )
            except:
                pass

        return has_face, face_rects, confidence
    
    def _get_window_status(self) -> bool:
        """获取窗口状态"""
        if self.behavior is None:
            return True  # 行为检测不可用时保守处理
        return self.behavior.is_learning_window()
    
    def _get_switch_count(self) -> int:
        """获取切换次数"""
        if self.behavior is None:
            return 0
        return self.behavior.get_switch_count()
    
    def _get_continuous_focus_time(self) -> float:
        """获取连续专注时间"""
        if self.start_time is None:
            return 0
        return time.time() - self.start_time - self.total_paused_time
    
    def get_state(self) -> str:
        """
        获取当前专注状态
        
        Returns:
            状态字符串：'focused', 'normal', 'distracted', 'unknown'
        """
        if self.analyzer is None:
            return "unknown"
        return self.analyzer.get_state().value
    
    def get_score(self) -> float:
        """
        获取当前专注度评分
        
        Returns:
            评分（0-100）
        """
        if self.analyzer is None:
            return 0
        return self.analyzer.get_score().total_score
    
    def get_report(self) -> Dict:
        """
        获取学习报告
        
        Returns:
            报告字典
        """
        if self.analyzer is None:
            return {}
        
        report = self.analyzer.get_report()
        
        # 添加额外信息
        report["window_info"] = self._get_window_info()
        report["face_detected"] = self._get_face_status()
        report["switch_frequency"] = self._get_switch_count()
        
        return report
    
    def _get_window_info(self) -> Optional[Dict]:
        """获取窗口信息"""
        if self.behavior is None:
            return None
        return self.behavior.get_current_window_info()
    
    def is_running(self) -> bool:
        """检查监控器是否在运行"""
        return self.status == MonitorStatus.RUNNING
    
    def get_status(self) -> str:
        """获取监控器状态"""
        return self.status.value
    
    def __enter__(self):
        """上下文管理器入口"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.stop()
