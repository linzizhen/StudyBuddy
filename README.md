# StudyPal - 智能学习搭子

> 你的 AI 学习伙伴，陪你一起变优秀！

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 产品简介

StudyPal 是一款面向泛学习者的 AI 学习搭子应用，核心特点是有情绪反应的虚拟学习伴侣。不再局限于考研，而是支持所有需要学习陪伴和监督的场景：考研、考证、考公、技能学习、语言学习等。

## 核心功能

### AI 搭子系统
- **6 种预设性格**：小豆（温柔陪伴）、阿然（热血激励）、学长（理性导师）、小夜（深夜倾听）、小九（幽默搞怪）、阿正（理性分析）
- **情绪感知**：11 种情绪状态随对话动态变化
- **搭子等级**：5 级成长体系，0/7/21/60/100 天解锁不同默契度
- **自定义搭子**：可创建专属学习伙伴

### 智能学习追踪
- **番茄钟计时器**：专注学习，支持自定义科目（数学/英语/政治/专业课）
- **学习统计**：连续学习天数、日/周/月学习量统计
- **成就系统**：32 个成就徽章 + 积分等级制度

### 情绪日记
- **每日记录**：记录心情、学习感受、事件
- **情绪追踪**：1-5 分情绪曲线图
- **日记回顾**：按月查看历史记录

### 任务管理
- **待办清单**：支持优先级和截止时间
- **学习计划**：AI 生成或基础模式，按考试日期生成阶段性计划
- **每日推荐**：基于时间、科目、计划自动推荐任务

## 技术架构

### 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Flask 3.0 + Python |
| 前端 | 原生 JavaScript SPA |
| AI | OpenAI 兼容 API（Groq/DeepSeek/OpenRouter/本地 Ollama）|
| 数据 | JSON 文件本地存储 |
| 认证 | JWT |

### 架构特点

- **后端流式代理**：API Key 完全在后端，消除前端暴露风险
- **用户数据隔离**：Buddy 实例和数据按 user_id 隔离
- **三层记忆系统**：重要性评分 + 自动遗忘机制
- **工具系统**：7 种搭子技能（学习计时、任务管理、里程碑检查等）

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 AI 模型

**推荐：使用云端免费模型（无需安装，响应快）**

1. 获取 API Key（任选其一）：
   - **Groq**（推荐，免费）：https://console.groq.com/keys
   - **DeepSeek**：https://platform.deepseek.com/api_keys
   - **OpenRouter**：https://openrouter.ai/keys

2. 创建 `.env` 文件：
   ```
   AI_API_KEY=你的API密钥
   DEFAULT_MODEL_KEY=groq_llama
   ```

**可选：使用本地 Ollama 模型**

确保已安装 [Ollama](https://ollama.ai/) 并下载模型：

```bash
ollama pull qwen3.5:9b
```

### 3. 启动服务

```bash
python app.py
```

### 4. 访问应用

打开浏览器访问 http://localhost:5000

## 项目结构

```
StudyPal/
├── app.py                    # Flask 应用入口
├── config.py                 # 配置中心（模型、AI、超时等）
├── requirements.txt          # Python 依赖
│
├── routes/                   # Flask Blueprint 路由模块
│   ├── __init__.py         # 路由注册中心
│   ├── buddy.py             # 搭子对话、状态、角色 API
│   ├── ai_model.py          # AI 模型配置 API
│   ├── auth.py              # 认证路由
│   ├── study.py             # 学习追踪 API
│   ├── diary.py             # 日记 API
│   ├── tasks.py             # 任务 API
│   ├── achievements.py      # 成就 API
│   ├── plans.py             # 学习计划 API
│   ├── timeline.py          # 考研历程 API
│   ├── recommend.py         # 每日推荐 API
│   └── insights.py          # 数据洞察 API
│
├── src/                     # 核心业务模块
│   ├── auth/
│   │   └── auth.py         # JWT + 用户认证服务
│   │
│   ├── buddy/              # 搭子系统核心
│   │   ├── buddy_roles.py  # 6 种角色配置 + 情绪响应映射
│   │   ├── buddy_profile.py # 用户/搭子档案管理
│   │   ├── buddy_memory.py  # 三层记忆系统
│   │   ├── buddy_tools.py   # 搭子技能工具
│   │   └── caring_engine.py # 主动关心引擎
│   │
│   ├── core/
│   │   └── buddy.py       # Buddy 核心类
│   │
│   ├── ai/
│   │   ├── ai_helper.py   # AI 调用封装
│   │   └── prompt_templates.py # 提示词模板
│   │
│   ├── study/
│   │   └── study_tracker.py # 番茄钟 + 学习统计
│   │
│   ├── diary/
│   │   └── diary.py       # 情绪日记
│   │
│   ├── utils/
│   │   ├── validators.py  # 输入验证装饰器
│   │   └── file_lock.py   # 文件锁
│   │
│   └── modules/
│       ├── achievements.py  # 成就系统
│       ├── task_manager.py  # 任务管理
│       ├── plan_generator.py # 学习计划生成
│       ├── timeline.py      # 考研历程时间线
│       ├── daily_recommender.py # 每日推荐
│       ├── data_manager.py  # 数据管理器
│       └── ai_memory.py    # AI 对话历史
│
├── static/                  # 静态资源
│   ├── css/                # 样式文件
│   │   ├── variables.css   # CSS 变量
│   │   ├── app.css        # 应用样式
│   │   ├── home.css       # 首页样式
│   │   ├── chat.css       # 聊天样式
│   │   ├── diary.css      # 日记样式
│   │   ├── bento.css      # Bento 网格布局
│   │   ├── landing.css    # 着陆页样式
│   │   └── tokens.css     # 设计令牌
│   └── js/
│       ├── app.js          # 主应用
│       ├── router.js       # SPA 路由
│       ├── state.js        # 状态管理
│       ├── api.js          # API 调用层
│       ├── constants.js    # 常量定义
│       └── pages/          # 页面模块
│           ├── home.js
│           ├── chat.js
│           └── diary.js
│
├── templates/               # HTML 模板
│   ├── index.html          # 主页面
│   ├── home.html           # 首页
│   ├── chat.html           # 聊天页
│   ├── diary.html          # 日记页
│   ├── tasks.html          # 任务页
│   ├── landing.html        # 着陆页
│   ├── splash.html         # 开屏页
│   ├── settings.html       # 设置页
│   └── auth/               # 认证页面
│       ├── login.html
│       └── register.html
│
└── data/                   # JSON 数据存储
    ├── users.json          # 用户数据
    ├── buddy_profile.json  # 搭子档案
    ├── buddy_memory.json   # 搭子记忆
    ├── diary.json          # 日记数据
    ├── study_tracker.json  # 学习记录
    ├── ai_history.json     # AI 对话历史
    ├── tasks.json          # 任务列表
    ├── achievements.json   # 成就状态
    ├── plans.json          # 学习计划
    └── timeline.json       # 考研历程
```

## API 接口

### 认证接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/auth/register` | POST | 用户注册 |
| `/api/auth/login` | POST | 用户登录 |
| `/api/auth/me` | GET | 获取当前用户 |

### 搭子接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/buddy/status` | GET | 获取搭子状态 |
| `/api/buddy/chat` | POST | 发送消息 |
| `/api/buddy/chat/stream` | POST | 流式对话 |
| `/api/buddy/roles` | GET | 获取所有角色 |
| `/api/buddy/role/switch` | POST | 切换角色 |
| `/api/buddy/profile` | GET/POST | 搭子档案 |
| `/api/buddy/memory` | GET/POST | 搭子记忆 |
| `/api/buddy/caring` | GET | 获取关心卡片 |
| `/api/buddy/analyze` | POST | 情绪分析 |
| `/api/buddy/custom/*` | POST/GET/PUT | 自定义搭子管理 |

### 学习接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/study/start` | POST | 开始学习 |
| `/api/study/stop` | POST | 停止学习 |
| `/api/study/stats` | GET | 学习统计 |

### 日记接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/diary` | GET/POST | 日记 CRUD |
| `/api/diary/today` | GET | 今日日记 |
| `/api/diary/emotions` | GET | 情绪追踪 |
| `/api/diary/review` | GET | 日记回顾 |

### 任务接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/tasks` | GET/POST | 任务列表 |
| `/api/tasks/<id>` | PUT/DELETE | 更新/删除 |
| `/api/tasks/<id>/complete` | POST | 完成任务 |
| `/api/tasks/stats` | GET | 任务统计 |

### AI 模型接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/ai-model/presets` | GET | 预设模型列表 |
| `/api/ai-model/current` | GET | 当前模型 |
| `/api/ai-model/preset` | POST | 切换预设模型 |
| `/api/ai-model/custom` | POST/DELETE | 自定义模型 |
| `/api/ai-model/test` | POST | 测试连接 |

## 数据存储

所有数据以 JSON 格式存储在 `data/` 目录：

| 文件 | 说明 |
|------|------|
| `users.json` | 用户账户信息 |
| `buddy_profile.json` | 用户档案、搭子信息、考研目标 |
| `buddy_memory.json` | 三层记忆（用户画像/场景记忆/对话摘要）|
| `diary.json` | 日记内容、情绪评分 |
| `study_tracker.json` | 学习时段记录 |
| `ai_history.json` | AI 对话记录 |
| `tasks.json` | 任务列表 |
| `achievements.json` | 成就解锁状态、积分、等级 |
| `plans.json` | 学习计划 |
| `timeline.json` | 考研历程记录 |

## 版本历史

- **v4.0** (2026-06-08)：AI 搭子系统重构
  - 后端流式代理，消除 API Key 暴露风险
  - 用户数据隔离
  - 三层记忆系统 + 自动遗忘机制
  - 7 种搭子技能工具
  - 提示词工程升级

- **v3.0** (2026-05-21)：新增用户认证系统

- **v2.0** (2026-04-30)：重构为 Flask Web 应用

- **v1.0** (2026-04-13)：CLI 版本发布

## License

MIT License
