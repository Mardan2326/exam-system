# Git 版本控制说明

## 📦 当前状态

✅ Git 仓库已初始化
✅ 所有修复已提交到版本控制

## 📝 提交记录

```
e0e84ec - 修复DeepSeek PDF解析问题
```

### 本次提交包含的文件：
- ✅ `Exam.html` - 前端页面（已优化）
- ✅ `server.py` - Flask 后端服务器（已优化）
- ✅ `utils.py` - LLM 调用工具（已优化）
- ✅ `README_修复说明.md` - 详细修复说明
- ✅ `.gitignore` - Git 忽略规则

## 🔍 查看提交详情

```bash
# 查看提交历史
git log

# 查看简洁的提交历史
git log --oneline

# 查看某个文件的修改历史
git log --follow Exam.html

# 查看具体的修改内容
git show e0e84ec
```

## 📊 查看修改内容

```bash
# 查看工作区状态
git status

# 查看所有修改的差异
git diff

# 查看已暂存的差异
git diff --staged
```

## 🔄 常用 Git 命令

### 添加和提交
```bash
# 添加所有修改的文件
git add .

# 添加特定文件
git add Exam.html server.py

# 提交修改
git commit -m "提交说明"

# 修改上一次提交
git commit --amend
```

### 分支管理
```bash
# 创建新分支
git branch feature/new-feature

# 切换分支
git checkout feature/new-feature

# 创建并切换到新分支
git checkout -b feature/new-feature

# 查看所有分支
git branch -a
```

### 回退操作
```bash
# 撤销工作区的修改
git checkout -- filename

# 撤销暂存区的修改
git reset HEAD filename

# 回退到上一个版本
git reset --hard HEAD^

# 回退到指定版本
git reset --hard e0e84ec
```

## 🌐 远程仓库（可选）

### 关联远程仓库
```bash
# 关联 GitHub 仓库
git remote add origin https://github.com/yourusername/exam-parser.git

# 推送到远程仓库
git push -u origin master

# 查看远程仓库
git remote -v
```

### 从远程仓库更新
```bash
# 拉取最新代码
git pull origin master

# 克隆仓库
git clone https://github.com/yourusername/exam-parser.git
```

## 📋 建议的工作流程

### 日常开发
1. 创建功能分支
   ```bash
   git checkout -b feature/add-progress-bar
   ```

2. 进行开发和测试

3. 提交修改
   ```bash
   git add .
   git commit -m "添加进度条功能"
   ```

4. 合并到主分支
   ```bash
   git checkout master
   git merge feature/add-progress-bar
   ```

### 修复 Bug
1. 创建修复分支
   ```bash
   git checkout -b bugfix/fix-timeout
   ```

2. 修复问题并提交
   ```bash
   git add .
   git commit -m "修复超时问题"
   ```

3. 合并到主分支
   ```bash
   git checkout master
   git merge bugfix/fix-timeout
   ```

## 🔖 标签管理

```bash
# 创建标签
git tag v1.0.0

# 创建带注释的标签
git tag -a v1.0.0 -m "第一个稳定版本"

# 查看所有标签
git tag

# 推送标签到远程
git push origin v1.0.0
```

## 📦 当前项目建议

### 下一步可以做：

1. **创建功能分支进行新功能开发**
   ```bash
   git checkout -b feature/progress-bar
   ```

2. **设置远程仓库备份**
   - GitHub
   - GitLab
   - Gitee

3. **添加更多文档**
   - API 文档
   - 开发者指南
   - 部署说明

4. **使用标签标记版本**
   ```bash
   git tag -a v1.0.0 -m "DeepSeek PDF解析修复版本"
   ```

## ⚠️ 注意事项

- ❌ 不要提交 `.pdf` 文件（已在 .gitignore 中排除）
- ❌ 不要提交 API Key（确保使用环境变量）
- ❌ 不要提交临时文件（已在 .gitignore 中排除）
- ✅ 每次提交前检查 `git status`
- ✅ 提交信息要清晰明确
- ✅ 定期推送到远程仓库备份

---

**Git 版本控制已就绪！** 🎉
