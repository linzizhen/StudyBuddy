"""
摄像头检测模块
负责调用摄像头并检测人脸
"""

import numpy as np
import logging
import time
import os
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# 延迟导入cv2
cv2 = None


def _get_cv2():
    """延迟加载cv2"""
    global cv2
    if cv2 is None:
        try:
            import cv2 as _cv2
            cv2 = _cv2
        except ImportError:
            logger.warning("OpenCV未安装，人脸检测功能将受限")
    return cv2


class CameraDetector:
    """摄像头人脸检测类"""
    
    def __init__(self, camera_index: int = None):
        """
        初始化摄像头检测器
        
        Args:
            camera_index: 摄像头索引，默认从配置读取
        """
        from .config import CAMERA_CONFIG, FACE_DETECTION_CONFIG
        
        self.camera_index = camera_index if camera_index is not None else CAMERA_CONFIG["camera_index"]
        self.cap: Optional[object] = None
        self.face_cascade: Optional[object] = None
        
        # 状态计数器
        self.consecutive_no_face = 0
        self.consecutive_has_face = 0
        
        # 上次检测时间
        self.last_detection_time = time.time()
        self.last_frame_time = time.time()
        
        # 检测结果缓存
        self._cached_result = None
        self._cache_valid_duration = 0.2  # 缓存有效时间（秒）
        
        self._init_face_detector()
    
    def _init_face_detector(self):
        """初始化人脸检测器"""
        try:
            _cv2 = _get_cv2()
            if _cv2 is None:
                self.face_cascade = None
                return

            CAMERA_CONFIG_local = {
                "haarcascade_path": None,
                "frame_width": 640,
                "frame_height": 480,
                "fps": 30,
            }

            # 尝试使用OpenCV内置的haarcascade
            cascade_path = CAMERA_CONFIG_local.get("haarcascade_path")

            if cascade_path and os.path.exists(cascade_path):
                self.face_cascade = _cv2.CascadeClassifier(cascade_path)
            else:
                self.face_cascade = _cv2.CascadeClassifier(
                    _cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                )

            if self.face_cascade.empty():
                logger.warning("无法加载人脸检测模型，使用简化检测")
                self.face_cascade = None

            # 人脸检测配置（无论cascade是否成功都设置）
            self.face_detection_config = {
                "min_size": (20, 20),
                "scale_factor": 1.05,
                "min_neighbors": 3,
            }

        except Exception as e:
            logger.warning(f"人脸检测器初始化失败: {e}")
            self.face_cascade = None
    
    def open(self) -> bool:
        """
        打开摄像头
        
        Returns:
            是否成功打开
        """
        try:
            _cv2 = _get_cv2()
            if _cv2 is None:
                logger.error("OpenCV未安装，无法打开摄像头")
                return False
            
            CAMERA_CONFIG_local = {
                "frame_width": 640,
                "frame_height": 480,
                "fps": 30,
                "camera_index": self.camera_index,
            }
            
            if self.cap is not None:
                self.release()
            
            self.cap = _cv2.VideoCapture(self.camera_index)
            
            if not self.cap.isOpened():
                logger.error(f"无法打开摄像头 {self.camera_index}")
                return False
            
            # 设置分辨率
            width = CAMERA_CONFIG_local["frame_width"]
            height = CAMERA_CONFIG_local["frame_height"]
            self.cap.set(_cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(_cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.cap.set(_cv2.CAP_PROP_FPS, CAMERA_CONFIG_local["fps"])
            
            logger.info(f"摄像头 {self.camera_index} 打开成功")
            return True
            
        except Exception as e:
            logger.error(f"打开摄像头失败: {e}")
            return False
    
    def release(self):
        """释放摄像头资源"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            logger.info("摄像头已关闭")
    
    def read_frame(self) -> Optional[np.ndarray]:
        """
        读取一帧图像
        
        Returns:
            图像数组，失败返回None
        """
        if self.cap is None or not self.cap.isOpened():
            return None
        
        _cv2 = _get_cv2()
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        self.last_frame_time = time.time()
        return frame
    
    def detect_face(self, frame: np.ndarray) -> Tuple[bool, int]:
        """
        检测人脸，同时返回置信度

        Args:
            frame: 图像数组

        Returns:
            (是否检测到人脸, 检测到的人脸数量)
        """
        if frame is None:
            return False, 0

        _cv2 = _get_cv2()
        if self.face_cascade is None or _cv2 is None:
            gray = _cv2.cvtColor(frame, _cv2.COLOR_BGR2GRAY) if _cv2 else None
            if gray is not None:
                brightness = np.mean(gray)
                has_face = 40 < brightness < 220
                return has_face, 1 if has_face else 0
            return True, 1  # 默认认为有人

        try:
            config = getattr(self, 'face_detection_config', None)
            if config is None:
                config = {
                    "min_face_size": (20, 20),
                    "scale_factor": 1.05,
                    "min_neighbors": 3,
                }
            gray = _cv2.cvtColor(frame, _cv2.COLOR_BGR2GRAY)

            min_size = config["min_size"]
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=config["scale_factor"],
                minNeighbors=config["min_neighbors"],
                minSize=min_size
            )

            return len(faces) > 0, len(faces)

        except Exception as e:
            logger.error(f"人脸检测出错: {e}")
            return False, 0

    def detect_face_with_confidence(self, frame: np.ndarray) -> Tuple[bool, int, float]:
        """
        检测人脸并返回置信度 v2.0

        Args:
            frame: 图像数组

        Returns:
            (是否检测到人脸, 人脸数量, 置信度 0.0~1.0)
        """
        if frame is None:
            return False, 0, 0.0

        _cv2 = _get_cv2()
        if self.face_cascade is None or _cv2 is None:
            gray = _cv2.cvtColor(frame, _cv2.COLOR_BGR2GRAY) if _cv2 else None
            if gray is not None:
                brightness = np.mean(gray)
                has_face = 40 < brightness < 220
                confidence = 0.5 if has_face else 0.3
                return has_face, 1 if has_face else 0, confidence
            return True, 1, 0.5

        try:
            config = getattr(self, 'face_detection_config', None)
            if config is None:
                config = {
                    "min_face_size": (20, 20),
                    "scale_factor": 1.05,
                    "min_neighbors": 3,
                }
            gray = _cv2.cvtColor(frame, _cv2.COLOR_BGR2GRAY)

            min_size = config["min_size"]
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=config["scale_factor"],
                minNeighbors=config["min_neighbors"],
                minSize=min_size
            )

            if len(faces) == 0:
                return False, 0, 0.0

            # 计算置信度：基于人脸大小和亮度
            # 人脸越大（占画面比例越大），置信度越高
            h, w = frame.shape[:2]
            avg_face_area = 0.0
            for (x, y, fw, fh) in faces:
                avg_face_area += fw * fh
            avg_face_area /= len(faces)
            area_ratio = avg_face_area / (w * h)
            # 假设人脸占画面5%以上为高置信度
            size_conf = min(1.0, area_ratio / 0.05)

            # 亮度置信度：中等亮度最佳
            brightness = np.mean(gray)
            brightness_conf = 1.0 - abs(brightness - 128) / 128

            # 综合置信度
            confidence = 0.5 * size_conf + 0.5 * brightness_conf

            return True, len(faces), min(1.0, confidence)

        except Exception as e:
            logger.error(f"人脸检测出错: {e}")
            return False, 0, 0.0
    
    def is_person_present(self, force_refresh: bool = False) -> bool:
        """
        判断是否有人在场（带状态平滑）
        
        Args:
            force_refresh: 是否强制刷新
            
        Returns:
            是否有人在场
        """
        current_time = time.time()
        
        # 检查缓存
        if (not force_refresh and self._cached_result is not None and
            current_time - self.last_detection_time < self._cache_valid_duration):
            return self._cached_result
        
        # 读取帧
        frame = self.read_frame()
        if frame is None:
            # 无法读取帧时，保守处理
            return True
        
        # 检测人脸
        has_face, face_count = self.detect_face(frame)

        # 更新状态计数器
        if has_face:
            self.consecutive_has_face += 1
            self.consecutive_no_face = 0
        else:
            self.consecutive_no_face += 1
            self.consecutive_has_face = 0

        # 阈值判断
        present_threshold = 2  # 连续2帧有人脸即判定在场
        missing_threshold = 5   # 连续5帧无人脸才判定离开

        if self.consecutive_has_face >= present_threshold:
            result = True
        elif self.consecutive_no_face >= missing_threshold:
            result = False
        else:
            # 使用最近一次检测结果
            result = has_face
        
        # 更新缓存
        self._cached_result = result
        self.last_detection_time = current_time
        
        return result
    
    def get_face_count(self) -> int:
        """获取当前帧检测到的人脸数量"""
        frame = self.read_frame()
        if frame is None:
            return 0
        
        _, count = self.detect_face(frame)
        return count
    
    def get_frame(self) -> Optional[np.ndarray]:
        """
        获取当前帧（用于显示）

        Returns:
            原始帧图像
        """
        if self.cap is None or not self.cap.isOpened():
            return None

        _cv2 = _get_cv2()
        if _cv2 is None:
            return None

        ret, frame = self.cap.read()
        if not ret:
            return None

        return frame

    def is_available(self) -> bool:
        """检查摄像头是否可用"""
        if self.cap is None:
            return False
        return self.cap.isOpened()

    def __enter__(self):
        """上下文管理器入口"""
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.release()
