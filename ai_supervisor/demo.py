"""
AI监督系统演示程序（可视化版本）
用于独立运行和测试ai_supervisor模块，带实时摄像头显示
"""

import sys
import os
import time
import logging
import signal
import numpy as np
from datetime import datetime

# 添加父目录到路径，以便能导入 ai_supervisor 模块
_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def signal_handler(signum, frame):
    """处理Ctrl+C信号"""
    print("\n\n收到停止信号，正在退出...")
    cv2.destroyAllWindows()
    sys.exit(0)


# 注册信号处理器
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def draw_status(frame, state, score, window_title, face_rects=None):
    """在帧上绘制状态信息（支持中文）"""
    try:
        import cv2
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return frame

    height, width = frame.shape[:2]

    # 状态颜色 (BGR格式)
    colors = {
        "focused": (0, 255, 0),       # 绿色
        "normal": (0, 255, 255),      # 黄色
        "distracted": (0, 0, 255),    # 红色
        "unknown": (128, 128, 128)    # 灰色
    }

    state_names = {
        "focused": "专注",
        "normal": "一般",
        "distracted": "分心",
        "unknown": "未知"
    }

    color = colors.get(state, (128, 128, 128))
    state_name = state_names.get(state, "未知")

    # 绘制顶部状态栏
    cv2.rectangle(frame, (0, 0), (width, 60), color, -1)

    # 使用PIL绘制中文文字
    pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)

    # 尝试加载中文字体
    font_paths = [
        "C:/Windows/Fonts/msyh.ttc",      # 微软雅黑
        "C:/Windows/Fonts/simhei.ttf",    # 黑体
        "C:/Windows/Fonts/simsun.ttc",   # 宋体
        "C:/Windows/Fonts/simkai.ttf",   # 楷体
    ]
    font = None
    for path in font_paths:
        try:
            font = ImageFont.truetype(path, 30)
            break
        except:
            continue

    if font is None:
        font = ImageFont.load_default()

    # 绘制状态文字
    draw.text((10, 10), f"状态: {state_name}", fill=(255, 255, 255), font=font)

    # 绘制评分
    score_text = f"评分: {score:.0f}/100"
    draw.text((width - 260, 10), score_text, fill=(255, 255, 255), font=font)

    # 转换回OpenCV格式
    frame = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    # 绘制人脸检测框
    if face_rects:
        for (x, y, w, h) in face_rects:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    return frame


def format_duration(seconds: float) -> str:
    """格式化时长"""
    if seconds < 60:
        return f"{int(seconds)}秒"
    elif seconds < 3600:
        return f"{int(seconds//60)}分{int(seconds%60)}秒"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours}小时{minutes}分{secs}秒"


def run_visual_demo(duration_seconds: int = None):
    """
    运行可视化演示程序

    Args:
        duration_seconds: 运行时长（秒），None表示无限运行
    """
    try:
        import cv2
    except ImportError:
        print("错误: OpenCV未安装，无法运行可视化模式")
        print("请运行: pip install opencv-python-headless")
        return

    print("\n" + "=" * 60)
    print("AI学习专注度监测系统 - 可视化版本")
    print("=" * 60)
    print("\n说明:")
    print("  - 本程序会显示摄像头画面")
    print("  - 实时检测专注状态并显示在画面上")
    print("  - 按 'q' 键退出程序")
    print("  - 按 's' 键保存当前截图")
    if duration_seconds:
        print(f"  - 将运行 {duration_seconds} 秒后自动停止")
    else:
        print("  - 将持续运行直到用户退出 (Ctrl+C 或按 q)")
    print("\n" + "-" * 60)

    # 导入模块
    try:
        from ai_supervisor import Monitor
    except ImportError:
        print("错误: 无法导入ai_supervisor模块")
        return

    # 创建监控器
    monitor = Monitor()
    print("\n模块初始化完成")

    # 创建窗口（使用大窗口便于查看）
    window_name = "AI学习专注度监测"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 800, 600)

    # 添加点击关闭功能
    def on_mouse(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDBLCLK:
            print("\n双击窗口退出")
            return True
        return False

    cv2.setMouseCallback(window_name, on_mouse)

    # 开始监控
    monitor.start()

    start_time = time.time()
    last_update = time.time()
    update_interval = 0.1  # 视频帧更新间隔

    print("\n开始监控...摄像头窗口已打开")

    try:
        while True:
            current_time = time.time()

            # 检查窗口是否被用户关闭
            if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                print("\n窗口已关闭，退出程序")
                break

            # 获取摄像头帧
            frame = None
            if monitor.camera and monitor.camera.is_available():
                frame = monitor.camera.get_frame()

            # 如果没有帧，创建一个空白帧
            if frame is None:
                frame = np.zeros((480, 640, 3), np.uint8)
                cv2.putText(frame, "摄像头不可用",
                            (180, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            # 获取状态信息
            state = monitor.get_state()
            score = monitor.get_score()
            report = monitor.get_report()
            window_info = report.get("window_info")
            window_title = window_info.get("title", "Unknown") if window_info else "Unknown"

            # 获取人脸位置
            face_rects = monitor._get_face_rects() if hasattr(monitor, '_get_face_rects') else None

            # 绘制状态信息
            frame = draw_status(frame, state, score, window_title, face_rects)

            # 显示帧
            cv2.imshow(window_name, frame)

            # 处理键盘输入
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:  # q 或 ESC
                print("\n用户退出")
                break
            elif key == ord('s'):
                # 保存截图
                filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                cv2.imwrite(filename, frame)
                print(f"截图已保存: {filename}")

            # 检查运行时间
            if duration_seconds and current_time - start_time >= duration_seconds:
                break

            time.sleep(update_interval)

    except KeyboardInterrupt:
        print("\n\n用户中断，正在停止...")

    finally:
        # 停止监控
        monitor.stop()
        cv2.destroyAllWindows()

        # 输出最终报告
        print("\n" + "=" * 60)
        print("最终学习报告")
        print("=" * 60)

        report = monitor.get_report()

        print(f"会话总时长: {format_duration(report.get('session_duration', 0))}")
        print(f"\n状态时间分布:")
        print(f"  专注时间: {format_duration(report.get('total_focused_time', 0))} ({report.get('focused_ratio', 0):.1f}%)")
        print(f"  一般时间: {format_duration(report.get('total_normal_time', 0))} ({report.get('normal_ratio', 0):.1f}%)")
        print(f"  分心时间: {format_duration(report.get('total_distracted_time', 0))} ({report.get('distracted_ratio', 0):.1f}%)")

        print(f"\n评分详情:")
        score_details = report.get('score_details', {})
        print(f"  人脸检测: {score_details.get('face_score', 0):.1f}/25")
        print(f"  学习窗口: {score_details.get('window_score', 0):.1f}/30")
        print(f"  切换频率: {score_details.get('switch_score', 0):.1f}/20")
        print(f"  专注时间: {score_details.get('time_score', 0):.1f}/25")
        print(f"  总分: {report.get('current_score', 0):.1f}/100")

        print("=" * 60)
        print("\n感谢使用！继续保持专注学习\n")


def run_simple_test():
    """运行简单测试（不依赖摄像头）"""
    print("\n" + "=" * 60)
    print("AI监督系统 - 简单测试模式")
    print("=" * 60)

    try:
        from ai_supervisor import Monitor
    except ImportError as e:
        print("导入失败: {}".format(e))
        return

    monitor = Monitor()

    # 模拟一些数据来测试分析器
    print("\n测试专注度分析器...")

    # 每次测试前重置分析器，模拟真实场景
    test_cases = [
        # (人脸, 学习窗口, 切换次数, 连续专注时间(分钟), 预期状态)
        (True, True, 2, 30, "专注"),       # 高分专注
        (True, True, 5, 10, "专注"),       # 中高分专注
        (True, False, 2, 30, "一般"),     # 窗口不在学习
        (False, True, 2, 30, "分心"),     # 人脸检测失败
        (True, True, 20, 5, "一般"),       # 切换频繁但总分够一般
        (True, False, 15, 5, "分心"),      # 低分分心
        (False, False, 5, 1, "分心"),      # 全低分
    ]

    print("\n测试用例:")
    print("-" * 80)
    print(f"{'人脸':^8} {'学习窗口':^10} {'切换次数':^10} {'专注时间':^12} {'预期':^10}")
    print("-" * 80)

    results = []
    for face, window, switches, focus_time, expected in test_cases:
        # 每次测试前重置分析器（模拟新场景）
        monitor.analyzer.reset()
        # 模拟状态持续超过延迟阈值
        time.sleep(0.1)

        state, score = monitor.analyzer.update(face, window, switches, focus_time)
        actual = {"focused": "专注", "normal": "一般", "distracted": "分心"}.get(state.value, "未知")

        status = "[OK]" if expected == actual else "[X]"
        print(f"{face:^8} {window:^10} {switches:^10} {focus_time:^10}分钟 {actual:^8} {status}")
        results.append((expected, actual, status))

    print("-" * 80)

    passed = sum(1 for _, _, s in results if s == "[OK]")
    print(f"\n测试结果: {passed}/{len(results)} 通过")

    if passed == len(results):
        print("所有测试通过！专注度分析器工作正常")
    else:
        print("部分测试未通过，请检查分析器配置")

    # 测试行为检测器（如果可用）
    print("\n测试行为检测器...")
    try:
        behavior = monitor.behavior
        if behavior:
            window_info = behavior.get_current_window_info()
            print(f"当前窗口: {window_info}")
            print("行为检测器工作正常")
        else:
            print("行为检测器未初始化")
    except Exception as e:
        print(f"行为检测器测试失败: {e}")

    print("\n简单测试完成！")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AI学习专注度监测系统")
    parser.add_argument("-t", "--test", action="store_true", help="运行简单测试模式")
    parser.add_argument("-v", "--visual", action="store_true", help="运行可视化模式（显示摄像头）")
    parser.add_argument("-d", "--duration", type=int, default=None, help="运行时长（秒）")
    parser.add_argument("-o", "--original", action="store_true", help="运行原始模式（无视频窗口）")

    args = parser.parse_args()

    if args.test:
        run_simple_test()
    elif args.visual:
        run_visual_demo(duration_seconds=args.duration)
    elif args.original:
        run_demo(duration_seconds=args.duration)
    else:
        # 默认运行可视化模式
        run_visual_demo(duration_seconds=args.duration)
