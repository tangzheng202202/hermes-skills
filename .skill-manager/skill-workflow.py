#!/usr/bin/env python3
"""
Skill Workflow System - 技能工作流系统
整合 skill-manager 和 达尔文进化机制

功能:
1. 列出所有skill
2. 自动评估质量（8维度）
3. 优化低分skill
4. 提交到GitHub
5. 生成进化报告

使用: python3 skill-workflow.py [command]
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional

# 配置
SKILLS_DIR = Path.home() / ".hermes" / "skills"
MANAGER_DIR = SKILLS_DIR / ".skill-manager"
CONFIG_FILE = MANAGER_DIR / "config.json"
DARWIN_DIR = MANAGER_DIR / "darwin"
REPORTS_DIR = DARWIN_DIR / "reports"
BACKUP_DIR = DARWIN_DIR / "backups"

# 8维度评分标准（来自达尔文.skill）
EVALUATION_DIMENSIONS = {
    "frontmatter": {"name": "Frontmatter规范", "weight": 8, "max": 8},
    "workflow": {"name": "工作流清晰度", "weight": 15, "max": 15},
    "exception": {"name": "异常处理", "weight": 10, "max": 10},
    "confirmation": {"name": "用户确认点", "weight": 7, "max": 7},
    "specificity": {"name": "指令具体性", "weight": 15, "max": 15},
    "paths": {"name": "路径有效性", "weight": 5, "max": 5},
    "architecture": {"name": "架构合理性", "weight": 15, "max": 15},
    "performance": {"name": "实测表现", "weight": 25, "max": 25},
}


class Skill:
    """技能对象"""
    def __init__(self, path: Path, category: str):
        self.path = path
        self.category = category
        self.name = path.stem
        self.skill_file = path / "SKILL.md"
        self.meta_file = path / "meta.json"
        self.score = 0
        self.scores = {}
        self.last_evaluated = None
        
    def exists(self) -> bool:
        return self.skill_file.exists()
    
    def read_content(self) -> str:
        if self.exists():
            return self.skill_file.read_text(encoding="utf-8")
        return ""
    
    def get_meta(self) -> dict:
        if self.meta_file.exists():
            return json.loads(self.meta_file.read_text(encoding="utf-8"))
        return {}
    
    def save_meta(self, meta: dict):
        self.meta_file.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")


class SkillManager:
    """技能管理器"""
    def __init__(self):
        self.skills_dir = SKILLS_DIR
        self.categories = self._load_categories()
        self.skills: List[Skill] = []
        
    def _load_categories(self) -> Dict[str, str]:
        """加载分类配置"""
        if CONFIG_FILE.exists():
            config = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            categories = config.get("categories", {})
            if isinstance(categories, dict):
                return {cat_id: cat_info.get("name", cat_id) for cat_id, cat_info in categories.items()}
            elif isinstance(categories, list):
                return {cat["id"]: cat.get("name", cat["id"]) for cat in categories}
        return {}
    
    def scan_skills(self) -> List[Skill]:
        """扫描所有skill"""
        self.skills = []
        
        for category_dir in self.skills_dir.iterdir():
            if not category_dir.is_dir():
                continue
            if category_dir.name.startswith("."):
                continue
                
            category_id = category_dir.name
            category_name = self.categories.get(category_id, category_id)
            
            for skill_dir in category_dir.iterdir():
                if not skill_dir.is_dir():
                    continue
                if skill_dir.name.startswith("."):
                    continue
                    
                skill = Skill(skill_dir, category_name)
                if skill.exists():
                    self.skills.append(skill)
        
        return self.skills
    
    def get_skill_by_name(self, name: str) -> Optional[Skill]:
        """通过名称获取skill"""
        for skill in self.skills:
            if skill.name == name:
                return skill
        return None


class DarwinEvaluator:
    """达尔文评估器 - 8维度评分"""
    
    def __init__(self):
        self.dimensions = EVALUATION_DIMENSIONS
    
    def evaluate(self, skill: Skill) -> Tuple[int, Dict[str, int]]:
        """
        评估skill，返回总分和各维度分数
        """
        content = skill.read_content()
        return self.evaluate_skill_content(content)
    
    def evaluate_skill_content(self, content: str) -> Tuple[int, Dict[str, int]]:
        """
        评估skill内容
        """
        scores = {}
        
        # Frontmatter规范 (8分)
        has_frontmatter = content.startswith("---") and "---" in content[3:]
        has_name = "name:" in content or "名称:" in content
        has_description = "description:" in content or "描述:" in content
        scores["frontmatter"] = 8 if has_frontmatter and has_name and has_description else 4
        
        # 工作流清晰度 (15分)
        steps = content.count("## ") + content.count("### ")
        scores["workflow"] = min(15, steps * 3)
        
        # 异常处理 (10分)
        has_error_handling = "错误" in content or "异常" in content or "error" in content.lower()
        scores["exception"] = 10 if has_error_handling else 3
        
        # 用户确认点 (7分)
        has_confirmation = "确认" in content or "确定" in content or "confirm" in content.lower()
        scores["confirmation"] = 7 if has_confirmation else 2
        
        # 指令具体性 (15分)
        has_commands = "```" in content or "命令" in content
        scores["specificity"] = 15 if has_commands else 7
        
        # 路径有效性 (5分)
        scores["paths"] = 5
        
        # 架构合理性 (15分)
        has_structure = content.count("#") >= 3
        scores["architecture"] = 15 if has_structure else 8
        
        # 实测表现 (25分)
        scores["performance"] = 15
        
        # 计算加权总分
        total = sum(scores[dim] * self.dimensions[dim]["weight"] // self.dimensions[dim]["max"] 
                   for dim in scores)
        
        return total, scores
    
    def evaluate_with_ai(self, skill: Skill) -> Tuple[int, Dict[str, int], str]:
        """
        使用AI进行深度评估
        返回: (总分, 各维度分数, 改进建议)
        """
        # 这个功能需要调用Hermes Agent
        # 实现略微复杂，需要单独实现
        pass


class SkillEvolver:
    """技能进化器 - 梭轮机制"""
    
    def __init__(self, manager: SkillManager, evaluator: DarwinEvaluator):
        self.manager = manager
        self.evaluator = evaluator
        self.backup_dir = BACKUP_DIR
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def backup(self, skill: Skill) -> Path:
        """备份skill"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{skill.name}_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        # 复制skill目录
        import shutil
        shutil.copytree(skill.path, backup_path)
        
        return backup_path
    
    def evolve(self, skill: Skill, iterations: int = 3) -> Tuple[bool, int, int]:
        """
        进化skill
        
        返回: (是否改进, 原始分数, 最终分数)
        """
        import sys
        sys.path.insert(0, str(MANAGER_DIR))
        from ai_optimizer import optimize_skill
        
        print(f"\n🧬 开始进化: {skill.name}")
        
        # 初始评估
        baseline_score, scores = self.evaluator.evaluate(skill)
        print(f"   基线分数: {baseline_score}")
        
        best_score = baseline_score
        improved = False
        original_content = skill.read_content()
        current_content = original_content
        
        for i in range(iterations):
            print(f"\n   迭代 {i+1}/{iterations}")
            
            # 使用AI优化
            try:
                optimized_content, iteration_improved, log = optimize_skill(
                    current_content, 
                    skill.name, 
                    scores
                )
                print(f"   {log}")
                
                if iteration_improved:
                    # 验证改进
                    new_score, new_scores = self.evaluator.evaluate_skill_content(optimized_content)
                    
                    if new_score > best_score:
                        print(f"   ✅ 改进有效: {best_score} → {new_score}")
                        best_score = new_score
                        scores = new_scores
                        current_content = optimized_content
                        improved = True
                        
                        # 保存改进
                        skill.skill_file.write_text(optimized_content, encoding="utf-8")
                    else:
                        print(f"   ⚠️ 改进未提升分数，回滚")
                else:
                    print(f"   ℹ️ 未发现改进空间")
                    
            except Exception as e:
                print(f"   ❌ 优化失败: {e}")
                continue
        
        # 最终评估
        if improved:
            final_score = best_score
            print(f"\n   🎯 最终: {baseline_score} → {final_score} (+提升{final_score - baseline_score})")
        else:
            final_score = baseline_score
            print(f"\n   ℹ️ 保持: {baseline_score}分")
        
        return improved, baseline_score, final_score


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self):
        self.reports_dir = REPORTS_DIR
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_evaluation_report(self, skills: List[Skill]) -> Path:
        """生成评估报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.reports_dir / f"evaluation_{timestamp}.md"
        
        content = f"""# Skill质量评估报告

生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
评估数量: {len(skills)}

## 概览

| Skill名称 | 分类 | 总分 | 状态 |
|----------|------|------|------|
"""
        
        for skill in skills:
            status = "✅ 优秀" if skill.score >= 80 else "⚠️ 可改进" if skill.score >= 60 else "❌ 需优化"
            content += f"| {skill.name} | {skill.category} | {skill.score} | {status} |\n"
        
        content += f"""
## 详细评分

"""
        
        for skill in skills:
            content += f"""### {skill.name}

- **分类**: {skill.category}
- **总分**: {skill.score}/100
- **各维度分数**:

"""
            for dim, score in skill.scores.items():
                dim_info = EVALUATION_DIMENSIONS[dim]
                content += f"  - {dim_info['name']}: {score}/{dim_info['max']} (权重{dim_info['weight']})\n"
            
            content += "\n---\n\n"
        
        report_file.write_text(content, encoding="utf-8")
        print(f"\n📊 报告已生成: {report_file}")
        
        return report_file


def cmd_list(args):
    "列出所有skill"
    manager = SkillManager()
    skills = manager.scan_skills()
    
    print(f"\n📁 共发现 {len(skills)} 个 skill:\n")
    print(f"{'名称':<30} {'分类':<20} {'评分':<10}")
    print("-" * 60)
    
    for skill in skills:
        score_str = f"{skill.score}分" if skill.score > 0 else "未评估"
        print(f"{skill.name:<30} {skill.category:<20} {score_str:<10}")


def cmd_evaluate(args):
    "评估skill"
    manager = SkillManager()
    evaluator = DarwinEvaluator()
    reporter = ReportGenerator()
    
    manager.scan_skills()
    
    if args.skill:
        # 评估指定skill
        skill = manager.get_skill_by_name(args.skill)
        if not skill:
            print(f"❌ 找不到 skill: {args.skill}")
            return
        skills = [skill]
    else:
        # 评估所有skill
        skills = manager.skills
    
    print(f"\n🔍 开始评估 {len(skills)} 个 skill...")
    
    for skill in skills:
        score, scores = evaluator.evaluate(skill)
        skill.score = score
        skill.scores = scores
        skill.last_evaluated = datetime.now().isoformat()
        
        # 保存到meta
        meta = skill.get_meta()
        meta["evaluation"] = {
            "score": score,
            "scores": scores,
            "evaluated_at": skill.last_evaluated
        }
        skill.save_meta(meta)
        
        status = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
        print(f"   {status} {skill.name}: {score}分")
    
    # 生成报告
    reporter.generate_evaluation_report(skills)


def cmd_evolve(args):
    "进化skill"
    manager = SkillManager()
    evaluator = DarwinEvaluator()
    evolver = SkillEvolver(manager, evaluator)
    
    manager.scan_skills()
    
    if args.skill:
        skill = manager.get_skill_by_name(args.skill)
        if not skill:
            print(f"❌ 找不到 skill: {args.skill}")
            return
        skills = [skill]
    else:
        # 只进化低分skill
        if args.all:
            skills = manager.skills
        else:
            skills = [s for s in manager.skills if s.score < 80]
            if not skills:
                print("✅ 所有skill分数都在80以上，无需进化")
                return
    
    print(f"\n🐸 开始进化 {len(skills)} 个 skill...")
    
    for skill in skills:
        improved, old_score, new_score = evolver.evolve(skill, iterations=args.iterations)
        if improved:
            print(f"   ✅ {skill.name}: {old_score} → {new_score}")
        else:
            print(f"   ℹ️ {skill.name}: 保持 {old_score}分")


def cmd_sync(args):
    "同步到GitHub"
    print("\ud83d? 开始同步到 GitHub...")
    
    # 检查git状态
    result = subprocess.run(
        ["git", "-C", str(SKILLS_DIR), "status", "--porcelain"],
        capture_output=True,
        text=True
    )
    
    if not result.stdout.strip():
        print("   ℹ️ 没有变更需要提交")
        return
    
    # 提交变更
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subprocess.run(["git", "-C", str(SKILLS_DIR), "add", "."], check=True)
    subprocess.run(
        ["git", "-C", str(SKILLS_DIR), "commit", "-m", f"Skill workflow update - {timestamp}"],
        check=True
    )
    subprocess.run(["git", "-C", str(SKILLS_DIR), "push"], check=True)
    
    print("   ✅ 同步完成")


def cmd_workflow(args):
    "完整工流: 评估 → 优化 → 提交"
    print("\n🚀 启动完整 Skill 工作流")
    print("=" * 50)
    
    # 1. 评估
    print("\n【阶段 1/3】评估所有skill")
    cmd_evaluate(args)
    
    # 2. 优化
    print("\n【阶段 2/3】优化低分skill")
    cmd_evolve(args)
    
    # 3. 提交
    print("\n【阶段 3/3】同步到GitHub")
    cmd_sync(args)
    
    print("\n" + "=" * 50)
    print("🎉 工作流完成！")


def main():
    parser = argparse.ArgumentParser(
        description="Skill Workflow System - 技能工作流系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 skill-workflow.py list                    # 列出所有skill
  python3 skill-workflow.py evaluate                # 评估所有skill
  python3 skill-workflow.py evaluate -s my-skill    # 评估指定skill
  python3 skill-workflow.py evolve                  # 进化低分skill
  python3 skill-workflow.py workflow                # 运行完整工流
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # list 命令
    list_parser = subparsers.add_parser("list", help="列出所有skill")
    list_parser.set_defaults(func=cmd_list)
    
    # evaluate 命令
    eval_parser = subparsers.add_parser("evaluate", help="评估skill")
    eval_parser.add_argument("-s", "--skill", help="评估指定skill")
    eval_parser.set_defaults(func=cmd_evaluate)
    
    # evolve 命令
    evolve_parser = subparsers.add_parser("evolve", help="进化skill")
    evolve_parser.add_argument("-s", "--skill", help="进化指定skill")
    evolve_parser.add_argument("-a", "--all", action="store_true", help="进化所有skill（默认只进化低分skill）")
    evolve_parser.add_argument("-i", "--iterations", type=int, default=3, help="进化迭代次数")
    evolve_parser.set_defaults(func=cmd_evolve)
    
    # sync 命令
    sync_parser = subparsers.add_parser("sync", help="同步到GitHub")
    sync_parser.set_defaults(func=cmd_sync)
    
    # workflow 命令
    workflow_parser = subparsers.add_parser("workflow", help="运行完整工流")
    workflow_parser.add_argument("-s", "--skill", help="处理指定skill")
    workflow_parser.add_argument("-a", "--all", action="store_true", help="处理所有skill")
    workflow_parser.add_argument("-i", "--iterations", type=int, default=3, help="进化迭代次数")
    workflow_parser.set_defaults(func=cmd_workflow)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
