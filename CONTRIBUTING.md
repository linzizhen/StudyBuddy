# Contributing to StudyPal

感谢您对 StudyPal 的关注！欢迎提交 Pull Request。

## 开发环境设置

```bash
# 克隆项目
git clone https://github.com/linzizhen/StudyBuddy.git
cd StudyBuddy

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
python app.py
```

## 代码规范

### Python

- 遵循 [PEP 8](https://pep8.org/) 规范
- 使用中文注释
- 模块和函数添加 docstring
- 变量和函数名使用英文

### JavaScript

- 遵循现有代码风格
- 使用 ES6+ 语法
- 使用中文注释

### CSS

- 使用 CSS 变量（`variables.css`）
- 组件样式放在 `components.css`
- 移动端样式放在 `mobile.css`

## 分支命名

| 类型 | 命名格式 | 示例 |
|------|----------|------|
| 功能 | `feature/功能名称` | `feature/ai-model-config` |
| 修复 | `fix/问题描述` | `fix/chat-timeout` |
| 重构 | `refactor/模块名称` | `refactor/auth-system` |
| 文档 | `docs/文档类型` | `docs/api-reference` |

## 提交规范

提交信息遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Type 类型

| Type | 说明 |
|------|------|
| `feat` | 新功能 |
| `fix` | Bug 修复 |
| `docs` | 文档更新 |
| `style` | 代码格式（不影响功能） |
| `refactor` | 重构 |
| `perf` | 性能优化 |
| `test` | 测试相关 |
| `chore` | 构建/工具相关 |

### 示例

```bash
# 新功能
git commit -m "feat(ai-model): 添加自定义模型配置功能"

# Bug 修复
git commit -m "fix(chat): 修复超时后无法重连问题"

# 文档更新
git commit -m "docs: 更新 API 文档"
```

## Pull Request 流程

1. **Fork** 项目到您的 GitHub 账号
2. **创建分支**：`git checkout -b feature/your-feature`
3. **开发并测试**
4. **提交**：`git commit -m "feat: 添加新功能"`
5. **推送**：`git push origin feature/your-feature`
6. **创建 Pull Request**

### PR 描述模板

```markdown
## 描述
简要说明这次更改的内容

## 更改类型
- [ ] 新功能 (feat)
- [ ] Bug 修复 (fix)
- [ ] 文档更新 (docs)
- [ ] 代码重构 (refactor)

## 测试
- [ ] 已测试新功能
- [ ] 已测试相关功能

## 截图（如有 UI 变更）
```

## 问题反馈

如果您发现 Bug 或有新功能建议，请：

1. 搜索现有 [Issues](https://github.com/linzizhen/StudyBuddy/issues)
2. 创建新的 Issue，包含：
   - 清晰的问题描述
   - 复现步骤
   - 预期行为
   - 环境信息（浏览器、操作系统等）

## 许可证

通过提交 Pull Request，您同意您的代码遵循 [MIT License](LICENSE)。
