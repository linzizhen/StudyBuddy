# StudyPal 产品文档 v4.0

## 产品概述

StudyPal 是一款面向泛学习者的 AI 学习搭子应用，核心特点是有情绪反应的虚拟学习伴侣，陪伴用户度过每一个学习阶段。不再局限于考研，而是支持所有需要学习陪伴和监督的场景：考研、考证、考公、技能学习、语言学习等。

### 目标用户

- 准备考研/考公/考证的学生
- 需要学习陪伴和监督的用户
- 希望提高学习效率和动力的用户
- 任何需要自律和专注陪伴的学习者

### 核心功能

1. **AI 搭子系统** — 6 种预设性格 + 用户自定义搭子，搭子具有情绪反应
2. **智能学习追踪** — 番茄钟 + 统计报表
3. **情绪日记** — 记录心情，分析情绪曲线
4. **任务管理** — 待办事项 + 学习计划
5. **成就系统** — 激励持续学习（3/7/14/30/100 天连续学习里程碑）
6. **AI 模型配置** — 支持预设云端模型 + 用户自定义 API Key

---

## 功能详解

### AI 搭子系统（v4.0 重构）

StudyPal 的搭子是整个产品的灵魂。搭子不是冰冷的问答机器人，而是有情绪、有性格、会主动关心用户的学习伙伴。

#### 预设角色（6 种性格）

| 角色 ID | 名称 | Emoji | 特点 |
|---------|------|-------|------|
| xiaodou | 小豆 | 🌸 | 温柔陪伴 — 善解人意，适合需要情感支持的用户 |
| aran | 阿然 | ⚡ | 热血激励 — 充满干劲，专治躺平摆烂 |
| senior | 学长 | 📚 | 理性导师 — 务实高效，传授学习方法 |
| xiaoye | 小夜 | 🌙 | 深夜倾听 — 深夜学习者的温暖陪伴 |
| xj | 小九 | 😎 | 幽默搞怪 — 快乐源泉，用段子治愈不开心 |
| azheng | 阿正 | 🎯 | 理性分析 — 冷静务实，帮你梳理问题 |

#### 情绪系统

搭子有 11 种情绪状态，会根据用户的消息内容和学习状态自动切换：

| 情绪 | Emoji | 触发场景 |
|------|-------|---------|
| idle | 😴 | 休息中 |
| happy | 😊 | 开心 |
| excited | 🎉 | 太棒了 |
| proud | 😤 | 为你骄傲 |
| thinking | 🤔 | 在思考 |
| study | 📚 | 学习中 |
| worried | 😟 | 有点担心 |
| sad | 😢 | 难过 |
| angry | 😡 | 生气 |
| sleepy | 😪 | 犯困 |
| scared | 😨 | 害怕 |

#### 搭子等级

搭子随用户的学习坚持天数成长，共 5 级：

| 等级 | 天数要求 | 解锁内容 |
|------|---------|---------|
| 初级 | 0+ | 基础对话 |
| 成长 | 7+ | 更多鼓励话语 |
| 熟悉 | 21+ | 记住更多细节 |
| 默契 | 60+ | 主动发起话题 |
| 灵魂 | 100+ | 最高默契度 |

#### 搭子设计器

用户可以在「设置 → 搭子设计」页面创建专属的学习搭子：

| 可自定义项 | 说明 |
|-----------|------|
| 搭子名称 | 2-20 个字符，给搭子起一个独特的名字 |
| 搭子头像 | 从预设 emoji 中选择，或上传图片 |
| 性格设定 | 描述搭子的性格特点，影响说话方式 |
| 关系描述 | 定义你和搭子的关系（朋友/战友/学长等）|
| 说话风格 | 关键词描述搭子说话的特点 |
| 背景故事 | 选填，让搭子更加立体真实 |
| 系统提示词 | 选填，高级用户可直接编写完整的系统提示词 |

### AI 模型配置

用户可以在「设置 → AI 模型」页面配置 AI 模型。

#### 预设模型（开箱即用）

| 模型 | 说明 |
|------|------|
| Groq Llama 3.3 70B | 免费快速，推荐使用（300+ tokens/s）|
| Groq Mixtral 8x7B | 免费额度，速度快 |
| DeepSeek Chat | 深度思考，适合复杂问题 |
| DeepSeek R1 | 推理模型，适合需要逻辑分析的场景 |
| OpenRouter DeepSeek R1 | 聚合模型，按需选择 |

#### 自定义模型（支持 OpenAI 兼容接口）

- 配置名称 — 给配置起个名字
- API 地址 — OpenAI 兼容的 API 端点
- API Key — 密钥
- 模型名称 — 如 deepseek-chat、gpt-4o

#### 功能特性

- 一键测试连接
- 实时显示当前使用的模型
- 切换模型无需重启
- API Key 安全存储，不暴露在前端

---

## 技术架构（v4.0）

### 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                         浏览器（前端）                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  聊天界面  │  │ 角色切换器 │  │搭子设计器 │  │ 头像系统  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       └──────────────┼──────────────┴──────────────┘        │
│                      │                                     │
│           sendChat() / _browserDirectChat()                 │
└──────────────────────┼──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   Flask 后端（安全代理）                       │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              /api/buddy/chat/stream                   │   │
│  │         后端统一代理 AI 调用（API Key 不暴露）          │   │
│  │           后端流式响应（SSE）+ 前端回退               │   │
│  └────────────────────────┬─────────────────────────────┘   │
│                           │                                 │
│  ┌──────────────┐  ┌──────┴──────────┐  ┌──────────────┐  │
│  │   搭子核心    │  │   AI 模型配置    │  │   关心引擎   │  │
│  │ Buddy 类     │  │  MODELS_CONFIG   │  │ CaringEngine │  │
│  │ (情绪/对话)  │  │ (云端 API Key)   │  │ (主动关心)   │  │
│  └──────┬───────┘  └─────────────────┘  └──────┬───────┘  │
│         │                                       │          │
│  ┌──────┴───────┐  ┌──────────────┐  ┌────────┴────────┐  │
│  │  记忆系统     │  │  工具系统     │  │  提示词模板   │  │
│  │BuddyMemory  │  │ BuddyTools   │  │PromptTpl     │  │
│  │(分层+遗忘)  │  │ (7种技能)    │  │              │  │
│  └──────────────┘  └──────────────┘  └───────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              JSON 数据存储（按用户隔离）                │   │
│  │  data/buddy_profile_{user_id}.json                  │   │
│  │  data/buddy_memory_{user_id}.json                   │   │
│  │  data/ai_history_{user_id}.json                     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    云端 AI 服务商                             │
│  Groq / DeepSeek / OpenAI / OpenRouter / 自定义兼容 API      │
└─────────────────────────────────────────────────────────────┘
```

### 调用链详解

**后端流式代理（优先）**：
```
用户发消息 → POST /api/buddy/chat/stream
         → 后端获取用户 AI 配置（API Key）
         → 后端 POST 到云端 AI（流式）
         → SSE 流式推送 → 前端实时显示
```

**浏览器直调（回退）**：
```
后端流式失败 → _browserDirectChat()
           → GET /api/ai-model/proxy/chat（获取配置）
           → 浏览器直调云端 AI（流式）
           → 浏览器解析 SSE
           → POST /api/ai-model/proxy/save（保存历史）
           → POST /api/buddy/analyze（情绪分析）
```

### 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Flask 3.0 + Python |
| 数据存储 | JSON 文件（按用户隔离）+ SQLite（用户认证）|
| 前端 | 原生 JavaScript SPA |
| 认证 | JWT |
| AI 调用 | OpenAI 兼容 API（云端）|
| 部署 | Docker + Gunicorn |

### 目录结构

```
StudyPal/
├── app.py                    # 应用入口
├── config.py                 # 配置中心（模型、AI、超时等）
├── requirements.txt           # 依赖
├── PRODUCT.md                 # 本文档
│
├── src/
│   ├── auth/
│   │   └── auth.py           # JWT + 用户认证服务
│   │
│   ├── buddy/                # 搭子系统核心
│   │   ├── buddy_roles.py    # 6 种角色配置 + 情绪响应映射
│   │   ├── buddy_profile.py  # 用户/搭子档案管理
│   │   ├── buddy_memory.py   # 三层记忆系统（v4.0：重要性评分+自动遗忘）
│   │   ├── buddy_tools.py    # 搭子技能工具（v4.0 新增）
│   │   └── caring_engine.py  # 主动关心引擎（11 种关心类型）
│   │
│   ├── core/
│   │   └── buddy.py          # Buddy 核心类（情绪+对话+记忆整合）
│   │
│   ├── ai/
│   │   ├── ai_helper.py      # AI 调用封装
│   │   └── prompt_templates.py # 提示词模板（v4.0：工具注入支持）
│   │
│   ├── study/
│   │   └── study_tracker.py  # 番茄钟 + 学习统计
│   │
│   ├── diary/
│   │   └── diary.py          # 情绪日记 + 情绪追踪
│   │
│   └── modules/
│       ├── ai_memory.py      # AI 对话历史管理
│       └── task_manager.py   # 任务管理
│
├── routes/                   # Flask API 路由
│   ├── buddy.py             # 搭子路由（含后端流式端点）
│   ├── ai_model.py          # AI 模型配置路由
│   ├── auth.py              # 认证路由
│   ├── study.py             # 学习追踪路由
│   ├── diary.py             # 日记路由
│   └── tasks.py             # 任务路由
│
├── static/
│   ├── css/                 # 样式文件（变量、设计令牌）
│   └── js/
│       ├── app.js           # 主应用（含 sendChat + 流式处理）
│       ├── router.js        # SPA 路由
│       └── constants.js     # 常量定义
│
├── templates/               # HTML 模板
│   ├── index.html          # 主页面
│   ├── chat.html           # 聊天页面
│   ├── home.html           # 首页
│   └── auth/               # 认证页面
│       ├── login.html
│       └── register.html
│
└── data/                    # JSON 数据存储
    ├── users.json           # 用户数据
    ├── tasks.json           # 任务数据
    ├── diary.json           # 日记数据
    └── study_tracker.json   # 学习追踪数据
```

---

## 模块详解

### 搭子核心（Buddy）

`src/core/buddy.py` — Buddy 类是整个搭子系统的核心，整合情绪、对话、记忆、关心四大子系统。

**核心方法：**

| 方法 | 说明 |
|------|------|
| `chat(message, conversation_id)` | 处理用户消息，返回回复 |
| `get_emotion() / set_emotion()` | 获取/设置当前情绪 |
| `get_lightweight_system_prompt(include_tools)` | 构建系统提示词（可选含工具） |
| `get_full_status()` | 获取搭子完整状态（供首页展示）|
| `update_emotion_by_action(action)` | 根据事件更新情绪 |

**实例池管理（v4.0）：**
```python
from src.core.buddy import get_buddy

# 按用户隔离的实例（推荐）
buddy = get_buddy(user_id="123")

# 向后兼容：全局单例（不推荐多用户场景）
buddy = get_buddy()
```

### 记忆系统（BuddyMemory）

`src/buddy/buddy_memory.py` — 三层记忆架构，参考扣子智能体设计。

| 层次 | 说明 | 容量 |
|------|------|------|
| 用户画像笔记 | 关键个人信息（目标、弱点、偏好）| 无限制 |
| 场景记忆 | 重要事件（成就/困难/情绪波动）| 自动遗忘 |
| 对话摘要 | 对话话题的提炼总结 | 按需 |

**重要性评分（v4.0 新增）：**

| 评分 | 场景类型 | 遗忘策略 |
|------|---------|---------|
| 4 | 里程碑（考上了/重大突破）| 永久保留 |
| 3 | 成就/困难 | 90 天后降级 |
| 2 | 情绪/普通对话 | 30 天后遗忘 |
| 1 | 日常闲聊 | 7 天后自动清理 |

**自动遗忘机制：**
- 30 天以上 + 从未访问 + 重要性 ≤ 1 → 自动删除
- 总场景超过 100 条 → 按遗忘分数排序删除最低分
- 遗忘分数 = age_days / (importance × 0.5 + access_count × 0.3)

**智能检索：**
```python
# smart_recall 综合考虑相关性 + 重要性 + 时效性
results = memory.smart_recall("考研", limit=5)
```

### 工具系统（BuddyTools）

`src/buddy/buddy_tools.py` — 7 种搭子技能，参考扣子智能体的工具调用设计。

| 工具名称 | 功能 | 触发场景 |
|---------|------|---------|
| `study_timer` | 开始/暂停学习计时 | "开始学习"/"暂停" |
| `get_study_stats` | 查询今日学习统计 | "今天学了多久" |
| `manage_task` | 添加/完成/查看任务 | "添加任务"/"看看待办" |
| `check_milestone` | 检查连续学习里程碑 | 达到 3/7/14/30/100 天 |
| `record_emotion` | 记录用户情绪 | 情绪波动时 |
| `search_memory` | 搜索记忆 | "你记得之前..." |
| `encourage` | 生成个性化鼓励 | 用户沮丧时 |

**工具调用格式：**
```
AI 回复末尾：
<tool_call>
{"name": "study_timer", "params": {"action": "start"}}
</tool_call>
```

### 关心引擎（CaringEngine）

`src/buddy/caring_engine.py` — 11 种主动关心类型。

| 关心类型 | 说明 | 冷却时间 |
|---------|------|---------|
| 早安问候 | 每日首次打开时的问候 | 1 天 |
| 学习提醒 | 检测到长时间未学习 | 4 小时 |
| 情绪确认 | 检测到负面情绪 | 2 小时 |
| 睡眠提醒 | 检测到深夜学习 | 1 天 |
| 休息提醒 | 连续学习超过 90 分钟 | 30 分钟 |
| 过度学习提醒 | 单日学习超 12 小时 | 1 天 |
| 深夜鼓励 | 23:00-02:00 仍在学习 | 1 天 |
| 周复盘 | 每周日推送 | 1 周 |
| 阶段鼓励 | 考试倒计时关键节点 | 1 天 |
| 成就庆祝 | 连续学习里程碑 | 1 天 |
| 任务提醒 | 待办任务堆积 | 2 小时 |

### 提示词模板（PromptTemplates）

`src/ai/prompt_templates.py` — 搭子提示词工程。

**轻量版（浏览器直调/后端流式）：**
- 仅保留搭子身份 + 极简风格描述
- 约 30-50 tokens，极速响应
- 可选注入工具说明

**完整版（后端同步调用）：**
- 含角色配置 + 口语化规则 + 学习上下文
- 约 600 tokens，适合需要完整上下文的场景

---

## API 文档

### 认证接口

#### POST /api/auth/register — 用户注册

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

#### POST /api/auth/login — 用户登录

**请求体：**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

#### GET /api/auth/me — 获取当前用户

**请求头：**
```
Authorization: Bearer <token>
```

---

### 搭子接口

#### POST /api/buddy/chat/stream — 流式对话（v4.0 新增）

**核心端点：后端统一代理 AI 调用，API Key 不暴露在前端。**

**请求头：**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体：**
```json
{
  "message": "今天心情不好",
  "conversation_id": ""
}
```

**响应：SSE 流式响应**

```
event: done
data: {"token": "回复内容"}

event: done
data: {}

---

GET /api/buddy/status — 获取搭子状态
```

#### GET /api/buddy/status — 获取搭子状态

**响应：**
```json
{
  "success": true,
  "buddy": {
    "name": "小豆",
    "emoji": "🌸",
    "emotion": "worried",
    "emotion_desc": "有点担心...",
    "role_id": "xiaodou",
    "level": 3
  },
  "stats": {
    "streak_days": 5,
    "today_minutes": 120,
    "tasks_pending": 3
  }
}
```

#### GET /api/buddy/roles — 获取所有角色

#### POST /api/buddy/role/switch — 切换角色

**请求体：**
```json
{ "role_id": "aran" }
```

#### GET /api/buddy/system-prompt — 获取系统提示词

#### GET /api/buddy/debug/prompt — 提示词调试预览（v4.0 新增）

**查询参数：**
- `include_tools=1` — 包含工具说明

**响应：**
```json
{
  "success": true,
  "buddy_info": { "name": "小豆", "role_id": "xiaodou" },
  "prompt_preview": {
    "lightweight": "你是小豆，温柔的学习伙伴...",
    "lightweight_tokens": 45,
    "with_tools": "你是小豆...\n【可用技能】...",
    "with_tools_tokens": 120
  },
  "context": { "streak_days": 5, "memory_stats": {...} },
  "tools": [...]
}
```

#### POST /api/buddy/analyze — 分析情绪并更新搭子

**请求体：**
```json
{
  "message": "今天做了三套卷子",
  "ai_reply": "太厉害了！",
  "conversation_id": "xxx"
}
```

**响应：**
```json
{
  "success": true,
  "emotion": "proud",
  "emoji": "😤",
  "emotion_desc": "为你骄傲！",
  "suggestions": ["继续保持这股劲头", "记录一下今天的收获"]
}
```

---

### 搭子设计接口

#### POST /api/buddy/custom/create — 创建自定义搭子

**请求体：**
```json
{
  "name": "小明",
  "emoji": "🤖",
  "personality": "活泼开朗",
  "relationship": "我最好的朋友",
  "speaking_style": "活泼俏皮",
  "background": "曾经是一名学霸...",
  "prompt": "（可选）完整的自定义系统提示词"
}
```

#### PUT /api/buddy/custom/update — 更新自定义搭子

#### GET /api/buddy/custom/is-custom — 检查是否为自定义搭子

#### POST /api/buddy/custom/switch — 切换到预设搭子

---

### AI 模型接口

#### GET /api/ai-model/presets — 获取预设模型列表

**响应：**
```json
{
  "success": true,
  "presets": [
    { "key": "groq_llama", "name": "Llama 3.3 70B (Groq)", "provider": "openai" },
    { "key": "deepseek_chat", "name": "DeepSeek Chat", "provider": "openai" }
  ],
  "default_key": "groq_llama"
}
```

#### GET /api/ai-model/current — 获取当前使用的模型

#### POST /api/ai-model/preset — 切换到预设模型

**请求体：**
```json
{ "model_key": "deepseek_chat" }
```

#### POST /api/ai-model/custom — 保存自定义模型配置

**请求体：**
```json
{
  "name": "我的配置",
  "base_url": "https://api.deepseek.com/v1",
  "api_key": "sk-xxx",
  "model": "deepseek-chat"
}
```

#### POST /api/ai-model/test — 测试模型连接

**请求体：**
```json
{
  "base_url": "https://api.deepseek.com/v1",
  "api_key": "sk-xxx",
  "model": "deepseek-chat"
}
```

#### DELETE /api/ai-model/custom — 删除自定义配置，恢复默认

---

## 会员体系

### 订阅等级

| 等级 | 价格 | AI 调用次数 | 功能 |
|------|------|-------------|------|
| Free | 免费 | 100 次/月 | 基础功能 |
| Pro | ¥29/月 | 1000 次/月 | 全部功能 + 优先 AI |
| VIP | ¥99/月 | 10000 次/月 | 全部功能 + 专属搭子 |

### AI 调用限制

- Free：100 次/月
- Pro：1000 次/月
- VIP：10000 次/月

---

## 部署指南

### 环境变量

创建 `.env` 文件：

```bash
SECRET_KEY=your-secure-random-key
FLASK_DEBUG=false

# AI 模型配置（至少配置一项）
# Groq（免费，推荐）
AI_API_KEY=your-groq-api-key
DEFAULT_MODEL_KEY=groq_llama

# 或 DeepSeek
# DEEPSEEK_API_KEY=your-deepseek-api-key
# DEFAULT_MODEL_KEY=deepseek_chat
```

### Docker 部署（推荐）

```bash
# 1. 编辑 .env
cp .env.example .env

# 2. 启动服务
docker-compose up -d
```

### 传统部署

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动应用
python app.py
```

---

## 版本历史

### v4.0 (2026-06-08) — AI 搭子系统重构

**架构重构：**
- **后端流式代理**：新增 `/api/buddy/chat/stream` 端点，后端统一代理 AI 调用，API Key 完全在后端，消除前端暴露风险
- **前端回退机制**：后端流式失败时自动回退到浏览器直调，保障用户体验
- **用户数据隔离**：所有 Buddy 实例和数据文件按 `user_id` 隔离，解决多用户数据混淆问题
- **记忆增强**：新增重要性评分、自动遗忘机制、智能检索（`smart_recall`）
- **工具系统**：新增 7 种搭子技能（学习计时、任务管理、里程碑检查等），参考扣子智能体设计
- **提示词工程升级**：轻量版提示词支持工具注入，AI 知道何时调用技能

**性能优化：**
- `max_tokens` 从 2048 降至 512，大幅减少生成时间
- 历史消息从 10 条减至 5 条，减少输入 token
- 为 qwen 模型禁用 Extended Thinking，防止慢速思考模式

### v3.2 (2026-05-28)

- 新增开屏动效
- 重构应用页 UI（Bento 网格布局）
- 自定义搭子设计器
- 增强 AI 模型配置界面

### v3.1 (2026-05-27)

- 新增搭子设计器
- 新增进阶提示词
- 增强 AI 模型配置
- 重构设置页面

### v3.0 (2026-05-21)

- 新增用户认证系统（JWT）
- 迁移到 SQLAlchemy ORM
- 新增多用户数据隔离
- 新增订阅会员体系

### v2.0 (2026-04-30)

- 重构为 Flask Web 应用
- 新增番茄钟功能
- 新增情绪日记
- 新增成就系统

### v1.0 (2026-04-13)

- CLI 版本发布
