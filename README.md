# StudyPal 考研搭子

> 你的智能学习搭子，陪你一起变优秀！

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)

---

Quickstart - Features - Architecture - API Reference - Configuration - Contributing

---

StudyPal 是一款专为考研学生设计的智能学习助手，提供情绪感知搭子、番茄钟计时、学习追踪、任务管理和成就系统，让学习不再孤单。

## Quickstart

### 1. 安装依赖

```bash
git clone https://github.com/linzizhen/StudyBuddy.git
cd StudyBuddy
pip install -r requirements.txt
```

### 2. 配置 AI 模型

**推荐使用云端免费模型**（无需本地部署，响应快）：

```bash
# 创建环境变量文件
cp .env.example .env
```

编辑 `.env` 文件，填入 API Key（任选其一）：

| 提供商 | 获取地址 | 免费额度 |
|--------|----------|----------|
| **Groq**（推荐） | https://console.groq.com/keys | 充足 |
| DeepSeek | https://platform.deepseek.com/api_keys | 丰富 |
| OpenRouter | https://openrouter.ai/keys | 有限 |

```bash
AI_API_KEY=你的API密钥
DEFAULT_MODEL_KEY=groq_llama
```

**可选：使用本地 Ollama 模型**

```bash
# 安装 Ollama
ollama pull qwen3.5:9b
```

### 3. 启动

```bash
python app.py
```

打开浏览器访问 http://localhost:5000

## Features

### 搭子系统

| 功能 | 说明 |
|------|------|
| 情绪感知 | 10 种情绪状态，搭子情绪随学习状态动态变化 |
| 三层记忆 | 工作记忆（偏好）、情绪记忆（事件）、场景记忆 |
| 主动关心 | 自动早安问候、学习提醒、情绪关怀、成就庆祝 |

### 学习功能

| 功能 | 说明 |
|------|------|
| 番茄钟 | 专注计时，支持多科目（数学/英语/政治/专业课） |
| 学习追踪 | 连续天数、日/周统计、学习曲线 |
| 任务管理 | 优先级、截止时间、任务完成追踪 |
| 学习计划 | AI 生成或手动制定阶段性计划 |
| 数据洞察 | 学习曲线、科目分布、情绪趋势可视化 |

### AI 模型

| 功能 | 说明 |
|------|------|
| 多模型支持 | 9 种预设模型（Groq/DeepSeek/OpenRouter/Ollama） |
| 自定义模型 | 支持用户配置任意 OpenAI 兼容 API |
| 搭子性格 | 6 种性格可选（温柔/热血/学霸/深夜/幽默/理性） |

### 成就系统

| 功能 | 说明 |
|------|------|
| 成就徽章 | 13+ 个成就（番茄钟、连续学习、任务完成等） |
| 积分等级 | 学习小白 → 学习传奇（5 个等级） |
| 情绪追踪 | 日记 + 情绪曲线，记录考研心路历程 |

## Architecture

### 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Flask (Python) + Blueprint 架构 |
| 前端 | HTML5 + CSS3 + Vanilla JavaScript（单页应用） |
| AI | Ollama / OpenAI 兼容 API / Groq / DeepSeek / OpenRouter |
| 数据 | JSON 文件本地存储 |

### 项目结构

```
StudyBuddy/
├── app.py                      # Flask 应用入口
├── config.py                   # 全局配置（AI模型、情绪、学习计时器）
├── requirements.txt           # Python 依赖
│
├── routes/                     # API 路由
│   ├── ai_model.py            # AI 模型配置
│   ├── buddy.py               # 搭子对话、档案、记忆
│   ├── diary.py              # 日记、情绪记录
│   ├── study.py               # 学习打卡、计时
│   ├── tasks.py               # 任务管理
│   ├── achievements.py         # 成就徽章
│   ├── plans.py               # 学习计划
│   ├── insights.py             # 数据洞察
│   └── ...
│
├── src/                        # 核心业务逻辑
│   ├── ai/
│   │   ├── ai_helper.py       # AI 对话核心
│   │   └── prompt_templates.py # 提示词模板
│   ├── buddy/
│   │   ├── buddy_profile.py   # 搭子档案
│   │   ├── buddy_memory.py    # 三层记忆系统
│   │   ├── buddy_roles.py     # 6种搭子性格
│   │   └── caring_engine.py  # 主动关心引擎
│   ├── core/buddy.py         # 搭子系统核心
│   ├── diary/diary.py        # 日记系统
│   └── modules/
│       ├── achievements.py     # 成就系统
│       └── task_manager.py    # 任务管理
│
├── static/
│   ├── css/
│   │   ├── variables.css      # CSS 变量（主题色、间距）
│   │   ├── base.css          # 基础样式
│   │   ├── components.css     # UI 组件
│   │   └── mobile.css        # 移动端适配
│   └── js/app.js             # 应用逻辑
│
├── templates/index.html         # 单页应用（首页/搭话/洞察/记忆/设置）
└── data/                      # JSON 数据存储
    ├── buddy_profile.json     # 用户档案
    ├── buddy_memory.json      # 搭子记忆
    ├── diary.json             # 日记
    ├── study_tracker.json     # 学习记录
    ├── tasks.json             # 任务
    └── achievements.json      # 成就
```

## API Reference

### 搭子 API

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/buddy/status` | 获取搭子状态 |
| POST | `/api/buddy/chat` | 发送消息，获取回复 |
| GET | `/api/buddy/roles` | 获取可选搭子列表 |
| POST | `/api/buddy/role/switch` | 切换搭子角色 |
| GET/PUT | `/api/buddy/profile` | 获取/更新档案 |

### 学习 API

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/study/start` | 开始学习 |
| POST | `/api/study/stop` | 结束学习 |
| GET | `/api/study/stats` | 获取学习统计 |

### 数据洞察 API

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/insights/overview` | 数据概览 |
| GET | `/api/insights/study-chart` | 学习曲线数据 |
| GET | `/api/insights/emotion-chart` | 情绪趋势数据 |
| GET | `/api/insights/subject-analysis` | 科目分析数据 |

### AI 模型 API

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/ai-model/presets` | 获取预设模型列表 |
| GET | `/api/ai-model/current` | 获取当前使用模型 |
| POST | `/api/ai-model/preset` | 切换预设模型 |
| POST | `/api/ai-model/custom` | 保存自定义模型 |
| POST | `/api/ai-model/test` | 测试模型连接 |

## Configuration

### 环境变量

| 变量 | 必填 | 说明 |
|------|------|------|
| `AI_API_KEY` | 是 | AI 服务 API Key |
| `DEFAULT_MODEL_KEY` | 否 | 默认模型 key，默认 `groq_llama` |
| `FLASK_DEBUG` | 否 | 设为 `true` 开启调试模式 |
| `SECRET_KEY` | 否 | Flask 密钥 |

### 预设模型

| Key | 名称 | 提供商 | 类型 |
|------|------|--------|------|
| `groq_llama` | Llama 3.3 70B | Groq | 云端免费 |
| `groq_mixtral` | Mixtral 8x7B | Groq | 云端免费 |
| `deepseek_chat` | DeepSeek Chat | DeepSeek | 云端 |
| `deepseek_r1` | DeepSeek R1 | DeepSeek | 云端推理 |
| `openrouter_deepseek` | DeepSeek R1 | OpenRouter | 免费模型 |
| `qwen3.5_9b` | Qwen3.5 9B | Ollama | 本地 |
| `qwen2.5_7b` | Qwen2.5 7B | Ollama | 本地 |
| `llama3_8b` | Llama3 8B | Ollama | 本地 |
| `mistral_7b` | Mistral 7B | Ollama | 本地 |

## Contributing

欢迎提交 Pull Request！

```bash
# 开发环境设置
pip install -r requirements.txt

# 启动开发服务器
python app.py

# 代码风格
# 遵循 PEP 8 规范
# 前端遵循现有代码风格
```

提交前请：
1. 确保所有 API 端点正常工作
2. 测试新增功能
3. 更新相关文档

## License

MIT License - 详见 [LICENSE](LICENSE)
