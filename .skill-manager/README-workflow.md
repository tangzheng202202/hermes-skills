# Skill Workflow System

技能工作流系统 - 整合 skill-manager + 达尔文进化机制

## 功能概览

这是一个统一的 skill 管理和进化系统，整合了：
1. **skill-manager** 的分类和管理功能
2. **达尔文.skill** 的 8维度评估和梭轮进化机制

## 安装

```bash
# 1. 确保已安装 skill-manager
cd ~/.hermes/skills/.skill-manager

# 2. 添加命令别名
echo 'alias skill-workflow="python3 ~/.hermes/skills/.skill-manager/skill-workflow.py"' >> ~/.bashrc
source ~/.bashrc
```

## 快速开始

```bash
# 列出所有 skill
skill-workflow list

# 评估所有 skill
skill-workflow evaluate

# 进化低分 skill
skill-workflow evolve

# 运行完整工作流（评估 → 优化 → 提交）
skill-workflow workflow
```

## 命令详解

### 1. list - 列出 skill
```bash
skill-workflow list
```
显示所有 skill 及其分类和当前评分。

### 2. evaluate - 评估 skill
```bash
# 评估所有 skill
skill-workflow evaluate

# 评估指定 skill
skill-workflow evaluate -s my-skill
```
评估结果保存在每个 skill 的 `meta.json` 中。

### 3. evolve - 进化 skill
```bash
# 进化所有低分 skill（默认，<80分）
skill-workflow evolve

# 进化指定 skill
skill-workflow evolve -s my-skill

# 进化所有 skill
skill-workflow evolve --all

# 设置迭代次数
skill-workflow evolve -i 5
```

### 4. sync - 同步到 GitHub
```bash
skill-workflow sync
```
将所有变更提交到 GitHub。

### 5. workflow - 完整工作流
```bash
skill-workflow workflow
```
自动执行：评估 → 优化 → 提交的完整流程。

## 8维度评估体系

| 维度 | 权重 | 说明 |
|------|------|------|
| Frontmatter规范 | 8 | 元数据完整性 |
| 工作流清晰度 | 15 | 步骤是否明确 |
| 异常处理 | 10 | 错误处理逻辑 |
| 用户确认点 | 7 | 危险操作确认 |
| 指令具体性 | 15 | 可直接执行性 |
| 路径有效性 | 5 | 文件引用正确性 |
| 架构合理性 | 15 | 模块设计 |
| 实测表现 | 25 | 测试用例通过率 |

## 梭轮机制

进化过程中采用梭轮机制：
1. 每次只改一个 skill
2. 改完评估分数
3. 分数上升 → git commit
4. 分数下降 → git revert

确保只保留有效改进。

## 目录结构

```
.skill-manager/
├── skill-workflow.py       # 主脚本
├── ai-evaluator.py          # AI评估模块
├── darwin-config.yaml       # 达尔文配置
├── darwin/                  # 达尔文工作目录
│   ├── backups/             # 进化备份
│   └── reports/             # 评估报告
└── ...
```

## 配置

编辑 `darwin-config.yaml` 修改评估标准和进化参数。

## 开发计划

- [ ] 集成 AI 深度评估
- [ ] 自动生成测试用例
- [ ] 批量进化支持
- [ ] Web UI 可视化

## 参考

- 花华 达尔文.skill: https://mp.weixin.qq.com/s/4ICQJGwa2MD616_oFmJb4w
- Karpathy autoresearch: https://github.com/karpathy/autoresearch
