# 知识雷达 - 按类型归档指南

## 概述

新版知识雷达支持**按信息类型归档**到不同的 Notion 数据库，让内容组织更有条理。

## 归档规则

| 信息源 | 归档目标 | 环境变量 |
|--------|----------|----------|
| Hacker News, GitHub, HuggingFace | 🤖 Tech/AI 数据库 | `NOTION_DB_TECH_AI` |
| 华尔街见闻, 36氪 | 💰 Finance 数据库 | `NOTION_DB_FINANCE` |
| arXiv | 📚 Academic 数据库 | `NOTION_DB_ACADEMIC` |
| 微博, V2EX, X/Twitter | 💬 Social 数据库 | `NOTION_DB_SOCIAL` |
| RSS, ProductHunt | 📊 Industry 数据库 | `NOTION_DB_INDUSTRY` |

## 快速设置

### 1. 在 Notion 中创建数据库

在你的 "📡 知识雷达" 页面下创建 5 个数据库：

```
📡 知识雷达 (Parent Page)
├── 🤖 Tech/AI 资讯 (Database)
├── 💰 财经市场 (Database)
├── 📚 学术研究 (Database)
├── 💬 社交媒体 (Database)
└── 📊 行业动态 (Database)
```

每个数据库需要这些字段：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 名称 | Title | 文章/项目标题 |
| 来源 | Select | Hacker News, GitHub, 微博 等 |
| 分类 | Multi-select | 科技, AI/ML, 财经, 学术 等 |
| 链接 | URL | 原文链接 |
| 热度 | Number | 评分/点赞数 |
| 摘要 | Rich text | AI 生成的摘要 |
| 状态 | Select | 🆕 新抓取 / ✅ 已阅读 / 📦 已归档 |
| 创建时间 | Date | 抓取时间 |

### 2. 分享数据库给 Integration

对每个数据库：
1. 打开数据库页面
2. 点击右上角的 **...**
3. 选择 **Add connections**
4. 选择你的 Integration (如 "Hermes Knowledge Radar")
5. 点击 **Confirm**

### 3. 获取数据库 ID

1. 打开数据库（确保是 Full page 视图）
2. 复制 URL，例如：
   ```
   https://www.notion.so/33c6a09f46ce8054ac0cd11974e212bd?v=...
   ```
3. 数据库 ID 是 `/` 和 `?v=` 之间的部分：
   ```
   33c6a09f46ce8054ac0cd11974e212bd
   ```

### 4. 配置环境变量

编辑 `~/.knowledge-radar-env`：

```bash
# 添加你的数据库 ID
export NOTION_DB_TECH_AI="your-tech-ai-db-id"
export NOTION_DB_FINANCE="your-finance-db-id"
export NOTION_DB_ACADEMIC="your-academic-db-id"
export NOTION_DB_SOCIAL="your-social-db-id"
export NOTION_DB_INDUSTRY="your-industry-db-id"
```

### 5. 验证配置

```bash
source ~/.knowledge-radar-env
```

应该会显示：
```
Type-based archiving: ✓ Enabled
  ✓ Tech/AI DB configured
  ✓ Finance DB configured
  ...
```

## 回退机制

如果某个 source 没有配置对应的数据库，系统会：
1. 尝试使用 `NOTION_DATABASE_ID`（旧版默认数据库）
2. 如果也没有设置，则跳过该 item 并提示

这保证了向后兼容 - 你可以逐步迁移到多数据库架构。

## 测试同步

手动运行测试：

```bash
cd ~/.hermes/skills/research/knowledge-radar-system/scripts
python3 knowledge_radar_full.py tech-ai
```

输出示例：
```
[2024-01-15 08:00:00] Collecting: tech-ai
📤 Syncing to Notion...
   Token: ✓
  [Tech/AI] Synced 5/5 items
  [Default] Synced 2/2 items

Total: 7 synced, 0 failed [tech-ai]
```

## 故障排除

### "No database configured for item from source 'xxx'"

**原因**: 该 source 没有配置对应的数据库，且没有设置默认数据库

**解决**: 
- 在 `~/.knowledge-radar-env` 中添加对应的数据库 ID
- 或者保留 `NOTION_DATABASE_ID` 作为回退

### "Could not find database with ID"

**原因**: Integration 没有访问该数据库的权限

**解决**: 重新执行 "分享数据库给 Integration" 步骤

### 内容都进了 Default DB

**原因**: 新的数据库环境变量未生效

**解决**:
```bash
# 确保环境变量已加载
source ~/.knowledge-radar-env

# 检查变量是否设置
echo $NOTION_DB_TECH_AI
```

## 迁移策略

如果你已经在使用旧版（单数据库），迁移步骤如下：

1. **备份现有数据**: 在 Notion 中导出当前数据库
2. **创建新数据库**: 按上面的说明创建 5 个分类数据库
3. **复制历史数据**: 将旧数据库中的内容按类型复制到新数据库
4. **更新配置**: 添加新的数据库 ID 到 `~/.knowledge-radar-env`
5. **验证**: 运行一次手动测试确认正常工作
6. **清理**: 可选 - 停用旧数据库或保留作为归档

## 高级配置

### 自定义 Source 映射

编辑 `notion_sync.py` 中的 `SOURCE_TO_DB_MAP`：

```python
SOURCE_TO_DB_MAP = {
    "hackernews": NOTION_DB_TECH_AI,
    "github": NOTION_DB_TECH_AI,
    "your_custom_source": NOTION_DB_TECH_AI,  # 添加自定义映射
}
```

### 每类别多个数据库

如果你希望进一步细分（比如把 GitHub 单独放一个库），可以修改映射：

```python
NOTION_DB_GITHUB = os.getenv("NOTION_DB_GITHUB")

SOURCE_TO_DB_MAP = {
    "github": NOTION_DB_GITHUB,  # GitHub 单独归档
    "hackernews": NOTION_DB_TECH_AI,
    ...
}
```
