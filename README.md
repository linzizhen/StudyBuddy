# StudyPal 学习豆

你的智能学习搭子，陪你一起变优秀！

## 功能特点

### 🎯 核心功能
- **番茄钟计时器** - 专注学习，支持自定义时长
- **任务管理** - 添加、跟踪、完成任务，截止日期提醒
- **学习日历** - 可视化学习记录，热力图展示
- **AI 助手** - 基于 Ollama 本地模型，智能问答
- **对话历史** - 持久化存储，随时回顾

### 🏆 成就系统
- 多维度学习成就（番茄钟、连续天数、学习时长等）
- 积分与等级制度，激励持续学习
- 成就徽章展示，解锁动画

### 🔔 智能提醒
- 桌面通知支持，番茄钟完成时自动提醒
- 任务截止提醒，再也不会错过重要事项

### 🎨 界面特色
- 精美的开屏动画
- 深色/浅色主题切换
- 响应式设计，支持移动端

## 技术栈

- **后端**: Flask (Python)
- **前端**: HTML5 + CSS3 + JavaScript
- **AI**: Ollama (本地部署，支持 qwen3.5 等模型)
- **数据**: JSON 文件本地存储

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 Ollama

确保本地已安装 [Ollama](https://ollama.ai/) 并下载模型：

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
├── app.py              # Flask 主应用
├── config.py           # 配置文件
├── requirements.txt    # Python 依赖
├── templates/
│   └── index.html      # 前端页面
├── src/
│   ├── ai/
│   │   └── ai_helper.py      # AI 对话模块
│   ├── core/
│   │   ├── buddy.py          # 学习搭子（情绪管理）
│   │   └── timer.py          # 计时器和监督器
│   └── modules/
│       ├── achievements.py    # 成就系统
│       ├── ai_memory.py       # AI 记忆存储
│       ├── data_manager.py    # 数据管理
│       ├── plan_generator.py  # 学习计划生成
│       ├── study_calendar.py  # 学习日历
│       └── task_manager.py    # 任务管理
├── data/               # 数据存储目录
└── assets/            # 静态资源（可选）
```

## 数据存储

所有数据存储在 `data/` 目录下：
- `user_settings.json` - 用户设置
- `tasks.json` - 任务数据
- `ai_history.json` - AI 对话历史
- `achievements.json` - 成就数据
- `calendar.json` - 学习日历数据

## License

MIT License
