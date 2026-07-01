"""
StudyBuddy 配置文件
包含所有可配置的参数，方便用户自定义设置

支持环境变量覆盖，详情见 .env.example

作者：StudyBuddy
创建日期：2026-04-13
重构日期：2026-04-30（dataclass 重构 + 环境变量中心化）
"""

import os
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


# ==================== 应用配置 ====================

@dataclass
class AppConfig:
    """应用基础配置"""
    debug: bool = field(default_factory=lambda: os.getenv('FLASK_DEBUG', 'False').lower() == 'true')
    secret_key: Optional[str] = field(default_factory=lambda: os.getenv('SECRET_KEY'))
    host: str = field(default_factory=lambda: os.getenv('HOST', '0.0.0.0'))
    port: int = field(default_factory=lambda: int(os.getenv('PORT', '5000')))
    cors_origins: str = field(default_factory=lambda: os.getenv('CORS_ORIGINS', '*'))
    log_level: str = field(default_factory=lambda: os.getenv('LOG_LEVEL', 'INFO'))


# ==================== AI 配置 ====================

@dataclass
class AIConfig:
    """AI 模型配置"""
    base_url: str = field(default_factory=lambda: os.getenv('OLLAMA_BASE_URL', 'https://api.groq.com/openai/v1'))
    default_model: str = field(default_factory=lambda: os.getenv('DEFAULT_MODEL', 'llama-3.3-70b-versatile'))
    timeout: int = field(default_factory=lambda: int(os.getenv('AI_TIMEOUT', '60')))
    max_retries: int = field(default_factory=lambda: int(os.getenv('AI_MAX_RETRIES', '3')))
    api_key: str = field(default_factory=lambda: os.getenv('AI_API_KEY', ''))
    model_key: str = field(default_factory=lambda: os.getenv('DEFAULT_MODEL_KEY', 'groq_llama'))


# 单例配置实例
app_config = AppConfig()
ai_config = AIConfig()


# ==================== 兼容旧版本（保持向后兼容） ====================

# AI 配置（向后兼容）
OLLAMA_BASE_URL = ai_config.base_url
DEFAULT_MODEL = ai_config.default_model
AI_TIMEOUT = ai_config.timeout
AI_MAX_RETRIES = ai_config.max_retries
API_BASE = ai_config.base_url
MODEL_NAME = ai_config.default_model
API_KEY = ai_config.api_key
DEFAULT_MODEL_KEY = ai_config.model_key

# 多模型配置字典
# 每个模型配置包含：
#   - name: 显示名称
#   - model: 模型标识符（API 调用时使用）
#   - provider: 提供者类型 ('ollama' 或 'openai')
#   - base_url: API 基础 URL
#   - api_key: API 密钥
MODELS_CONFIG = {
    # ===== 云端免费模型（推荐）=====
    # Groq - 免费额度，速度极快（300+ tokens/s）
    "groq_llama": {
        "name": "Llama 3.3 70B (Groq)",
        "model": "llama-3.3-70b-versatile",
        "provider": "openai",
        "base_url": "https://api.groq.com/openai/v1",
        "api_key": ""  # 需要从 https://console.groq.com 获取
    },
    "groq_mixtral": {
        "name": "Mixtral 8x7B (Groq)",
        "model": "mixtral-8x7b-32768",
        "provider": "openai",
        "base_url": "https://api.groq.com/openai/v1",
        "api_key": ""  # 需要从 https://console.groq.com 获取
    },
    # DeepSeek - 新用户有大量免费额度
    "deepseek_chat": {
        "name": "DeepSeek Chat (DeepSeek)",
        "model": "deepseek-chat",
        "provider": "openai",
        "base_url": "https://api.deepseek.com/v1",
        "api_key": ""  # 需要从 https://platform.deepseek.com 获取
    },
    "deepseek_r1": {
        "name": "DeepSeek R1 (DeepSeek)",
        "model": "deepseek-reasoner",
        "provider": "openai",
        "base_url": "https://api.deepseek.com/v1",
        "api_key": ""  # 需要从 https://platform.deepseek.com 获取
    },
    # OpenRouter - 聚合多个免费模型
    "openrouter_deepseek": {
        "name": "DeepSeek R1 (OpenRouter)",
        "model": "deepseek/deepseek-r1-0528-qwen3-8b:free",
        "provider": "openai",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key": ""  # 需要从 https://openrouter.ai/keys 获取
    },

    # ===== 智谱AI (Zhipu/GLM) - 国内免费推荐 =====
    # 智谱开放平台：https://open.bigmodel.cn
    "zhipu_glm4_flash": {
        "name": "GLM-4-Flash（免费推荐）",
        "model": "glm-4-flash",
        "provider": "zhipu",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "api_key": ""  # 需要从 https://open.bigmodel.cn/usercenter/apikeys 获取
    },
    "zhipu_glm_z1_flash": {
        "name": "GLM-Z1-Flash（推理/免费）",
        "model": "glm-z1-flash",
        "provider": "zhipu",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "api_key": ""
    },
    "zhipu_glm4": {
        "name": "GLM-4（标准版）",
        "model": "glm-4",
        "provider": "zhipu",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "api_key": ""
    },
    "zhipu_glm4v": {
        "name": "GLM-4V（多模态）",
        "model": "glm-4v",
        "provider": "zhipu",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "api_key": ""
    },

    # ===== Ollama 本地模型 =====
    "qwen3.5_9b": {
        "name": "Qwen3.5 9B (本地)",
        "model": "qwen3.5:9b",
        "provider": "ollama",
        "base_url": OLLAMA_BASE_URL,
        "api_key": ""
    },
    "qwen2.5_7b": {
        "name": "Qwen2.5 7B (本地)",
        "model": "qwen2.5:7b",
        "provider": "ollama",
        "base_url": OLLAMA_BASE_URL,
        "api_key": ""
    },
    "llama3_8b": {
        "name": "Llama3 8B (本地)",
        "model": "llama3:8b",
        "provider": "ollama",
        "base_url": OLLAMA_BASE_URL,
        "api_key": ""
    },
    "mistral_7b": {
        "name": "Mistral 7B (本地)",
        "model": "mistral:7b",
        "provider": "ollama",
        "base_url": OLLAMA_BASE_URL,
        "api_key": ""
    },

    # ===== OpenAI 兼容 API（需付费）=====
    # "openai_gpt4o": {
    #     "name": "GPT-4o (OpenAI)",
    #     "model": "gpt-4o",
    #     "provider": "openai",
    #     "base_url": "https://api.openai.com/v1",
    #     "api_key": "your-api-key-here"
    # },
}

# 默认使用的模型配置 key（推荐使用云端免费模型）
DEFAULT_MODEL_KEY = os.getenv('DEFAULT_MODEL_KEY', 'groq_llama')

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

# ==================== 用户数据配置 ====================

# 用户数据文件路径
USER_DATA_FILE = "data/user_settings.json"

# ==================== AI 历史记录配置 ====================

# AI 对话历史数据文件路径
AI_HISTORY_FILE = "data/ai_history.json"

# ==================== 成就系统配置 ====================

# 成就数据文件路径
ACHIEVEMENTS_FILE = "data/achievements.json"
