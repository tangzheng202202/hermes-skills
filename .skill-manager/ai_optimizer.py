#!/usr/bin/env python3
"""
AI 优化器 - 使用 Hermes Agent 自动优化 Skill

这个模块负责：
1. 分析 skill 的弱点
2. 生成优化建议
3. 调用 AI 修改 SKILL.md
4. 验证优化效果
"""

import os
import re
import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Weakness:
    """弱点分析结果"""
    dimension: str  # 维度名称
    score: int      # 当前得分
    max_score: int  # 满分
    issues: List[str]  # 具体问题
    suggestions: List[str]  # 改进建议


class SkillAnalyzer:
    """Skill 分析器"""
    
    def __init__(self):
        self.dimensions = {
            "frontmatter": {"name": "Frontmatter规范", "max": 8},
            "workflow": {"name": "工作流清晰度", "max": 15},
            "exception": {"name": "异常处理", "max": 10},
            "confirmation": {"name": "用户确认点", "max": 7},
            "specificity": {"name": "指令具体性", "max": 15},
            "paths": {"name": "路径有效性", "max": 5},
            "architecture": {"name": "架构合理性", "max": 15},
            "performance": {"name": "实测表现", "max": 25},
        }
    
    def analyze(self, skill_content: str, scores: Dict[str, int]) -> List[Weakness]:
        """分析 skill 弱点，返回需要优化的维度列表"""
        weaknesses = []
        
        for dim, score in scores.items():
            dim_info = self.dimensions.get(dim, {"max": 10})
            max_score = dim_info["max"]
            
            # 只分析低分维度（低于 70% 满分）
            if score < max_score * 0.7:
                issues, suggestions = self._analyze_dimension(dim, skill_content, score)
                weaknesses.append(Weakness(
                    dimension=dim,
                    score=score,
                    max_score=max_score,
                    issues=issues,
                    suggestions=suggestions
                ))
        
        # 按得分从低到高排序（优先优化最差的）
        weaknesses.sort(key=lambda w: w.score / w.max_score)
        
        return weaknesses
    
    def _analyze_dimension(self, dim: str, content: str, score: int) -> Tuple[List[str], List[str]]:
        """分析单个维度的问题"""
        issues = []
        suggestions = []
        
        if dim == "exception":
            if "错误" not in content and "error" not in content.lower():
                issues.append("缺少错误处理说明")
                suggestions.append("添加常见错误处理步骤")
            if "边界" not in content and "boundary" not in content.lower():
                issues.append("缺少边界条件检查")
                suggestions.append("添加输入验证和边界条件处理")
        
        elif dim == "confirmation":
            if "确认" not in content and "confirm" not in content.lower():
                issues.append("缺少用户确认机制")
                suggestions.append("在危险/不可逆操作前添加确认提示")
        
        elif dim == "specificity":
            code_blocks = content.count("```")
            if code_blocks < 2:
                issues.append("缺少具体代码示例")
                suggestions.append("为关键步骤添加可复制的命令示例")
        
        elif dim == "performance":
            if "测试" not in content and "test" not in content.lower():
                issues.append("缺少测试用例")
                suggestions.append("添加测试示例验证 skill 效果")
        
        return issues, suggestions


class AIOptimizer:
    """AI 优化器 - 生成优化后的 SKILL.md"""
    
    def __init__(self, model: str = "anthropic/claude-3.5-sonnet"):
        self.model = model
    
    def generate_optimization_prompt(self, skill_content: str, weakness: Weakness, skill_name: str) -> str:
        """生成优化提示词"""
        
        prompt = f"""你是一个专业的 Skill 优化专家。请优化以下 SKILL.md 文件，重点改进【{weakness.dimension}】这个维度。

## Skill 名称
{skill_name}

## 当前得分
{weakness.score}/{weakness.max_score}

## 发现的问题
"""
        
        for issue in weakness.issues:
            prompt += f"- {issue}\n"
        
        prompt += f"""
## 改进建议
"""
        
        for suggestion in weakness.suggestions:
            prompt += f"- {suggestion}\n"
        
        prompt += f"""
## 当前 SKILL.md 内容

```markdown
{skill_content}
```

## 优化要求

1. 保持原有的结构和功能
2. 重点增强【{weakness.dimension}】这个维度
3. 保持 SKILL.md 标准格式（frontmatter + 正文）
4. 不要改变 skill 的核心功能
5. 只返回优化后的完整内容，不要有其他说明

请输出优化后的完整 SKILL.md 内容：
"""
        
        return prompt
    
    def optimize(self, skill_content: str, weakness: Weakness, skill_name: str) -> str:
        """
        调用 AI 优化 skill
        返回优化后的内容
        """
        prompt = self.generate_optimization_prompt(skill_content, weakness, skill_name)
        
        # 这里需要调用 Hermes Agent 或直接调用 LLM API
        # 由于环境限制，这里返回一个示例实现
        # 完整版本需要集成 Hermes 调用
        
        return self._fallback_optimize(skill_content, weakness)
    
    def _fallback_optimize(self, content: str, weakness: Weakness) -> str:
        """后备优化逻辑 - 基于规则的简单优化"""
        optimized = content
        
        if weakness.dimension == "exception":
            # 添加异常处理模板
            if "## 错误处理" not in content:
                optimized += """

## 错误处理

如果遇到以下情况，请按步骤处理：

1. **命令执行失败**
   - 检查网络连接
   - 确认依赖已正确安装
   - 查看错误日志: `cat /tmp/error.log`

2. **输入参数无效**
   - 验证输入格式
   - 使用默认值重试

3. **权限不足**
   - 检查当前用户权限
   - 尝试使用 sudo 或切换用户
"""
        
        elif weakness.dimension == "confirmation":
            # 在步骤前添加确认提示
            if "确认" not in optimized and "备份" not in optimized:
                # 在第一个 ## 标题前添加提示
                optimized = optimized.replace(
                    "## ",
                    """⚠️ **重要提示**：在执行以下操作前，请确保已备份重要数据，并确认操作无误。

## """)
                # 如果没有 ## 标题，在文末添加
                if "重要提示" not in optimized:
                    optimized += """

---

⚠️ **操作前请确认**：
- [ ] 已备份重要数据
- [ ] 了解操作风险
- [ ] 确认参数配置正确
"""
        
        elif weakness.dimension == "specificity":
            # 添加示例代码块
            if "```" not in optimized:
                optimized += """

## 示例

```bash
# 示例命令
skill-workflow list

# 带参数示例
skill-workflow evaluate -s my-skill
```
"""
        
        return optimized


class OptimizationVerifier:
    """优化验证器"""
    
    def __init__(self):
        self.analyzer = SkillAnalyzer()
    
    def verify(self, original_content: str, optimized_content: str, weakness: Weakness) -> Tuple[bool, int]:
        """
        验证优化效果
        返回: (是否改进, 新分数)
        """
        # 简化版本：检查关键词是否添加
        score_improvement = 0
        
        if weakness.dimension == "exception":
            if "错误" in optimized_content or "error" in optimized_content.lower():
                score_improvement = 3
        
        elif weakness.dimension == "confirmation":
            if "确认" in optimized_content or "备份" in optimized_content:
                score_improvement = 3
        
        elif weakness.dimension == "specificity":
            if optimized_content.count("```") > original_content.count("```"):
                score_improvement = 5
        
        new_score = min(weakness.max_score, weakness.score + score_improvement)
        improved = new_score > weakness.score
        
        return improved, new_score


def optimize_skill(skill_content: str, skill_name: str, scores: Dict[str, int]) -> Tuple[str, bool, str]:
    """
    优化 skill 的主函数
    
    返回: (优化后内容, 是否改进, 日志信息)
    """
    analyzer = SkillAnalyzer()
    optimizer = AIOptimizer()
    verifier = OptimizationVerifier()
    
    # 1. 分析弱点
    weaknesses = analyzer.analyze(skill_content, scores)
    
    if not weaknesses:
        return skill_content, False, "无需优化，所有维度达标"
    
    # 2. 选择最需要优化的维度（得分最低的）
    target_weakness = weaknesses[0]
    
    # 3. AI 优化
    optimized_content = optimizer.optimize(skill_content, target_weakness, skill_name)
    
    # 4. 验证效果
    improved, new_score = verifier.verify(skill_content, optimized_content, target_weakness)
    
    log = f"优化维度: {target_weakness.dimension}, 分数: {target_weakness.score} → {new_score}"
    
    return optimized_content, improved, log


if __name__ == "__main__":
    # 测试
    print("AI 优化器模块已加载")
    print("支持功能:")
    print("  - Skill 弱点分析")
    print("  - AI 自动优化")
    print("  - 效果验证")
