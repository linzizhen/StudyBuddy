"""
StudyPal 搭子工具系统
参考扣子（Coze）智能体架构：工具 = 智能体的技能插件

核心设计：
1. 工具注册表：所有可用工具的元数据
2. 工具执行器：根据 AI 调用执行具体操作
3. 工具上下文注入：将可用工具传给 AI 作为参考

工具格式（参考扣子）：
{
    "name": "工具名",
    "description": "何时使用",
    "parameters": {...}
}
"""

import json
import re
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime


# ========== 工具定义 ==========

class Tool:
    """工具基类"""

    name: str = ""
    description: str = ""
    parameters: Dict[str, Any] = {}

    def execute(self, params: Dict[str, Any], buddy_context: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError


class StudyTimerTool(Tool):
    """学习计时器工具"""
    name = "study_timer"
    description = "当用户想要开始学习、暂停休息、或结束学习时使用。返回今日学习统计。参数 action: start(开始)/stop(暂停)/resume(继续)"
    parameters = {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["start", "stop", "resume"], "description": "计时动作"}
        },
        "required": ["action"]
    }

    def execute(self, params: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
        action = params.get("action", "start")
        study_tracker = ctx.get("study_tracker")
        if not study_tracker:
            return {"success": False, "message": "无法访问学习追踪器"}

        if action == "start":
            study_tracker.start_session("focus")
            return {"success": True, "message": "学习计时开始！专注模式启动~"}
        elif action == "stop":
            study_tracker.end_session()
            stats = study_tracker.get_today_stats()
            return {
                "success": True,
                "message": f"本次学习结束！今日已学习 {stats.get('total_minutes', 0)} 分钟",
                "stats": stats
            }
        elif action == "resume":
            study_tracker.start_session("focus")
            return {"success": True, "message": "继续学习中~"}


class GetStudyStatsTool(Tool):
    """获取学习统计"""
    name = "get_study_stats"
    description = "当用户问今天/本周学习了多久、有没有偷懒、或者想要了解学习进度时使用。无参数。"
    parameters = {"type": "object", "properties": {}}

    def execute(self, params: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
        study_tracker = ctx.get("study_tracker")
        if not study_tracker:
            return {"success": False, "message": "无法访问学习追踪器"}

        stats = study_tracker.get_today_stats()
        return {
            "success": True,
            "stats": stats,
            "message": f"今日学习 {stats.get('total_minutes', 0)} 分钟，完成 {stats.get('sessions_count', 0)} 个番茄钟"
        }


class TaskTool(Tool):
    """任务管理工具"""
    name = "manage_task"
    description = "当用户想要添加任务、标记完成、查看待办时使用。参数 action: add(添加)/done(完成)/list(列表)"
    parameters = {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["add", "done", "list"]},
            "task": {"type": "string", "description": "任务内容（add时必填）"},
            "subject": {"type": "string", "description": "科目（可选）"}
        },
        "required": ["action"]
    }

    def execute(self, params: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
        action = params.get("action")
        task = params.get("task", "").strip()
        subject = params.get("subject", "")

        task_manager = ctx.get("task_manager")
        if not task_manager:
            return {"success": False, "message": "无法访问任务管理器"}

        if action == "add":
            if not task:
                return {"success": False, "message": "任务内容不能为空"}
            task_id = task_manager.add_task(task, subject=subject)
            return {"success": True, "message": f"任务「{task}」已添加！加油~", "task_id": task_id}

        elif action == "done":
            # 查找最近添加的任务
            tasks = task_manager.get_tasks()
            pending = [t for t in tasks if not t.get("completed")]
            if not pending:
                return {"success": True, "message": "没有待完成的任务呀~"}
            done = pending[0]
            task_manager.toggle_task(done.get("id"))
            return {"success": True, "message": f"「{done.get('title')}」完成！太棒了！", "task": done}

        elif action == "list":
            tasks = task_manager.get_tasks()
            pending = [f"- {t.get('title')}" for t in tasks if not t.get("completed")]
            if not pending:
                return {"success": True, "message": "目前没有待办任务，很棒！"}
            return {"success": True, "message": "当前待办：\n" + "\n".join(pending), "tasks": pending}

        return {"success": False, "message": "未知操作"}


class CheckMilestoneTool(Tool):
    """里程碑检查工具"""
    name = "check_milestone"
    description = "当用户完成重要学习目标、连续学习多天、或达到某个里程碑时使用，检查是否有成就可以庆祝。"
    parameters = {"type": "object", "properties": {}}

    def execute(self, params: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
        study_tracker = ctx.get("study_tracker")
        if not study_tracker:
            return {"success": False, "message": "无法访问学习追踪器"}

        streak = study_tracker.get_streak_days()
        milestones = [3, 7, 14, 30, 100]

        # 检查是否达到新里程碑
        reached = [m for m in milestones if m <= streak]
        next_milestone = next((m for m in milestones if m > streak), None)

        return {
            "success": True,
            "streak": streak,
            "reached_milestones": reached,
            "next_milestone": next_milestone,
            "message": f"连续学习 {streak} 天！" + (f"距离下一个里程碑 {next_milestone} 天，加油！" if next_milestone else "你是最棒的！")
        }


class RecordEmotionTool(Tool):
    """情绪记录工具"""
    name = "record_emotion"
    description = "当用户表达情绪、心情不好、很开心、或者搭子想要确认用户感受时使用。参数 emotion: happy/sad/worried/excited/sleepy/idle"
    parameters = {
        "type": "object",
        "properties": {
            "emotion": {"type": "string", "description": "情绪类型"},
            "note": {"type": "string", "description": "心情备注（可选）"}
        },
        "required": ["emotion"]
    }

    def execute(self, params: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
        emotion = params.get("emotion", "idle")
        note = params.get("note", "")

        emotion_tracker = ctx.get("emotion_tracker")
        if emotion_tracker:
            emotion_tracker.track(emotion, note=note)

        return {"success": True, "message": f"记录了你的心情：{emotion}。" + (f"你说：{note}" if note else "有什么想说的可以告诉我~")}


class GetBuddyStatusTool(Tool):
    """搭子状态工具"""
    name = "get_buddy_status"
    description = "获取搭子当前状态，包括情绪、最近学习情况、待办任务数等。无参数。"
    parameters = {"type": "object", "properties": {}}

    def execute(self, params: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
        buddy = ctx.get("buddy")
        study_tracker = ctx.get("study_tracker")
        task_manager = ctx.get("task_manager")

        status = {}
        if buddy:
            status["emotion"] = buddy.get_emotion()
            status["emoji"] = buddy.get_emoji()
        if study_tracker:
            status["today_study_minutes"] = study_tracker.get_today_stats().get("total_minutes", 0)
            status["streak_days"] = study_tracker.get_streak_days()
        if task_manager:
            tasks = task_manager.get_tasks()
            status["pending_tasks"] = len([t for t in tasks if not t.get("completed")])

        return {"success": True, "status": status}


class SearchMemoryTool(Tool):
    """记忆搜索工具"""
    name = "search_memory"
    description = "当用户提到之前聊过的话题、记忆中的事件、或者问起之前发生过什么事时使用。"
    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "搜索关键词"}
        },
        "required": ["query"]
    }

    def execute(self, params: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
        query = params.get("query", "")
        memory = ctx.get("memory")

        if not memory:
            return {"success": False, "message": "无法访问记忆系统"}

        results = memory.smart_recall(query, limit=3)
        if not results:
            return {"success": True, "message": f"关于「{query}」，我暂时没有记忆呢~", "results": []}

        parts = [f"想起一件事：{r['data'].get('summary', '')}" for r in results]
        return {
            "success": True,
            "message": "想起一些相关记忆：\n" + "\n".join(parts),
            "results": results
        }


class EncourageTool(Tool):
    """鼓励生成工具"""
    name = "encourage"
    description = "当用户感到沮丧、焦虑、想放弃、或者需要打气时使用。根据用户的具体情况生成个性化鼓励。"
    parameters = {
        "type": "object",
        "properties": {
            "situation": {"type": "string", "description": "用户当前遇到的情况（可选）"}
        }
    }

    def execute(self, params: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
        buddy = ctx.get("buddy")
        study_tracker = ctx.get("study_tracker")

        # 根据连续学习天数生成不同强度的鼓励
        streak = 0
        if study_tracker:
            streak = study_tracker.get_streak_days()

        encouragements = []
        if streak >= 7:
            encouragements = ["你已经连续学习了7天以上，真的很厉害！", "这种坚持本身就是胜利，继续加油！"]
        elif streak >= 3:
            encouragements = ["3天了！习惯正在养成中~", "小坚持也有大力量，继续保持！"]
        else:
            encouragements = ["没关系，重新开始就是进步！", "每个人都会有低落的时候，我陪着你~"]

        return {
            "success": True,
            "message": "\n".join(encouragements),
            "streak": streak
        }


# ========== 工具注册表 ==========

TOOL_REGISTRY: Dict[str, Tool] = {
    "study_timer": StudyTimerTool(),
    "get_study_stats": GetStudyStatsTool(),
    "manage_task": TaskTool(),
    "check_milestone": CheckMilestoneTool(),
    "record_emotion": RecordEmotionTool(),
    "get_buddy_status": GetBuddyStatusTool(),
    "search_memory": SearchMemoryTool(),
    "encourage": EncourageTool(),
}


def get_available_tools() -> List[Dict[str, Any]]:
    """获取所有可用工具的元数据（用于注入到 AI 提示词）"""
    tools = []
    for name, tool in TOOL_REGISTRY.items():
        tools.append({
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters
        })
    return tools


def execute_tool_call(tool_name: str, params: Dict[str, Any], buddy_context: Dict[str, Any]) -> Dict[str, Any]:
    """执行工具调用"""
    tool = TOOL_REGISTRY.get(tool_name)
    if not tool:
        return {"success": False, "message": f"未知的工具：{tool_name}"}

    try:
        return tool.execute(params, buddy_context)
    except Exception as e:
        return {"success": False, "message": f"工具执行出错：{str(e)}"}


def extract_tool_calls(text: str) -> List[Dict[str, Any]]:
    """
    从 AI 回复中提取工具调用

    支持格式：
    <tool_call>
    {"name": "study_timer", "params": {"action": "start"}}
    </tool_call>
    """
    pattern = r'<tool_call>(.*?)</tool_call>'
    matches = re.findall(pattern, text, re.DOTALL)
    calls = []
    for match in matches:
        try:
            call = json.loads(match.strip())
            if isinstance(call, dict) and "name" in call:
                calls.append({
                    "name": call["name"],
                    "params": call.get("params", {})
                })
        except json.JSONDecodeError:
            pass
    return calls


def format_tool_result_for_ai(result: Dict[str, Any]) -> str:
    """将工具执行结果格式化为字符串，返回给 AI 进行二次处理"""
    if result.get("success"):
        return f"[工具执行成功] {result.get('message', '')}"
    else:
        return f"[工具执行失败] {result.get('message', '')}"
