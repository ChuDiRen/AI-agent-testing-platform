# Git 工作流技能

## 触发条件
当用户提到：Git、分支、提交、PR、merge、rebase、commit

## 分支策略

### Git Flow
```
main        ─────●─────────────●─────────────●───→
                 ↑             ↑             ↑
release    ─────●───●─────────●───●─────────●───→
                ↑   ↑         ↑   ↑
develop    ●───●───●───●───●───●───●───●───●───→
           ↑       ↑       ↑       ↑
feature    ●───●───●       ●───●───●
```

| 分支 | 用途 | 命名 |
|------|------|------|
| main | 生产环境 | main |
| develop | 开发环境 | develop |
| feature | 功能开发 | feature/xxx |
| release | 发布准备 | release/v1.0.0 |
| hotfix | 紧急修复 | hotfix/xxx |

### 简化流程（小团队）
```
main      ─────●─────────────●─────────────●───→
               ↑             ↑             ↑
feature   ●───●───●     ●───●───●     ●───●───●
```

## 常用命令

### 分支操作
```bash
# 创建分支
git checkout -b feature/user-login

# 切换分支
git checkout develop

# 查看分支
git branch -a

# 删除分支
git branch -d feature/user-login      # 本地
git push origin --delete feature/xxx  # 远程

# 合并分支
git checkout develop
git merge feature/user-login

# 变基
git checkout feature/user-login
git rebase develop
```

### 提交操作
```bash
# 暂存
git add .
git add file.py

# 提交
git commit -m "feat: 添加用户登录功能"

# 修改最后一次提交
git commit --amend -m "新的提交信息"

# 撤销暂存
git reset HEAD file.py

# 撤销修改
git checkout -- file.py

# 撤销提交（保留修改）
git reset --soft HEAD~1

# 撤销提交（丢弃修改）
git reset --hard HEAD~1
```

### 远程操作
```bash
# 拉取
git pull origin develop
git pull --rebase origin develop  # 变基方式

# 推送
git push origin feature/user-login

# 强制推送（慎用）
git push -f origin feature/user-login

# 查看远程
git remote -v
```

### 暂存操作
```bash
# 暂存当前修改
git stash

# 暂存并添加说明
git stash save "work in progress"

# 查看暂存列表
git stash list

# 恢复暂存
git stash pop        # 恢复并删除
git stash apply      # 恢复但保留

# 删除暂存
git stash drop
git stash clear      # 清空所有
```

## 提交规范

### Commit Message 格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型
| 类型 | 说明 | 示例 |
|------|------|------|
| feat | 新功能 | feat: 添加用户登录 |
| fix | 修复 Bug | fix: 修复登录失败问题 |
| docs | 文档 | docs: 更新 API 文档 |
| style | 格式 | style: 格式化代码 |
| refactor | 重构 | refactor: 重构用户模块 |
| perf | 性能 | perf: 优化查询性能 |
| test | 测试 | test: 添加单元测试 |
| chore | 构建/工具 | chore: 更新依赖 |

### 示例
```bash
# 简单提交
git commit -m "feat: 添加用户登录功能"

# 详细提交
git commit -m "feat(user): 添加用户登录功能

- 实现用户名密码登录
- 添加 JWT Token 生成
- 添加登录日志记录

Closes #123"
```

## 常见场景

### 1. 功能开发
```bash
# 1. 创建功能分支
git checkout develop
git pull origin develop
git checkout -b feature/user-login

# 2. 开发并提交
git add .
git commit -m "feat: 添加用户登录功能"

# 3. 推送到远程
git push origin feature/user-login

# 4. 创建 PR/MR 合并到 develop
```

### 2. 修复 Bug
```bash
# 1. 创建修复分支
git checkout main
git pull origin main
git checkout -b hotfix/login-error

# 2. 修复并提交
git add .
git commit -m "fix: 修复登录失败问题"

# 3. 合并到 main 和 develop
git checkout main
git merge hotfix/login-error
git checkout develop
git merge hotfix/login-error
```

### 3. 解决冲突
```bash
# 1. 拉取最新代码
git pull origin develop

# 2. 如果有冲突，手动解决
# 编辑冲突文件，删除 <<<<<<< ======= >>>>>>> 标记

# 3. 标记已解决
git add .
git commit -m "merge: 解决冲突"

# 4. 继续推送
git push origin feature/xxx
```

### 4. 回滚代码
```bash
# 回滚到指定提交
git revert <commit-hash>

# 回滚最近一次提交
git revert HEAD

# 强制回滚（会丢失历史）
git reset --hard <commit-hash>
git push -f origin main  # 慎用！
```

### 5. Cherry-pick
```bash
# 将某个提交应用到当前分支
git cherry-pick <commit-hash>

# 应用多个提交
git cherry-pick <hash1> <hash2>
```

## 查看历史

```bash
# 查看提交历史
git log --oneline

# 图形化历史
git log --oneline --graph --all

# 查看某文件历史
git log --oneline -- file.py

# 查看某次提交
git show <commit-hash>

# 查看差异
git diff                    # 工作区 vs 暂存区
git diff --staged           # 暂存区 vs 最新提交
git diff develop..feature   # 分支差异
```

## .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
.env
venv/

# Node
node_modules/
dist/

# IDE
.idea/
.vscode/
*.swp

# 日志
logs/
*.log

# 系统文件
.DS_Store
Thumbs.db
```

## 注意事项
1. 提交前先 pull，避免冲突
2. 不要直接在 main/develop 上开发
3. 提交信息要清晰有意义
4. 敏感信息不要提交到仓库
5. 大文件使用 Git LFS
