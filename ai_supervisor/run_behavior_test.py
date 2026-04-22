"""快速运行脚本：测试 BehaviorDetector"""
import time
import sys
sys.path.insert(0, "d:/code/ai_monitor")

from ai_monitor.behavior import BehaviorDetector

detector = BehaviorDetector()
print("[行为检测器初始化完成]")
print(f"白名单应用: {detector.learning_apps[:5]}...")
print(f"黑名单应用: {detector.distraction_apps[:5]}...")

# 模拟3轮评估，观察平滑效果
print("\n=== 模拟3轮评估 ===")
for i in range(3):
    result = detector.evaluate_focus(face_state="focused")
    exp = detector.explain_state(result)
    print(f"\n--- 第{i+1}轮 ---")
    print(f"状态: {result.state}  分数: {result.score}")
    details = result.details
    print(f"原始分: {details['raw_score']}  平滑分: {details['smoothed_score']}  历史: {details['score_history_count']}条")
    print(f"窗口分: {details['window_score']}  人脸分: {details['face_score']}  切换分: {details['switch_score']}  学习时间分: {details['study_time_score']}")
    print(f"总结: {exp.summary}")
    if exp.factors:
        for f in exp.factors:
            print(f"  因素: {f}")
    time.sleep(0.5)

# 测试 get_window_status
print("\n=== get_window_status ===")
status = detector.get_window_status()
for k, v in status.items():
    if k != "raw_window":
        print(f"  {k}: {v}")

print("[运行完成]")

# ====== 模拟分心窗口，观察提醒触发 ======
print("\n" + "=" * 50)
print("模拟分心：连续6秒低于阈值，观察延迟判断和提醒")
print("=" * 50)

# 通过模拟窗口来触发分心（手动注入一个非学习窗口）
detector.current_window = detector._get_foreground_window()  # 先恢复真实窗口

# 注入一个B站窗口模拟分心
class FakeWindow:
    title = "bilibili - 直播中心"
    process_name = "bilibili.exe"
    timestamp = time.time()

detector.current_window = FakeWindow()
detector._study_start_time = None  # 清空学习时间
detector._score_history.clear()    # 清空历史

print(f"注入分心窗口: {detector.current_window.title}")
print(f"当前是否分心软件: {detector._is_distraction_related(detector.current_window)}")

for i in range(7):
    result = detector.evaluate_focus(face_state="focused")
    exp = detector.explain_state(result)
    conf = "已确认" if exp.is_distraction_confirmed else "未确认"
    print(f"\n  第{i+1}次  状态={result.state}  分数={result.score}  延迟={conf}")
    print(f"  raw={result.details['raw_score']}  smooth={result.details['smoothed_score']}  hist={result.details['score_history_count']}条")
    if exp.factors:
        for f in exp.factors:
            print(f"  -> {f}")
    time.sleep(1)

print("\n[分心模拟结束]")

