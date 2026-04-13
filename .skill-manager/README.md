# 🚀 Hermes Skill Manager

参考空格的开源方案，为 Hermes Agent 设计的 Skill 管理系统。

---

## 📐 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Hermes Skill Manager                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   本地管理    │    │   分类组织    │    │   云端同步    │  │
│  │  skill-manager│───▶│  12个分类目录 │───▶│  GitHub仓库  │  │
│  │   .py       │    │  config.json │    │  自动备份    │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                   │          │
│         ▼                   ▼                   ▼          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  命令行工具   │    │  软链接分发   │    │  版本控制    │  │
│  │  list/search │    │  link命令    │    │  git同步     │  │
│  │  sync/backup │    │  项目复用    │    │  多端共享    │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              ~/.hermes/skills/  (全局目录)                  │
│  ├─ 01-coding-dev/      # 代码开发                          │
│  ├─ 02-ai-agents/       # AI Agent                          │
│  ├─ 03-mlops/           # MLOps                             │
│  ├─ 04-content/         # 内容创作                          │
│  ├─ 05-research/        # 研究信息                          │
│  ├─ 06-productivity/    # 效率工具                          │
│  ├─ 07-smart-home/      # 智能家居                          │
│  ├─ 08-social/          # 社交媒体                          │
│  ├─ 09-tools/           # 工具实用                          │
│  ├─ 10-gaming/          # 游戏相关                          │
│  ├─ 11-security/        # 安全相关                          │
│  └─ 99-integrations/    # 第三方集成                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 核心功能

| 功能 | 命令 | 说明 |
|------|------|------|
| 📋 列出 Skills | `list` | 显示所有 skills 及状态 |
| 📁 分类查看 | `list <分类>` | 按分类查看 skills |
| 🔍 搜索 | `search <关键词>` | 快速查找 skill |
| ℹ️ 详情 | `info <skill>` | 查看 skill 详细信息 |
| 🔗 软链接 | `link <skill>` | 创建项目级软链接 |
| ☁️ GitHub 同步 | `sync` | 推送到 GitHub |
| 💾 本地备份 | `backup` | 创建压缩备份 |
| 🗂️ 整理检查 | `organize` | 自动分类检查 |

---

## 🚀 快速开始

### 1. 添加别名到 shell

```bash
# ~/.zshrc 或 ~/.bashrc
echo 'alias skill="python3 ~/.hermes/skills/.skill-manager/skill-manager.py"' >> ~/.zshrc
source ~/.zshrc
```

### 2. 基础命令

```bash
# 列出所有 skills
skill list

# 搜索 skills
skill search github

# 查看 skill 详情
skill info mlops

# 创建项目软链接
skill link github          # 在当前项目创建 .skills/github
```

### 3. GitHub 同步配置

编辑 `config.json`:

```json
{
  "sync": {
    "github_repo": "你的用户名/hermes-skills",
    "auto_sync": false
  }
}
```

然后执行:
```bash
skill sync
```

---

## 📁 分类体系

| 分类 | 用途 | 示例 Skills |
|------|------|-------------|
| **01-coding-dev** | 代码开发 | github, devops, software-development |
| **02-ai-agents** | AI Agent | autonomous-ai-agents, dogfood |
| **03-mlops** | MLOps | mlops, training, data-science |
| **04-content** | 内容创作 | creative, media, youtube-content |
| **05-research** | 研究信息 | research, feeds, note-taking |
| **06-productivity** | 效率工具 | productivity, email, notion |
| **07-smart-home** | 智能家居 | smart-home, openhue |
| **08-social** | 社交媒体 | xitter, social-media |
| **09-tools** | 工具实用 | mcp, diagramming |
| **10-gaming** | 游戏 | gaming, minecraft-modpack |
| **11-security** | 安全 | red-teaming, godmode |
| **99-integrations** | 集成 | openclaw-imports, apple |

---

## 🔗 项目集成方案

### 方案 1: 软链接 (推荐)

```bash
# 在项目目录执行
skill link github
skill link devops

# 会自动创建
# .skills/github -> ~/.hermes/skills/github
# .skills/devops -> ~/.hermes/skills/devops
```

### 方案 2: 全局引用

Hermes 会自动加载 `~/.hermes/skills/` 下的所有 skills，无需额外配置。

---

## 📊 与空格方案的对比

| 特性 | 空格方案 | 本方案 |
|------|----------|--------|
| 目标平台 | Cursor/Codex | Hermes Agent |
| 目录结构 | `~/.claude/skills` | `~/.hermes/skills` |
| 管理方式 | 手动+AI辅助 | 专用 CLI 工具 |
| 分类 | 4个大类 | 12个精细分类 |
| 同步 | GitHub | GitHub + 本地备份 |
| 项目集成 | 软链接 | 软链接 + 全局加载 |
| Skill 数量 | 130+ | 27 (可扩展) |
| 自动化 | skill-manage | 更完善的 CLI |

---

## 🛠️ 进阶用法

### 批量创建软链接

```bash
# 在项目目录创建常用 skills 链接
for s in github devops software-development; do
  skill link $s
done
```

### 自动备份脚本

```bash
# 添加到 crontab 每日备份
0 18 * * * python3 ~/.hermes/skills/.skill-manager/skill-manager.py backup
```

### CI/CD 同步

```yaml
# .github/workflows/sync-skills.yml
name: Sync Skills
on:
  schedule:
    - cron: '0 */6 * * *'  # 每6小时
jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: python3 skill-manager.py sync
```

---

## 📝 添加新 Skill

1. 在对应分类目录创建文件夹
2. 添加 `SKILL.md` 文件
3. 更新 `config.json` 分类配置
4. 执行 `skill sync` 同步

---

## 🔮 未来规划

- [ ] Web UI 管理界面
- [ ] Skill  marketplace 集成
- [ ] 自动依赖分析
- [ ] Skill 评分系统
- [ ] 云端共享仓库

---

**设计理念**: 上下文优先于提示词，Skill 的管理本身也是上下文工程。
