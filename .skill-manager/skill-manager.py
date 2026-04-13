#!/usr/bin/env python3
"""
🚀 Skill Manager for Hermes
一个管理 Hermes Skills 的工具

用法:
    python3 skill-manager.py <command> [args]

命令:
    list              列出所有 skills
    list <category>   列出指定分类的 skills  
    search <keyword>  搜索 skills
    sync              同步到 GitHub
    organize          自动分类整理
    info <skill>      显示 skill 详情
    link <skill>      创建软链接到当前目录
    backup            备份到本地压缩包
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

# 配置
SKILLS_DIR = Path.home() / ".hermes/skills"
CONFIG_FILE = SKILLS_DIR / ".skill-manager/config.json"

def load_config():
    """加载配置"""
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {"categories": {}}

def get_all_skills():
    """获取所有 skill 目录"""
    skills = []
    for item in SKILLS_DIR.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            # 检查是否是有效的 skill
            skill_md = item / "SKILL.md"
            has_skill_md = skill_md.exists()
            
            desc = ""
            if has_skill_md:
                try:
                    content = skill_md.read_text(encoding='utf-8', errors='ignore')
                    for line in content.split('\n'):
                        if line.startswith('description:'):
                            desc = line.split(':', 1)[1].strip()
                            break
                        if line.startswith('description =') or line.startswith('description='):
                            desc = line.split('=', 1)[1].strip().strip('"\'')
                            break
                except:
                    pass
            
            skills.append({
                "name": item.name,
                "path": item,
                "has_skill_md": has_skill_md,
                "description": desc
            })
    return sorted(skills, key=lambda x: x["name"])

def cmd_list(args):
    """列出 skills"""
    config = load_config()
    skills = get_all_skills()
    
    if not args:
        # 列出所有
        print(f"\n📋 Hermes Skills ({len(skills)} 个)\n")
        print(f"{'名称':<30} {'状态':<8} {'描述'}")
        print("-" * 80)
        for skill in skills:
            status = "✅" if skill["has_skill_md"] else "❌"
            desc = skill["description"][:35] + "..." if len(skill["description"]) > 35 else skill["description"]
            print(f"{skill['name']:<30} {status:<8} {desc}")
    else:
        # 按分类列出
        category = args[0]
        cat_config = config.get("categories", {}).get(category)
        if not cat_config:
            print(f"❌ 未找到分类: {category}")
            return
        
        print(f"\n📁 {cat_config['name']}\n")
        print(f"   {cat_config['description']}\n")
        
        for skill_name in cat_config.get("skills", []):
            skill = next((s for s in skills if s["name"] == skill_name), None)
            if skill:
                status = "✅" if skill["has_skill_md"] else "❌"
                print(f"  {status} {skill['name']:<25} {skill['description'][:40]}")

def cmd_search(args):
    """搜索 skills"""
    if not args:
        print("用法: skill-manager search <关键词>")
        return
    
    keyword = args[0].lower()
    skills = get_all_skills()
    
    results = []
    for skill in skills:
        if keyword in skill["name"].lower() or keyword in skill["description"].lower():
            results.append(skill)
    
    print(f"\n🔍 搜索结果: '{keyword}' ({len(results)} 个匹配)\n")
    for skill in results:
        status = "✅" if skill["has_skill_md"] else "❌"
        print(f"  {status} {skill['name']:<25} {skill['description'][:50]}")

def cmd_info(args):
    """显示 skill 详情"""
    if not args:
        print("用法: skill-manager info <skill-name>")
        return
    
    skill_name = args[0]
    skill_path = SKILLS_DIR / skill_name
    
    if not skill_path.exists():
        print(f"❌ Skill 不存在: {skill_name}")
        return
    
    skill_md = skill_path / "SKILL.md"
    print(f"\nℹ️  Skill: {skill_name}\n")
    print(f"   路径: {skill_path}")
    print(f"   状态: {'✅ 已标准化' if skill_md.exists() else '❌ 未标准化'}")
    
    if skill_md.exists():
        content = skill_md.read_text(encoding='utf-8', errors='ignore')
        # 解析 frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        if key in ['name', 'description', 'version', 'category']:
                            print(f"   {key}: {value}")
        
        # 统计文件
        files = list(skill_path.rglob('*'))
        print(f"   文件数: {len(files)}")

def cmd_sync(args):
    """同步到 GitHub"""
    config = load_config()
    repo = config.get("sync", {}).get("github_repo", "")
    
    if not repo:
        print("❌ 未配置 GitHub 仓库")
        print("   请在 config.json 中设置 sync.github_repo")
        return
    
    print(f"\n🔄 准备同步到 GitHub: {repo}\n")
    
    # 检查 git 是否初始化
    git_dir = SKILLS_DIR / ".git"
    if not git_dir.exists():
        print("📝 初始化 Git 仓库...")
        subprocess.run(["git", "init"], cwd=SKILLS_DIR, capture_output=True)
        subprocess.run(["git", "remote", "add", "origin", f"https://github.com/{repo}.git"], 
                      cwd=SKILLS_DIR, capture_output=True)
    
    # 添加所有文件
    print("📝 添加文件到 git...")
    subprocess.run(["git", "add", "."], cwd=SKILLS_DIR, capture_output=True)
    
    # 提交
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result = subprocess.run(
        ["git", "commit", "-m", f"Auto sync: {timestamp}"],
        cwd=SKILLS_DIR, capture_output=True, text=True
    )
    
    if result.returncode == 0:
        print("✅ 提交成功")
        
        # 推送
        print("🚀 推送到 GitHub...")
        push_result = subprocess.run(
            ["git", "push", "-u", "origin", "main"],
            cwd=SKILLS_DIR, capture_output=True, text=True
        )
        
        if push_result.returncode == 0:
            print(f"\n✅ 同步成功!")
            print(f"   仓库: https://github.com/{repo}")
        else:
            print(f"\n❌ 推送失败:")
            print(push_result.stderr)
    else:
        if "nothing to commit" in result.stdout.lower():
            print("✅ 没有变更需要提交")
        else:
            print(f"❌ 提交失败: {result.stderr}")

def cmd_backup(args):
    """备份到本地"""
    backup_dir = Path.home() / ".hermes/skills-backup"
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"skills_backup_{timestamp}.tar.gz"
    
    print(f"\n💾 创建备份...")
    
    # 创建压缩包
    result = subprocess.run(
        ["tar", "-czf", str(backup_file), "-C", str(SKILLS_DIR.parent), "skills"],
        capture_output=True
    )
    
    if result.returncode == 0:
        size = backup_file.stat().st_size / (1024 * 1024)  # MB
        print(f"\n✅ 备份完成!")
        print(f"   文件: {backup_file}")
        print(f"   大小: {size:.2f} MB")
        
        # 列出历史备份
        backups = sorted(backup_dir.glob("skills_backup_*.tar.gz"))
        print(f"\n📂 历史备份 ({len(backups)} 个):")
        for b in backups[-5:]:  # 只显示最近5个
            b_size = b.stat().st_size / (1024 * 1024)
            print(f"   - {b.name} ({b_size:.2f} MB)")
    else:
        print(f"\n❌ 备份失败")

def cmd_link(args):
    """创建软链接到当前目录"""
    if not args:
        print("用法: skill-manager link <skill-name>")
        return
    
    skill_name = args[0]
    skill_path = SKILLS_DIR / skill_name
    
    if not skill_path.exists():
        print(f"❌ Skill 不存在: {skill_name}")
        return
    
    # 在当前目录创建软链接
    current_dir = Path.cwd()
    link_path = current_dir / ".skills"
    link_path.mkdir(exist_ok=True)
    
    target_link = link_path / skill_name
    
    if target_link.exists():
        print(f"⚠️  软链接已存在: {target_link}")
        return
    
    try:
        target_link.symlink_to(skill_path, target_is_directory=True)
        print(f"\n✅ 软链接创建成功!")
        print(f"   源: {skill_path}")
        print(f"   链接: {target_link}")
        print(f"\n   在当前项目可以通过 .skills/{skill_name} 访问")
    except Exception as e:
        print(f"\n❌ 创建失败: {e}")

def cmd_organize(args):
    """自动分类整理"""
    config = load_config()
    skills = get_all_skills()
    categories = config.get("categories", {})
    
    print("\n🖼️  自动分类整理\n")
    
    # 计算每个 skill 应该在哪个分类
    skill_to_category = {}
    for cat_name, cat_config in categories.items():
        for skill_name in cat_config.get("skills", []):
            skill_to_category[skill_name] = cat_name
    
    # 检查现有 skills
    uncategorized = []
    for skill in skills:
        if skill["name"] not in skill_to_category:
            uncategorized.append(skill["name"])
    
    print(f"   已分类: {len(skills) - len(uncategorized)} 个")
    print(f"   未分类: {len(uncategorized)} 个\n")
    
    if uncategorized:
        print("📝 未分类的 skills:")
        for name in uncategorized:
            print(f"   - {name}")
        print("\n   提示: 编辑 config.json 添加这些 skills 到适当的分类")
    
    # 显示分类统计
    print("\n📊 分类统计:")
    for cat_name, cat_config in categories.items():
        count = len([s for s in cat_config.get("skills", []) 
                    if (SKILLS_DIR / s).exists()])
        total = len(cat_config.get("skills", []))
        print(f"   {cat_config['name']:<25} {count}/{total} 个")

def show_help(args=None):
    """显示帮助"""
    print(__doc__)
    print("\n📋 快速入门:")
    print("   skill-manager list                    # 列出所有 skills")
    print("   skill-manager search <关键词>          # 搜索 skills")
    print("   skill-manager info <skill-name>       # 查看详情")
    print("   skill-manager sync                    # 同步到 GitHub")
    print("   skill-manager backup                  # 本地备份")

def main():
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    commands = {
        "list": cmd_list,
        "search": cmd_search,
        "info": cmd_info,
        "sync": cmd_sync,
        "backup": cmd_backup,
        "link": cmd_link,
        "organize": cmd_organize,
        "help": show_help,
        "-h": show_help,
        "--help": show_help,
    }
    
    if command in commands:
        commands[command](args)
    else:
        print(f"❌ 未知命令: {command}")
        print("使用 'skill-manager help' 查看帮助")

if __name__ == "__main__":
    main()
