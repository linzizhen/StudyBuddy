# StudyPal 考研搭子

> 你的智能学习搭子，陪你一起变优秀！

## 功能特点

### 搭子系统
- **情绪感知搭子**：10 种情绪状态（开心、难过、兴奋、困倦、自豪等），搭子情绪随学习状态动态变化
- **三层记忆系统**：工作记忆（学习偏好）、情绪记忆（重要事件）、场景记忆，记住你的重要信息
- **主动关心引擎**：行为感知驱动，自动早安问候、学习提醒、情绪关怀、成就庆祝、睡眠提醒

### 学习功能
- **番茄钟计时器**：专注学习，支持自定义科目（数学/英语/政治/专业课），可暂停/继续
- **学习追踪**：记录每日学习时段，计算连续学习天数，统计日/周学习量
- **任务管理**：添加、编辑、完成、删除任务，支持优先级和截止时间
- **学习计划**：AI 生成或基础模式，按考试日期和科目生成阶段性计划
- **每日推荐**：基于时间、科目、计划自动推荐每日任务
- **考研历程**：时间线记录里程碑、困难时刻、突破时刻、情绪变化

### AI 助手
- **本地 AI**：基于 Ollama，支持 qwen3.5、qwen2.5、llama3、mistral 等多模型，可扩展 OpenAI 兼容 API
- **智能问答**：学习疑问解答、计划建议、心理支持
- **对话历史**：持久化存储，支持多会话、搜索

### 成就系统
- **32 个成就徽章**：番茄钟、连续学习、任务完成、隐藏彩蛋等
- **积分与等级制度**：学习小白 → 学习传奇（10 个等级）
- **成就解锁动画**：实时弹窗通知

### 界面特色
- **现代卡片式布局**：清晰的信息层次
- **CSS 模块化设计**：变量系统、组件库、动画系统分离
- **响应式设计**：适配桌面和移动端
- **丰富交互动画**：页面切换、成就解锁、情绪波动

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Flask (Python) + Blueprint 架构 |
| 前端 | HTML5 + CSS3 (模块化) + Vanilla JS |
| AI | Ollama (本地部署) / OpenAI 兼容 API |
| 数据 | JSON 文件本地存储 |

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

2. 在项目根目录创建 `.env` 文件，填入 API Key：
   ```
   AI_API_KEY=你的API密钥
   DEFAULT_MODEL_KEY=groq_llama
   ```

**可选：使用本地 Ollama 模型**

确保本地已安装 [Ollama](https://ollama.ai/) 并下载模型：

```bash
ollama pull qwen3.5:9b
```

如需切换模型，编辑 `config.py` 中的 `MODELS_CONFIG` 字典，或在应用中通过 API 切换。

### 3. 启动服务

```bash
python app.py
```

### 4. 访问应用

打开浏览器访问 http://localhost:5000

## 项目结构

```
StudyPal/
├── app.py                     # Flask 主应用入口
├── config.py                  # 全局配置文件（AI 模型、情绪、学习计时器等）
├── requirements.txt           # Python 依赖
│
├── routes/                    # Flask Blueprint 路由模块
│   ├── __init__.py           # 路由注册中心
│   ├── buddy.py              # 搭子对话、档案、记忆、关心 API
│   ├── diary.py              # 考研日记、情绪记录 API
│   ├── study.py              # 学习打卡、计时、统计 API
│   ├── tasks.py              # 任务增删改查 API
│   ├── achievements.py       # 成就徽章 API
│   ├── plans.py              # 学习计划生成与管理 API
│   ├── user.py               # 用户设置、AI 问答、对话历史、导出 API
│   ├── timeline.py           # 考研历程时间线 API
│   └── recommend.py          # 每日任务推荐 API
│
├── src/                       # 核心业务模块
│   ├── ai/
│   │   ├── ai_helper.py      # AI 对话核心（Ollama API 调用）
│   │   └── prompt_templates.py # 提示词模板库
│   ├── buddy/
│   │   ├── buddy_profile.py  # 搭子档案（目标院校、专业、分数、备考阶段）
│   │   ├── buddy_memory.py   # 三层记忆系统
│   │   └── caring_engine.py  # 主动关心引擎
│   ├── core/
│   │   ├── buddy.py          # 搭子系统核心（情绪状态、对话处理）
│   │   └── timer.py          # 学习计时器和监督器
│   ├── diary/
│   │   └── diary.py          # 日记系统与情绪追踪器
│   ├── modules/
│   │   ├── achievements.py  # 成就系统（32 个成就、积分等级）
│   │   ├── task_manager.py   # 任务管理器
│   │   ├── plan_generator.py # 学习计划生成器
│   │   ├── timeline.py       # 考研历程时间线
│   │   ├── daily_recommender.py # 每日任务推荐器
│   │   ├── data_manager.py   # 数据管理器（座右铭、收藏、学习目标）
│   │   └── ai_memory.py      # AI 记忆与对话历史
│   └── study/
│       └── study_tracker.py  # 学习追踪器
│
├── static/                    # 静态资源
│   ├── css/
│   │   ├── variables.css     # CSS 变量（主题色彩、间距、圆角、阴影）
│   │   ├── base.css          # 基础样式、重置、工具类、响应式布局
│   │   ├── components.css    # UI 组件样式（卡片、按钮、表单、导航）
│   │   └── animations.css   # 动画关键帧（页面切换、成就解锁动画）
│   └── js/
│       ├── api.js            # API 调用层（封装所有后端 API 请求）
│       ├── state.js          # 状态管理系统（观察者模式、持久化）
│       └── utils.js          # 工具函数（时间格式化、DOM 操作、防抖节流）
│
├── templates/
│   └── index.html            # 单页应用主文件（8 个页面：首页、聊天、记忆、任务、计划、成就、日记、设置）
│
├── data/                      # JSON 数据存储
│   ├── buddy_profile.json    # 用户档案、搭子信息、目标设置
│   ├── buddy_memory.json     # 三层记忆数据
│   ├── diary.json            # 日记和情绪记录
│   ├── study_tracker.json    # 学习时段记录
│   ├── ai_history.json       # AI 对话历史
│   ├── tasks.json            # 任务列表
│   ├── achievements.json     # 成就解锁状态
│   ├── plans.json            # 学习计划
│   ├── timeline.json         # 考研历程时间线
│   └── user_settings.json    # 用户设置
│
├── ai_supervisor/             # AI 监督模块（可选，当前未启用）
│   ├── __init__.py
│   ├── config.py
│   ├── monitor.py
│   ├── camera.py
│   ├── analyzer.py
│   ├── behavior.py
│   ├── notifier.py
│   ├── demo.py
│   ├── run_behavior_test.py
│   ├── ai_monitor/
│   └── requirements.txt
│
├── docs/                      # 项目文档
│   ├── StudyBuddy 项目文档.md
│   └── 项目结构说明.md
│
├── DESIGN_DOC.md             # 设计文档
└── README.md                 # 项目说明
```

## API 接口

应用提供完整的 RESTful API，所有端点以 `/api` 为前缀：

| 模块 | 端点 | 方法 | 说明 |
|------|------|------|------|
| 首页 | `/api/home` | GET | 获取首页展示数据 |
| 搭子 | `/api/buddy/status` | GET | 获取搭子状态 |
| 搭子 | `/api/buddy/chat` | POST | 发送消息并获取回复 |
| 搭子 | `/api/buddy/profile` | GET/POST | 获取/更新搭子档案 |
| 搭子 | `/api/buddy/memory` | GET/POST | 获取/添加记忆 |
| 搭子 | `/api/buddy/caring` | GET | 获取关心卡片 |
| 日记 | `/api/diary` | GET/POST | 日记 CRUD |
| 日记 | `/api/diary/today` | GET | 获取今日日记 |
| 日记 | `/api/diary/emotions` | GET | 获取情绪追踪数据 |
| 日记 | `/api/diary/review` | GET | 获取日记回顾 |
| 学习 | `/api/study/start` | POST | 开始学习计时 |
| 学习 | `/api/study/stop` | POST | 停止学习计时 |
| 学习 | `/api/study/stats` | GET | 获取学习统计数据 |
| 任务 | `/api/tasks` | GET/POST | 获取/添加任务 |
| 任务 | `/api/tasks/<id>` | PUT/DELETE | 更新/删除任务 |
| 任务 | `/api/tasks/<id>/complete` | POST | 完成任务 |
| 任务 | `/api/tasks/stats` | GET | 获取任务统计 |
| 成就 | `/api/achievements` | GET | 获取成就数据 |
| 成就 | `/api/achievements/unlock` | POST | 解锁成就 |
| 计划 | `/api/plans` | GET/POST | 获取/创建学习计划 |
| 计划 | `/api/plans/<id>` | GET/PUT/DELETE | 计划详情/更新/删除 |
| 计划 | `/api/plans/expiring` | GET | 获取即将到期的计划 |
| 用户 | `/api/user/home` | GET | 获取用户首页数据 |
| 用户 | `/api/user/motto` | GET/POST | 座右铭管理 |
| 用户 | `/api/user/ask` | POST | AI 问答 |
| 用户 | `/api/user/data/export` | GET | 导出数据 |
| 时间线 | `/api/timeline` | GET/POST | 获取/添加时间线记录 |
| 时间线 | `/api/timeline/record/<type>` | GET | 按类型获取记录 |
| 推荐 | `/api/recommend/daily` | GET | 获取每日推荐 |
| 推荐 | `/api/recommend/tasks` | GET | 获取推荐任务 |

## 数据存储

所有数据以 JSON 格式存储在 `data/` 目录，支持数据导出备份：

| 文件 | 说明 |
|------|------|
| `buddy_profile.json` | 用户档案、搭子信息、考研目标（院校、专业、分数、考试日期） |
| `buddy_memory.json` | 三层记忆（工作记忆/情绪记忆/场景记忆/对话摘要） |
| `diary.json` | 日记内容、情绪评分（1-5）、学习感受、事件记录 |
| `study_tracker.json` | 学习时段（开始/结束时间、科目、时长） |
| `ai_history.json` | AI 对话记录（消息、模型、时间戳） |
| `tasks.json` | 任务列表（标题、描述、优先级、截止时间、完成状态） |
| `achievements.json` | 成就解锁状态、积分、等级 |
| `plans.json` | 学习计划（科目、阶段、每日任务） |
| `timeline.json` | 考研历程记录（里程碑/困难时刻/突破时刻/情绪变化） |
| `user_settings.json` | 用户设置、偏好配置 |

## 版本历史

- **v2.0** (2026-04-27)：全面重构
  - Flask Blueprint 架构，模块化路由
  - 前端 CSS/JS 模块化分离（变量、组件、动画）
  - 新增任务管理、学习计划、每日推荐页面
  - 三层记忆系统和主动关心引擎
  - 32 个成就徽章与积分等级系统
  - 考研历程时间线
  - 单页应用（SPA）架构

- **v1.0** (2026-04-13)：初始版本

## License

MIT License
