# Git 工作流技能

## 触发条件
- 关键词：Git、分支、提交、PR、merge、rebase、commit、版本控制
- 场景：当用户需要进行版本控制操作时

## 核心规范

### 规范1：分支命名规范

| 分支类型 | 命名格式 | 示例 |
|---------|---------|------|
| 主分支 | main/master | main |
| 开发分支 | develop | develop |
| 功能分支 | feature/功能名 | feature/user-login |
| 修复分支 | fix/问题描述 | fix/login-error |
| 热修复 | hotfix/问题描述 | hotfix/security-patch |
| 发布分支 | release/版本号 | release/v1.0.0 |

### 规范2：提交信息规范

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Type 类型
| 类型 | 说明 |
|------|------|
| feat | 新功能 |
| fix | 修复 Bug |
| docs | 文档更新 |
| style | 代码格式（不影响功能） |
| refactor | 重构（不是新功能也不是修复） |
| perf | 性能优化 |
| test | 测试相关 |
| chore | 构建/工具相关 |

#### 示例
```bash
# 新功能
git commit -m "feat(apitest): 添加测试用例批量导入功能"

# 修复
git commit -m "fix(login): 修复登录超时问题"

# 文档
git commit -m "docs: 更新 API 文档"

# 重构
git commit -m "refactor(service): 重构用户服务层代码"
```

### 规范3：常用 Git 命令

```bash
# 分支操作
git branch                      # 查看本地分支
git branch -a                   # 查看所有分支
git checkout -b feature/xxx     # 创建并切换分支
git checkout main               # 切换分支
git branch -d feature/xxx       # 删除本地分支
git push origin --delete xxx    # 删除远程分支

# 提交操作
git add .                       # 暂存所有修改
git commit -m "message"         # 提交
git commit --amend              # 修改上次提交
git push origin branch-name     # 推送到远程

# 同步操作
git fetch origin                # 获取远程更新
git pull origin main            # 拉取并合并
git pull --rebase origin main   # 拉取并变基

# 合并操作
git merge feature/xxx           # 合并分支
git rebase main                 # 变基到 main

# 撤销操作
git reset --soft HEAD^          # 撤销提交，保留修改
git reset --hard HEAD^          # 撤销提交，丢弃修改
git checkout -- file            # 撤销文件修改
git stash                       # 暂存当前修改
git stash pop                   # 恢复暂存的修改

# 查看历史
git log --oneline               # 简洁历史
git log --graph                 # 图形化历史
git diff                        # 查看差异
git blame file                  # 查看文件修改历史
```

### 规范4：工作流程

```
1. 从 main 创建功能分支
   git checkout main
   git pull origin main
   git checkout -b feature/xxx

2. 开发并提交
   git add .
   git commit -m "feat: xxx"

3. 推送到远程
   git push origin feature/xxx

4. 创建 Pull Request

5. 代码审查通过后合并

6. 删除功能分支
   git checkout main
   git pull origin main
   git branch -d feature/xxx
```

### 规范5：冲突解决

```bash
# 1. 拉取最新代码
git fetch origin
git rebase origin/main

# 2. 解决冲突
# 编辑冲突文件，保留需要的代码

# 3. 标记冲突已解决
git add .

# 4. 继续变基
git rebase --continue

# 5. 推送（可能需要强制）
git push origin feature/xxx --force-with-lease
```

### 规范6：.gitignore 配置

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
.eggs/
venv/
.env

# Node
node_modules/
dist/
.npm

# IDE
.idea/
.vscode/
*.swp

# 日志
*.log
logs/

# 系统文件
.DS_Store
Thumbs.db

# 本地配置
*.local
.env.local
```

## 禁止事项
- ❌ 直接在 main 分支开发
- ❌ 提交敏感信息（密码、密钥）
- ❌ 提交大文件（超过 10MB）
- ❌ 强制推送到公共分支
- ❌ 提交信息不规范

## 检查清单
- [ ] 是否从最新 main 创建分支
- [ ] 提交信息是否规范
- [ ] 是否有敏感信息
- [ ] 是否解决了所有冲突
- [ ] 是否通过代码审查
