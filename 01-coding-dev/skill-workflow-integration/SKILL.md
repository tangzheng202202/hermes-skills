---
name: skill-workflow-integration
description: Integrate Darwin evaluation system with skill-manager for automated skill quality assessment and evolution
version: 1.0.0
trigger: when integrating skill evaluation systems or automating skill quality improvement
---

# Skill Workflow Integration

Integrates the Darwin.skill evaluation system (8-dimensional assessment + ratchet evolution) with skill-manager for unified skill quality management.

## Overview

This skill provides a complete workflow for:
1. **Scanning** all skills in the repository
2. **Evaluating** them using 8-dimensional scoring (from Darwin.skill)
3. **Evolving** low-scoring skills using ratchet mechanism (improvement-only)
4. **Reporting** comprehensive quality assessments
5. **Syncing** improvements to GitHub

## Architecture

```
skill-workflow.py (main)
├── SkillManager       - From skill-manager: category management, Git sync
├── DarwinEvaluator    - From Darwin: 8-dimensional scoring
├── SkillEvolver       - From Darwin: ratchet evolution mechanism
└── ReportGenerator    - Quality reports and analytics
```

## 8-Dimensional Evaluation

| Dimension | Weight | Max Score | Criteria |
|-----------|--------|-----------|----------|
| Frontmatter规范 | 8 | 8 | name, description, version fields |
| 工作流清晰度 | 15 | 15 | Clear steps, numbered sections |
| 异常处理 | 10 | 10 | Error handling logic |
| 用户确认点 | 7 | 7 | Dangerous operation confirmations |
| 指令具体性 | 15 | 15 | Executable commands with examples |
| 路径有效性 | 5 | 5 | Referenced files exist |
| 架构合理性 | 15 | 15 | Module design quality |
| 实测表现 | 25 | 25 | Test case pass rate |

**Total: 100 points**

## Ratchet Evolution Mechanism

From Darwin.skill / Karpathy's autoresearch:

```
Modify → Evaluate → Commit if improved / Revert if not
```

Key principles:
1. **Single asset**: Modify one SKILL.md at a time
2. **Dual evaluation**: Structure review + Performance test
3. **Ratchet**: Score can only increase (failed attempts are reverted)
4. **Independent scoring**: Different agent evaluates than modifies
5. **Human in loop**: Human approval for final changes

## Usage

### Setup
```bash
# Add alias to shell
alias skill-workflow="python3 ~/.hermes/skills/.skill-manager/skill-workflow.py"
```

### Commands
```bash
# List all skills
skill-workflow list

# Evaluate all skills
skill-workflow evaluate

# Evolve low-scoring skills (<80)
skill-workflow evolve

# Run complete workflow
skill-workflow workflow
```

## Implementation Notes

### Configuration Compatibility Issue

When integrating, discovered that `skill-manager/config.json` uses dict-based categories:
```json
{"categories": {"01-coding-dev": {"name": "...", ...}}}
```

Not list-based. Fixed in `_load_categories()`:
```python
categories = config.get("categories", {})
if isinstance(categories, dict):
    return {cat_id: cat_info.get("name", cat_id) ...}
elif isinstance(categories, list):
    return {cat["id"]: cat.get("name", cat["id"]) ...}
```

### Directory Structure

```
.skill-manager/
├── skill-workflow.py       # Main workflow script
├── ai-evaluator.py         # AI-powered deep evaluation (stub)
├── darwin-config.yaml      # Evaluation thresholds
├── darwin/
│   ├── backups/            # Evolution backups
│   └── reports/            # Assessment reports
└── ...existing files...
```

### Scoring Thresholds

- **Excellent (≥80)**: Well-structured, production-ready
- **Acceptable (60-79)**: Functional but needs improvement
- **Poor (<60)**: Requires significant work

## Common Issues Found

After evaluating 28 skills, typical weaknesses:
1. **异常处理**: 3/10 avg - Missing error handling
2. **用户确认点**: 2/7 avg - No confirmation prompts
3. **指令具体性**: 7/15 avg - Commands lack examples
4. **实测表现**: 15/25 avg - No test cases

Strengths:
- ✅ Frontmatter规范: 8/8 (all perfect)
- ✅ 工作流清晰度: 15/15 (all perfect)
- ✅ 架构合理性: 15/15 (all perfect)

## Integration with AI (TODO)

Current version uses rule-based evaluation. For true AI-powered evolution:

```python
# In ai-evaluator.py
def evaluate_with_ai(skill_content: str) -> dict:
    prompt = f"""
    Evaluate this SKILL.md across 8 dimensions...
    Return structured scores and improvement suggestions.
    """
    return hermes_client.chat(prompt)
```

## References

- Darwin.skill (Huashu): https://mp.weixin.qq.com/s/4ICQJGwa2MD616_oFmJb4w
- Karpathy autoresearch: https://github.com/karpathy/autoresearch
- Original skill-manager: ~/.hermes/skills/.skill-manager/skill-manager.py

## Category

Coding & Development

## Tags

skill-management, quality-assurance, darwin, evolution, workflow-automation

## Author

Hermes Skills Collection
