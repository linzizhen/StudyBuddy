"""
StudyBuddy 配置文件
包含所有可配置的参数，方便用户自定义设置

作者：StudyBuddy
创建日期：2026-04-13
"""

# ==================== AI 配置 ====================

# 多模型配置字典
# 每个模型配置包含：
#   - name: 显示名称
#   - model: 模型标识符（API 调用时使用）
#   - provider: 提供者类型 ('ollama' 或 'openai')
#   - base_url: API 基础 URL
#   - api_key: API 密钥（Ollama 不需要，留空即可）
MODELS_CONFIG = {
    # Ollama 本地模型
    "qwen3.5_9b": {
        "name": "Qwen3.5 9B (本地)",
        "model": "qwen3.5:9b",
        "provider": "ollama",
        "base_url": "http://localhost:11434",
        "api_key": ""
    },
    "qwen2.5_7b": {
        "name": "Qwen2.5 7B (本地)",
        "model": "qwen2.5:7b",
        "provider": "ollama",
        "base_url": "http://localhost:11434",
        "api_key": ""
    },
    "llama3_8b": {
        "name": "Llama3 8B (本地)",
        "model": "llama3:8b",
        "provider": "ollama",
        "base_url": "http://localhost:11434",
        "api_key": ""
    },
    "mistral_7b": {
        "name": "Mistral 7B (本地)",
        "model": "mistral:7b",
        "provider": "ollama",
        "base_url": "http://localhost:11434",
        "api_key": ""
    },
    
    # OpenAI 兼容 API 示例（需要替换为实际的 API 地址和密钥）
    # "openai_gpt4o": {
    #     "name": "GPT-4o (OpenAI)",
    #     "model": "gpt-4o",
    #     "provider": "openai",
    #     "base_url": "https://api.openai.com/v1",
    #     "api_key": "your-api-key-here"
    # },
    # "deepseek": {
    #     "name": "DeepSeek (API)",
    #     "model": "deepseek-chat",
    #     "provider": "openai",
    #     "base_url": "https://api.deepseek.com/v1",
    #     "api_key": "your-api-key-here"
    # },
}

# 默认使用的模型配置 key
DEFAULT_MODEL_KEY = "qwen3.5_9b"

# 兼容旧版本的单模型配置（如果 MODELS_CONFIG 为空则使用）
API_BASE = "http://localhost:11434"
MODEL_NAME = "qwen3.5:9b"
API_KEY = ""

# ==================== 情绪配置 ====================

# 情绪更新间隔（秒）
# 每隔这个时间，宠物会根据学习状态更新情绪
MOOD_UPDATE_INTERVAL = 30

# ==================== 学习配置 ====================

# 学习计时器默认时长（分钟）
# 点击"开始学习"后的默认计时时长
DEFAULT_TIMER_MINUTES = 25

# ==================== 表情状态 ====================

# 表情符号配置（命令行/Web 版本使用）
EMOJIS = {
    # 原有情绪
    "idle": "😴",        # 空闲/休息状态 - 默认状态
    "happy": "😊",       # 开心/完成任务
    "sad": "😢",         # 难过/太久没学习
    "study": "📚",       # 学习中
    "thinking": "🤔",    # 思考/AI 回答中
    
    # 新增情绪
    "angry": "😡",       # 生气/用户一直玩手机时（超过 2 小时没活动）
    "excited": "🎉",     # 兴奋/完成学习目标时
    "sleepy": "😪",      # 困倦/深夜学习时（23:00-6:00）
    "proud": "😤"        # 自豪/用户坚持学习时（连续学习 3 次以上）
}

# 情绪图片路径配置（GUI 版本使用）
EMOTION_IMAGES = {
    "idle": "assets/idle.png",
    "happy": "assets/happy.png",
    "sad": "assets/sad.png",
    "study": "assets/study.png",
    "thinking": "assets/thinking.png",
    "angry": "assets/angry.png",
    "excited": "assets/excited.png",
    "sleepy": "assets/sleepy.png",
    "proud": "assets/proud.png"
}

# ==================== 任务配置 ====================

# 任务数据文件路径
TASK_DATA_FILE = "data/tasks.json"

# 任务提醒时间（分钟）
# 距离截止时间多少分钟前发出提醒
REMINDER_BEFORE_MINUTES = 30

# ==================== 学习日程配置 ====================

# 学习日志数据文件路径
STUDY_LOG_DATA_FILE = "data/study_log.json"

# 日历数据文件路径
CALENDAR_DATA_FILE = "data/calendar.json"

# 每日学习目标（分钟）
DAILY_GOAL_MINUTES = 120

# ==================== 用户数据配置 ====================

# 用户数据文件路径
USER_DATA_FILE = "data/user_settings.json"

# 默认每日学习目标（分钟）
DEFAULT_DAILY_GOAL = 120

# ==================== AI 历史记录配置 ====================

# AI 对话历史数据文件路径
AI_HISTORY_FILE = "data/ai_history.json"

# ==================== 成就系统配置 ====================

# 成就数据文件路径
ACHIEVEMENTS_FILE = "data/achievements.json"
