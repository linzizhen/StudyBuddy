# 📚 StudyPal 项目文档

## 项目概述
StudyPal 是一个桌面 AI 宠物，旨在解决大学生学习拖延、遇到问题无人解答以及宿舍学习孤独的问题。它既是学习监督工具，也是情感陪伴伙伴。

---

## 产品概念单页

### 产品名称
**StudyPal**

### 一句话 Slogan
你的桌面 AI 宠物，也是你的学习搭子

---

### 用户痛点
| 痛点 | 描述 |
|------|------|
| 学习拖延 | 想学习但总忍不住刷手机，缺乏监督 |
| 无人答疑 | 自习遇到难题卡住，不好意思总问同学 |
| 孤独感 | 一个人学习容易分心，缺少陪伴 |

---

### 解决方案
| 功能 | 描述 | AI 技术 |
|------|------|--------|
| 学习监督 | 设定学习时间，定时提醒；玩手机太久它会"难过" | 状态机 + 计时器 |
| 智能问答 | 语音/文字提问，实时解答学习问题 | 大模型 (LLM) |
| 情绪陪伴 | 完成任务开心，陪你聊天，记住你的信息 | TTS 语音 + 情绪算法 |
| 表情反馈 | 屏幕显示😊😴😡等情绪状态 | 表情动画系统 |

---

### AI 参与度
| 环节 | AI 工具 | Prompt 示例 |
|------|--------|------------|
| 创意发散 | ChatGPT | "我是一名大一学生，想做一个桌面 AI 宠物，解决学习拖延和孤独问题，给我 10 个创意" |
| 代码框架 | Claude | "用 Python 写一个桌面宠物程序，有表情变化、学习计时器、AI 问答功能" |
| 产品概念图 | Midjourney | "可爱卡通风格的桌面机器人，像大白，白色胖乎乎，圆形屏幕显示😊表情，放在宿舍书桌上" |
| 演讲稿 | DeepSeek | "帮我写一份 5 分钟课堂演讲脚本，介绍 StudyPal 项目" |

> *（附上 Prompt 截图）*

---

## 可视化原型

### 产品概念图
![alt text](<皮克斯风格桌面机器人场景 (1).png>)
*风格：可爱卡通（大白风格），白色胖乎乎机器人，圆形屏幕显示😊表情，放在宿舍书桌上*

**演示内容**：
1. 打开 StudyPal 程序
2. 表情初始状态😴
3. 输入问题"高数怎么学"
4. AI 回答，表情变为😊
5. 点击"开始学习"，表情变为📚

---

## 技术方案

### 技术栈
| 组件 | 技术选型 |
|------|----------|
| 语言 | Python 3.9+ |
| GUI 框架 | Flask (Web 界面) / Tkinter (桌面版) |
| AI 能力 | DeepSeek API / GPT API |
| 语音 | Google TTS / Edge TTS |
| 打包 | PyInstaller |

### 项目结构
```
StudyPal/
├── main.py              # 主程序入口
├── app.py               # Flask Web 应用
├── buddy.py             # Buddy 类（表情 + 情绪）
├── ai_helper.py         # AI 问答功能
├── timer.py             # 学习计时器（番茄钟）
├── task_manager.py      # 任务管理模块
├── study_calendar.py    # 学习日历模块
├── data_manager.py      # 数据持久化管理
├── config.py            # 配置文件
├── requirements.txt     # 依赖包
├── assets/              # 资源文件
│   ├── happy.png
│   ├── sad.png
│   └── study.mp3
├── data/                # 数据文件
│   ├── study_log.json   # 学习记录
│   ├── tasks.json       # 任务数据
│   └── user_settings.json # 用户设置
├── templates/           # HTML 模板
│   └── index.html
└── docs/                # 文档
    └── README.md
```

---

## 功能模块详解

### 1. 主应用 (app.py)
Flask Web 应用，提供 RESTful API 和 Web 界面：
- `/` - 主页
- `/api/status` - 获取状态
- `/api/ask` - AI 问答
- `/api/timer/start` - 开始计时
- `/api/timer/stop` - 停止计时
- `/api/tasks` - 任务管理
- `/api/calendar` - 学习日历

### 2. 情绪管理 (buddy.py)
管理宠物情绪状态和表情变化：
- **情绪状态**：idle(😴), happy(😊), sad(😢), study(📚), thinking(🤔), angry(😡), excited(🎉), sleepy(😪), proud(😤)
- **自动情绪更新**：根据用户动作和时间自动切换
- **联动功能**：与计时器、任务管理器联动

### 3. 学习计时器 (timer.py)
番茄钟和学习监督功能：
- **番茄钟模式**：25 分钟学习 + 5 分钟休息
- **每日目标**：可设置每日学习时长目标
- **空闲检测**：检测用户是否在学习或玩手机
- **休息提醒**：连续学习提醒休息

### 4. 任务管理 (task_manager.py)
管理今日任务和截止时间：
- **任务 CRUD**：添加、更新、删除任务
- **截止时间提醒**：快到截止时间提醒
- **任务统计**：完成率、逾期任务统计

### 5. 学习日历 (study_calendar.py)
记录学习数据和统计：
- **学习记录**：每日学习时长、次数
- **连续学习统计**：计算连续学习天数
- **周/月统计**：按周、月查看学习数据
- **日历视图**：可视化展示学习日历

### 6. 数据持久化 (data_manager.py)
JSON 文件存储用户数据：
- **用户设置**：座右铭、每日目标等
- **学习记录**：每日学习时长
- **任务数据**：任务列表和状态

### 7. AI 助手 (ai_helper.py)
调用大模型 API 回答问题：
- **API 调用**：支持 OpenAI 兼容接口
- **模拟回答**：API 不可用时使用预设回答
- **系统提示词**：可爱简短的回答风格

---

## 情绪状态详解

| 情绪 | Emoji | 触发条件 |
|------|-------|----------|
| idle | 😴 | 默认空闲状态 |
| happy | 😊 | 完成任务、收到 AI 回答 |
| sad | 😢 | 太久没学习 |
| study | 📚 | 开始学习时 |
| thinking | 🤔 | AI 回答中 |
| angry | 😡 | 一直玩手机 |
| excited | 🎉 | 完成学习目标 |
| sleepy | 😪 | 深夜学习 (23:00-6:00) |
| proud | 😤 | 连续学习 3 次以上 |

---

## API 接口文档

### 获取状态
```
GET /api/status
```
返回当前宠物状态、学习进度等信息。

### AI 问答
```
POST /api/ask
Content-Type: application/json

{
    "question": "高数怎么学？"
}
```

### 开始计时
```
POST /api/timer/start
{
    "duration": 25
}
```

### 任务管理
```
GET /api/tasks - 获取任务列表
POST /api/tasks - 添加任务
PUT /api/tasks/<id> - 更新任务
DELETE /api/tasks/<id> - 删除任务
```

---

## 配置说明

### config.py 配置项
| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| API_BASE | "" | AI API 地址 |
| API_KEY | "" | API 密钥 |
| MODEL_NAME | "gpt-4o-mini" | 模型名称 |
| DEFAULT_TIMER_MINUTES | 25 | 默认计时器时长 |
| DAILY_GOAL_MINUTES | 120 | 每日学习目标 |
| REMINDER_BEFORE_MINUTES | 30 | 提醒提前时间 |

---

## 运行方式

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行应用
```bash
python main.py
# 或
python app.py
```

### 访问界面
打开浏览器访问 `http://localhost:5000`

---

## 未来规划

### 短期目标
- [ ] 添加语音输入/输出功能
- [ ] 实现桌面悬浮窗模式
- [ ] 添加学习数据统计图表

### 长期目标
- [ ] 支持多用户
- [ ] 添加学习社区功能
- [ ] 实现个性化宠物形象定制
