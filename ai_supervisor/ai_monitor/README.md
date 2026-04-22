# AI监督系统模块（ai_monitor）

用于检测用户学习专注度的Python模块，可独立运行和测试。

## 功能特性

- 📷 **摄像头检测**：使用OpenCV检测人脸，判断用户是否在场
- 🖥️ **行为检测**：监控活跃窗口，使用白名单机制判断是否为学习软件
- 🔄 **切换检测**：统计窗口切换次数，频繁切换视为分心
- ⏱️ **时间分析**：记录专注时长，统计各状态时间占比
- 📊 **专注度评分**：综合多因素计算0-100评分
- 💬 **提醒功能**：状态变化时发送提醒

## 安装

```bash
pip install opencv-python-headless psutil pywin32
```

## 快速开始

```bash
cd ai_monitor
python demo.py
```

## 测试模式

```bash
python demo.py -t  # 运行简单测试（不依赖摄像头）
```

## 依赖

- opencv-python-headless >= 4.5.0
- psutil >= 5.8.0
- pywin32 >= 300 （仅Windows）

## 配置

编辑 `config.py` 修改所有阈值和参数：
- 摄像头配置
- 人脸检测参数
- 学习软件白名单
- 评分权重
- 提醒配置
