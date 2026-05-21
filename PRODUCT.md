# StudyPal 产品文档 v3.0

## 产品概述

StudyPal 是一款面向考研学生的 AI 学习搭子应用，核心特点是有情绪反应的虚拟学习伴侣，陪伴用户度过考研全程。

### 目标用户

- 准备考研的大学生
- 需要学习陪伴和监督的用户
- 希望提高学习效率和动力的用户

### 核心功能

1. **AI 搭子系统** - 6种性格可选的虚拟学习伙伴
2. **智能学习追踪** - 番茄钟 + 统计报表
3. **情绪日记** - 记录心情，分析情绪曲线
4. **任务管理** - 待办事项 + 学习计划
5. **成就系统** - 激励持续学习

---

## 技术架构

### 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Flask 3.0 + SQLAlchemy |
| 数据库 | SQLite（开发）/ PostgreSQL（生产）|
| 前端 | 原生 JavaScript SPA |
| 认证 | JWT |
| 部署 | Docker + Gunicorn |

### 目录结构

```
StudyPal/
├── app.py                 # 应用入口
├── requirements.txt       # 依赖
├── Dockerfile            # Docker 配置
├── docker-compose.yml    # Docker Compose 配置
│
├── src/
│   ├── auth/             # 认证模块
│   │   └── auth.py       # JWT + 用户认证
│   ├── models/           # 数据模型
│   │   └── models.py     # SQLAlchemy 模型
│   ├── buddy/            # 搭子系统
│   │   ├── buddy_roles.py    # 角色配置
│   │   ├── buddy_profile.py  # 档案管理
│   │   ├── buddy_memory.py   # 记忆系统
│   │   └── caring_engine.py  # 关心引擎
│   ├── core/
│   │   └── buddy.py      # 核心搭子类
│   ├── ai/               # AI 接口
│   │   ├── ai_helper.py # AI 调用
│   │   └── prompt_templates.py # 提示词模板
│   ├── study/            # 学习追踪
│   │   └── study_tracker.py
│   ├── diary/           # 日记系统
│   │   └── diary.py
│   └── db.py             # 数据库管理脚本
│
├── routes/               # API 路由
│   ├── auth_routes.py   # 认证路由
│   ├── buddy.py         # 搭子路由
│   ├── study.py         # 学习路由
│   ├── diary.py         # 日记路由
│   └── ...
│
├── templates/           # HTML 模板
│   ├── index.html       # 主页面
│   └── auth/            # 认证页面
│       ├── login.html
│       └── register.html
│
├── static/              # 静态资源
│   ├── css/
│   └── js/
│
└── data/                # 数据存储（开发环境）
```

---

## API 文档

### 认证接口

#### POST /api/auth/register - 用户注册

**请求体：**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "nickname": "考研战士"
}
```

**响应：**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "nickname": "考研战士",
    "subscription_tier": "free"
  }
}
```

#### POST /api/auth/login - 用户登录

**请求体：**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

#### GET /api/auth/me - 获取当前用户

**请求头：**
```
Authorization: Bearer <token>
```

---

### 搭子接口

#### GET /api/buddy/status - 获取搭子状态

#### POST /api/buddy/chat - 发送消息

**请求体：**
```json
{
  "message": "今天心情不好",
  "conversation_id": "conv_xxx"
}
```

**响应：**
```json
{
  "success": true,
  "reply": "抱抱你...",
  "emotion": "worried",
  "emoji": "😟"
}
```

#### GET /api/buddy/roles - 获取所有角色

#### POST /api/buddy/role/switch - 切换角色

---

## 会员体系

### 订阅等级

| 等级 | 价格 | AI 调用次数 | 功能 |
|------|------|-------------|------|
| Free | 免费 | 100次/月 | 基础功能 |
| Pro | ¥29/月 | 1000次/月 | 全部功能 + 优先 AI |
| VIP | ¥99/月 | 10000次/月 | 全部功能 + 专属搭子 |

### AI 调用限制

- Free: 100次/月
- Pro: 1000次/月
- VIP: 10000次/月

---

## 部署指南

### Docker 部署（推荐）

1. 复制环境配置：
```bash
cp .env.production .env
```

2. 编辑 `.env` 填写实际值：
```bash
SECRET_KEY=your-secure-random-key
DATABASE_URL=postgresql://user:pass@localhost:5432/studypal
AI_API_KEY=your-openai-key
```

3. 启动服务：
```bash
docker-compose up -d
```

### 传统部署

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 初始化数据库：
```bash
python -m src.db init
python -m src.db seed  # 可选：填充测试数据
```

3. 启动应用：
```bash
python app.py
```

---

## 开发指南

### 本地开发

```bash
# 克隆代码
git clone https://github.com/linzizhen/StudyBuddy.git
cd StudyBuddy

# 安装依赖
pip install -r requirements.txt

# 复制环境变量
cp .env.example .env
# 编辑 .env 填写 AI API Key

# 初始化数据库
python -m src.db init
python -m src.db seed

# 启动开发服务器
flask run --debug
```

### 创建管理员

```bash
python -m src.db admin admin@example.com
```

---

## 版本历史

### v3.0 (2026-05-21)
- 新增用户认证系统（JWT）
- 迁移到 SQLAlchemy ORM
- 新增多用户数据隔离
- 新增订阅会员体系
- 新增管理员后台
- 新增 Docker 部署支持

### v2.0 (2026-04-30)
- 重构为 Flask Web 应用
- 新增番茄钟功能
- 新增情绪日记
- 新增成就系统

### v1.0 (2026-04-13)
- CLI 版本发布
