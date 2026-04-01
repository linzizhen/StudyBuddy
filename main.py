"""
StudyBuddy 主程序入口
命令行界面，整合所有功能模块
"""

from buddy import Buddy
from ai_helper import ask_ai
from timer import StudyTimer
from config import EMOJIS, DAILY_GOAL_MINUTES


def show_status(buddy, timer, brief=False):
    """显示状态（brief=True 时只显示简短信息）"""
    if brief:
        print(f"  [{buddy.get_emoji()}] 已学：{timer.get_current_duration():.1f}min | ", end="")
    else:
        print(f"\n📊 当前状态：")
        print(f"  情绪：{buddy.get_emoji()} ({buddy.get_emotion()})")
        print(f"  学习时长：{timer.get_current_duration():.1f} / {timer._target_minutes} 分钟")
        print(f"  剩余时长：{timer.get_remaining():.1f} 分钟")
        status = "🟢 学习中" if timer._is_running else ("🟡 已暂停" if timer._pause_time else "⚫ 未开始")
        print(f"  状态：{status}")
        
        # 显示任务统计
        task_stats = buddy.task_manager.get_stats()
        print(f"\n📋 任务：{task_stats['completed']}/{task_stats['total']} 完成")
        
        # 显示学习日历统计
        calendar_stats = buddy.get_calendar_stats()
        print(f"📅 今日学习：{calendar_stats['today_minutes']} / {DAILY_GOAL_MINUTES} 分钟")


def show_menu():
    """显示简洁菜单"""
    print("\n┌──────────────────────────────┐")
    print("│  1.提问  2.学习  3.任务      │")
    print("│  4.日历  5.暂停  6.状态  7.退│")
    print("└──────────────────────────────┘")


def task_menu(buddy):
    """任务管理子菜单"""
    while True:
        print("\n📋 任务管理")
        print("  1. 查看任务  2. 添加任务")
        print("  3. 完成任务  4. 删除任务")
        print("  5. 返回主菜单")
        
        choice = input("➤ ").strip()
        
        if choice == "1":
            tasks = buddy.task_manager.get_all_tasks()
            if not tasks:
                print("  暂无任务")
            else:
                for t in tasks:
                    status = "✅" if t['completed'] else "⬜"
                    priority = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(t['priority'], "⚪")
                    print(f"  [{t['id']}] {priority} {status} {t['title']} ({t['category']})")
                    
        elif choice == "2":
            title = input("  任务标题：").strip()
            if not title:
                print("  ⚠️  标题不能为空")
                continue
            
            print("  优先级：1.高 2.中 3.低")
            p_choice = input("➤ ").strip()
            priority = {"1": "high", "2": "medium", "3": "low"}.get(p_choice, "medium")
            
            category = input("  分类 (学习/工作/生活): ").strip() or "学习"
            
            buddy.task_manager.add_task(title=title, priority=priority, category=category)
            print("  ✅ 任务已添加")
            
        elif choice == "3":
            task_id = input("  任务 ID: ").strip()
            try:
                task_id = int(task_id)
                task = buddy.task_manager.complete_task(task_id)
                if task:
                    print(f"  ✅ 完成任务：{task['title']}")
                    print(f"  {buddy.get_emoji()} {buddy.get_emotion_description()}")
                else:
                    print("  ⚠️  任务不存在")
            except ValueError:
                print("  ⚠️  请输入有效的任务 ID")
                
        elif choice == "4":
            task_id = input("  任务 ID: ").strip()
            try:
                task_id = int(task_id)
                if buddy.task_manager.delete_task(task_id):
                    print("  ✅ 任务已删除")
                else:
                    print("  ⚠️  任务不存在")
            except ValueError:
                print("  ⚠️  请输入有效的任务 ID")
                
        elif choice == "5":
            break
            
        else:
            print("  ⚠️  无效输入")


def calendar_menu(buddy):
    """学习日历子菜单"""
    while True:
        print("\n📅 学习日历")
        print("  1. 查看统计  2. 记录学习")
        print("  3. 查看历史  4. 返回主菜单")
        
        choice = input("➤ ").strip()
        
        if choice == "1":
            stats = buddy.get_calendar_stats()
            print(f"  今日学习：{stats['today_minutes']} 分钟")
            print(f"  本周学习：{stats['week_minutes']} 分钟")
            print(f"  总学习天数：{stats['total_days']} 天")
            print(f"  连续学习：{stats['streak']} 天")
            
        elif choice == "2":
            duration = input("  学习时长 (分钟): ").strip()
            try:
                duration = int(duration)
                subject = input("  学习科目：").strip() or "学习"
                buddy.log_study_session(duration)
                print(f"  ✅ 已记录 {duration} 分钟")
                today_duration = buddy.study_calendar.get_today_duration()
                print(f"  今日累计：{today_duration} 分钟")
                if today_duration >= DAILY_GOAL_MINUTES:
                    print(f"  🎉 {buddy.get_emoji()} 达到每日目标！")
            except ValueError:
                print("  ⚠️  请输入有效的数字")
                
        elif choice == "3":
            days = input("  查看最近几天 (默认 7): ").strip()
            try:
                days = int(days) if days else 7
                history = buddy.study_calendar.get_history(days)
                if not history:
                    print("  暂无学习记录")
                else:
                    for record in history:
                        if record['minutes'] > 0:
                            print(f"  {record['date']}: {record['minutes']} 分钟")
            except ValueError:
                print("  ⚠️  请输入有效的数字")
                
        elif choice == "4":
            break
            
        else:
            print("  ⚠️  无效输入")


def main():
    """主函数"""
    # 初始化组件
    buddy = Buddy()
    timer = StudyTimer()
    
    print("\n👋 你好！我是 StudyBuddy，你的学习搭子！")
    show_status(buddy, timer, brief=True)
    show_menu()
    
    while True:
        try:
            choice = input("➤ ").strip()
            
            if choice == "1":
                # 提问功能
                question = input("你的问题：").strip()
                if not question:
                    print("⚠️  问题不能为空")
                    continue
                
                buddy.update_by_action("ask")
                print(f"{buddy.get_emoji()} 思考中...")
                answer = ask_ai(question)
                print(f"💬 {answer}")
                buddy.update_by_action("answer_received")
                
            elif choice == "2":
                # 开始学习
                if timer.start():
                    buddy.update_by_action("study_start")
                    print(f"✅ {buddy.get_emoji()} 开始学习！目标{timer._target_minutes}分钟")
                else:
                    print("⚠️  已在计时中")
                
                if timer.check_finish():
                    buddy.update_by_action("study_finish")
                    print(f"\n🎉 完成！{buddy.get_emoji()} 你真棒！")
                    # 记录到日历
                    buddy.log_study_session(timer.get_current_duration())
                
            elif choice == "3":
                # 任务管理
                task_menu(buddy)
                show_status(buddy, timer, brief=True)
                
            elif choice == "4":
                # 学习日历
                calendar_menu(buddy)
                show_status(buddy, timer, brief=True)
                
            elif choice == "5":
                # 暂停/继续
                if timer._is_running:
                    timer.pause()
                    print("⏸️  已暂停")
                elif timer._pause_time:
                    timer.resume()
                    print("▶️  继续")
                else:
                    print("⚠️  先开始学习")
                
            elif choice == "6":
                # 查看状态
                show_status(buddy, timer, brief=False)
                
            elif choice == "7":
                # 退出
                print(f"\n👋 {buddy.get_emoji()} 再见！加油！\n")
                break
                
            else:
                print("⚠️  请输入 1-7")
            
            # 显示简短状态和菜单
            show_status(buddy, timer, brief=True)
            show_menu()
                
        except KeyboardInterrupt:
            print(f"\n👋 {buddy.get_emoji()} 再见！\n")
            break
        except Exception as e:
            print(f"⚠️  错误：{e}")
            show_status(buddy, timer, brief=True)
            show_menu()


if __name__ == "__main__":
    main()