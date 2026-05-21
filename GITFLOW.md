# StudyPal Git 工作流规范

## 分支策略

我们采用 **Git Flow** 分支模型，针对本项目特点进行了简化：

```
main (生产环境)
├── develop (开发环境)
│   ├── feature/xxx (功能分支)
│   ├── fix/xxx (修复分支)
│   └── release/xxx (发布分支)
└── hotfix/xxx (紧急修复)
```

### 分支命名规范

| 分支类型 | 命名格式 | 示例 |
|----------|----------|------|
| 功能分支 | `feature/功能名称` | `feature/multi-buddy-roles` |
| 修复分支 | `fix/问题描述` | `fix/login-timeout` |
| 发布分支 | `release/版本号` | `release/v3.0.0` |
| 紧急修复 | `hotfix/问题描述` | `hotfix/security-patch` |

---

## 开发流程

### 1. 开始新功能

```bash
# 确保在最新 develop 分支
git checkout develop
git pull origin develop

# 创建功能分支
git checkout -b feature/新功能名称

# 开发完成后，提交到远程
git add .
git commit -m "feat: 描述"
git push -u origin feature/新功能名称
```

### 2. 提交规范

我们使用 **Conventional Commits** 规范：

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

**类型 (type)：**

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(buddy): 添加角色切换功能` |
| `fix` | 修复 Bug | `fix(chat): 修复消息发送失败问题` |
| `docs` | 文档更新 | `docs: 更新 API 文档` |
| `style` | 代码格式 | `style: 格式化代码` |
| `refactor` | 重构 | `refactor: 重构认证模块` |
| `perf` | 性能优化 | `perf: 优化数据库查询` |
| `test` | 测试 | `test: 添加单元测试` |
| `chore` | 构建/工具 | `chore: 更新依赖` |

**示例：**

```bash
# 好
git commit -m "feat(buddy): 添加角色切换功能"
git commit -m "fix(auth): 修复 Token 过期后无法刷新问题"
git commit -m "docs(api): 添加会员订阅接口文档"

# 不好
git commit -m "更新代码"
git commit -m "fix bug"
git commit -m "WIP"
```

### 3. 发起 Pull Request

1. 在 GitHub 打开 Pull Request
2. 填写 PR 模板
3. 指定 Reviewer
4. 关联 Issue（可选）

**PR 模板：**

```markdown
## 描述
[简要描述这个 PR 的内容]

## 改动
- [改动点1]
- [改动点2]

## 测试
- [ ] 已通过本地测试
- [ ] 已添加相关测试
- [ ] 已更新文档

## 截图（UI 改动）
```

### 4. Code Review

- 至少 1 人 Review 通过才能合并
- Reviewer 需要检查：
  - 代码逻辑是否正确
  - 是否有安全风险
  - 是否符合项目规范
  - 是否有测试覆盖

---

## 发布流程

### 版本号规范

采用 **SemVer** 语义化版本：

```
主版本.次版本.修订号
  v3    .  0   .  0
```

- **主版本 (major)**: 不兼容的 API 变更
- **次版本 (minor)**: 向后兼容的新功能
- **修订号 (patch)**: 向后兼容的问题修复

### 发布步骤

1. **创建发布分支：**
```bash
git checkout develop
git pull
git checkout -b release/v3.0.0
```

2. **更新版本号：**
```bash
# 更新 app.py 中的版本号
# 更新 CHANGELOG.md
git commit -m "chore: bump version to v3.0.0"
```

3. **测试和修复：**
```bash
# 测试完成后
git checkout main
git merge release/v3.0.0 --no-ff
git tag -a v3.0.0 -m "Release v3.0.0"
git push origin main --tags
```

4. **合并回 develop：**
```bash
git checkout develop
git merge release/v3.0.0 --no-ff
git push origin develop
```

5. **清理：**
```bash
git branch -d release/v3.0.0
git push origin --delete release/v3.0.0
```

---

## 紧急修复流程

### Hotfix 流程

```bash
# 从 main 创建 hotfix 分支
git checkout main
git pull
git checkout -b hotfix/问题描述

# 修复并测试
git commit -m "fix: 修复安全问题"

# 合并到 main
git checkout main
git merge hotfix/问题描述 --no-ff
git tag -a v3.0.1 -m "Hotfix v3.0.1"
git push origin main --tags

# 合并到 develop
git checkout develop
git merge hotfix/问题描述 --no-ff
git push origin develop

# 删除 hotfix 分支
git branch -d hotfix/问题描述
```

---

## Git Hooks

项目使用 pre-commit hooks 确保代码质量：

### 安装

```bash
pip install pre-commit
pre-commit install
```

### 检查内容

- Python 语法检查
- 敏感信息检查
- 提交信息格式检查
- 大文件检查

---

## 常用 Git 命令速查

```bash
# 查看状态
git status

# 查看分支
git branch -a

# 切换分支
git checkout 分支名

# 创建并切换
git checkout -b 新分支名

# 添加改动
git add 文件路径    # 单个文件
git add .          # 所有改动

# 提交
git commit -m "提交信息"

# 拉取更新
git pull origin 分支名

# 推送
git push origin 分支名

# 查看提交历史
git log --oneline -10

# 撤销未提交的改动
git checkout -- 文件路径

# 撤销已提交的 commit
git revert commit_id

# 暂存当前改动
git stash

# 恢复暂存的改动
git stash pop
```

---

## 注意事项

1. **不要直接 push 到 main/develop**
2. **每次 commit 前先 pull**
3. **PR 描述要详细**
4. **保持 commit 粒度适中**（不要积累太多改动再提交）
5. **及时清理已合并的分支**
