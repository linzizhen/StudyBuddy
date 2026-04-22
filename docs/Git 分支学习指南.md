# Git 分支学习指南

## 一、什么是分支？

分支（Branch）是 Git 的核心功能之一，它允许你在独立的工作线上进行开发，而不会影响主分支（通常是 `main` 或 `master`）。

### 分支的作用：
- **隔离开发**：在新功能开发时不影响主代码
- **并行工作**：多人可以同时在不同分支上工作
- **实验安全**：尝试新功能失败也不会破坏主分支
- **代码审查**：通过 Pull Request 进行代码审核

---

## 二、常用 Git 分支命令

### 1. 查看分支

```bash
# 查看本地所有分支
git branch

# 查看所有分支（包括远程）
git branch -a

# 查看远程分支
git branch -r
```

### 2. 创建分支

```bash
# 创建新分支（不切换）
git branch <分支名>

# 创建并切换到新分支
git checkout -b <分支名>

# 推荐方式（Git 2.23+）
git switch -c <分支名>
```

### 3. 切换分支

```bash
# 切换到指定分支
git checkout <分支名>

# 推荐方式（Git 2.23+）
git switch <分支名>
```

### 4. 删除分支

```bash
# 删除本地分支（安全删除，未合并会警告）
git branch -d <分支名>

# 强制删除本地分支（即使未合并）
git branch -D <分支名>

# 删除远程分支
git push origin --delete <分支名>
```

### 5. 重命名分支

```bash
# 重命名当前分支
git branch -m <新名称>

# 重命名指定分支
git branch -m <旧名称> <新名称>
```

---

## 三、分支工作流程

### 典型开发流程：

```
1. 从主分支创建新分支
   git checkout main
   git pull origin main
   git checkout -b feature/new-feature

2. 在新分支上开发
   # 编写代码
   git add .
   git commit -m "添加新功能"

3. 推送分支到远程
   git push -u origin feature/new-feature

4. 创建 Pull Request（在 GitHub 网页上）
   - 访问仓库页面
   - 点击 "Compare & pull request"
   - 描述更改内容
   - 提交 PR

5. 代码审查和合并
   - 同事 review 代码
   - 修复问题
   - 合并到主分支

6. 删除已合并的分支
   git branch -d feature/new-feature
   git push origin --delete feature/new-feature
```

---

## 四、合并分支

### 合并方式：

#### 1. Fast-Forward 合并（快进合并）
当目标分支没有新提交时，Git 会直接移动指针。

```bash
git checkout main
git merge feature-branch
```

#### 2. Three-Way Merge（三路合并）
当两个分支都有新提交时，Git 会创建合并提交。

```bash
git checkout main
git merge feature-branch
```

#### 3. Rebase（变基）
将分支的提交" replay"到另一个分支上，保持线性历史。

```bash
git checkout feature-branch
git rebase main
```

### 处理合并冲突：

当两个分支修改了同一文件的同一部分时，会产生冲突：

```
<<<<<<< HEAD
你的修改
=======
对方的修改
>>>>>>> feature-branch
```

**解决步骤：**
1. 手动编辑文件，选择保留哪部分代码
2. 删除冲突标记（<<<<<<<, =======, >>>>>>>）
3. 添加解决后的文件
4. 完成合并

```bash
git add <文件路径>
git commit  # 如果 merge 时没有加 --no-edit
```

---

## 五、GitHub 上的分支操作

### 在 GitHub 网页上：

1. **查看分支**
   - 点击仓库顶部的 "Branch: main" 下拉菜单
   - 可以看到所有分支列表

2. **创建分支**
   - 从任意分支或提交创建
   - 点击 "Branch" 下拉菜单
   - 输入新分支名
   - 点击 "Create branch: xxx"

3. **比较和 Pull Request**
   - 点击 "Pull requests" 标签
   - 点击 "New pull request"
   - 选择基准分支和比较分支
   - 填写 PR 描述
   - 创建 PR

4. **合并 Pull Request**
   - 审查更改
   - 点击 "Merge pull request"
   - 确认合并
   - 删除源分支（可选）

---

## 六、最佳实践

### 分支命名规范：
- `feature/xxx` - 新功能
- `bugfix/xxx` - 修复 bug
- `hotfix/xxx` - 紧急修复
- `docs/xxx` - 文档更新
- `refactor/xxx` - 代码重构

### 分支管理：
- 定期同步主分支到你的功能分支
- 及时删除已合并的分支
- 保持分支简洁，不要过大
- 编写清晰的提交信息

### 协作流程：
1. 拉取最新的主分支代码
2. 基于主分支创建功能分支
3. 开发并提交
4. 推送并创建 PR
5. 等待审查和合并

---

## 七、练习任务

现在让我们在你的项目中进行实际操作练习！
