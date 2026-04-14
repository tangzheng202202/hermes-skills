# Second Brain - AI 第二大脑系统

基于 Hermes Agent 复刻 Tree Solo 的 MTC+Code 双模态知识管理工作流。

## 核心理念

**摄取 → 消化 → 输出** 全自动闭环

让 AI 成为你的长期知识资产，持续进化。

## 架构

```
┌────────────────┬────────────────┬────────────────┐
│  摄取 (Ingest)   │  消化 (Digest)    │  输出 (Output)    │
├────────────────┼────────────────┼────────────────┤
│ - 文章收集      │ - 自动标签     │ - 知识卡片     │
│ - 视频转录    │ - 概要生成     │ - 文章汇编     │
│ - 翻译        │ - 关联建立     │ - 报告生成     │
│ - 存储归档    │ - 知识图谱     │ - 多格式输出   │
└────────────────┴────────────────┴────────────────┘
```

## 快速开始

```bash
# 1. 配置知识库目录
export SECOND_BRAIN_HOME="~/second-brain"

# 2. 启动摄取流程
second-brain ingest https://mp.weixin.qq.com/s/xxxxx

# 3. 消化内容
second-brain digest --recent 7d

# 4. 输出成果
second-brain output --format pdf --topic "AI工具"
```

## 组件

- **ingest/** - 摄取模块
- **digest/** - 消化模块
- **output/** - 输出模块
- **memory/** - 知识图谱

## 与 Tree Solo 对比

| 功能 | Tree Solo | Hermes Second Brain |
|------|-----------|---------------------|
| MTC模式 | ✅ | ✅ 通过skill呼叫 |
| Code模式 | ✅ | ✅ Hermes原生支持 |
| 摄取 | ✅ | ✅ 公众号/网页/视频 |
| 消化 | ✅ | ✅ 自动标签/概要 |
| 输出 | ✅ | ✅ PDF/卡片/文章 |
| 本地存储 | ✅ | ✅ Markdown+Git |
| 云端协同 | ✅ | ✅ 飞书/Notion |
| 技能市场 | ✅ | ✅ Skill系统 |
