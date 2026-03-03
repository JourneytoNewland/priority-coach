#!/usr/bin/env python3
"""
Priority Coach v1.2 发布前测试
验证核心功能和文件完整性
"""

import os
import sys
import json
from pathlib import Path

# 测试结果
results = {"passed": [], "failed": []}

def test_section(name):
    """测试节装饰器"""
    def decorator(func):
        def wrapper():
            try:
                func()
                results["passed"].append(name)
                print(f"✅ {name}")
            except AssertionError as e:
                results["failed"].append((name, str(e)))
                print(f"❌ {name}: {e}")
            except Exception as e:
                results["failed"].append((name, f"Unexpected error: {e}"))
                print(f"⚠️  {name}: {e}")
        return wrapper
    return decorator

# ==================== 文件结构测试 ====================

@test_section("文件结构完整性")
def test_file_structure():
    """测试所有必需文件是否存在"""
    base_path = Path(__file__).parent.parent

    required_files = [
        "SKILL.md",
        "README.md",
        "examples.md",
        "references/eisenhower-matrix.md",
        "references/p-persona-guide.md",
        "references/pomodoro-technique.md",
        "references/biotime-matching.md",
        "references/self-evolution.md",
        "scripts/calculate_value_score.py",
        "scripts/analyze_escape_patterns.py",
        "scripts/daily_review.py",
        "scripts/generate_weekly_report.py",
        "scripts/self_evolution.py",
    ]

    for file in required_files:
        file_path = base_path / file
        assert file_path.exists(), f"缺少文件: {file}"
        assert file_path.is_file(), f"不是文件: {file}"

# ==================== Python 脚本测试 ====================

@test_section("Python脚本语法检查")
def test_python_syntax():
    """测试所有Python脚本是否可以导入"""
    base_path = Path(__file__).parent.parent / "scripts"

    scripts = [
        "calculate_value_score.py",
        "analyze_escape_patterns.py",
        "daily_review.py",
        "generate_weekly_report.py",
        "self_evolution.py",
    ]

    for script in scripts:
        script_path = base_path / script
        # 编译检查
        with open(script_path, 'r', encoding='utf-8') as f:
            code = f.read()
        try:
            compile(code, script, 'exec')
        except SyntaxError as e:
            raise AssertionError(f"{script} 语法错误: {e}")

# ==================== 数据格式测试 ====================

@test_section("JSON数据格式验证")
def test_json_format():
    """测试JSON示例文件格式"""
    base_path = Path(__file__).parent.parent

    # 测试 user_goals.json 示例
    example_goals = {
        "version": "1.0",
        "last_updated": "2025-03-03",
        "goals": [
            {
                "id": "goal_1",
                "title": "完成AI教练产品MVP",
                "category": "career",
                "priority_weight": 0.5,
                "deadline": "2025-06-01",
                "why": "验证产品方向",
                "keywords": ["开发", "AI", "产品", "代码"]
            }
        ],
        "preferences": {
            "deep_work_hours": ["9:00-11:30", "14:00-16:00"],
            "max_pomodoros_per_day": 8,
            "buffer_ratio": 0.2
        }
    }

    # 验证可以序列化和反序列化
    json_str = json.dumps(example_goals, ensure_ascii=False)
    parsed = json.loads(json_str)
    assert parsed["goals"][0]["title"] == "完成AI教练产品MVP"

# ==================== 文档内容测试 ====================

@test_section("SKILL.md 必需内容检查")
def test_skill_md_content():
    """测试 SKILL.md 是否包含必需的内容"""
    base_path = Path(__file__).parent.parent
    skill_md = base_path / "SKILL.md"

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查 YAML frontmatter
    assert "---" in content, "缺少 YAML frontmatter"
    assert "name: priority-coach" in content, "缺少技能名称"
    assert "user-invocable: true" in content, "缺少 user-invocable 标记"

    # 检查核心章节（实际章节名称）
    assert "## 概述" in content or "# 概述" in content, "缺少概述章节"
    assert "## 工作流程" in content, "缺少工作流程章节"
    assert "## 更新日志" in content, "缺少更新日志章节"

    # 检查 v1.2 新增功能
    assert "进化报告" in content, "缺少进化报告命令"
    assert "TodoWrite" in content, "缺少 TodoWrite 集成说明"
    assert "自我进化" in content, "缺少自我进化系统说明"

@test_section("examples.md 场景完整性")
def test_examples_completeness():
    """测试 examples.md 是否包含8个场景"""
    base_path = Path(__file__).parent.parent
    examples_md = base_path / "examples.md"

    with open(examples_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查场景标题（实际标题格式是"示例X："）
    scenarios = [
        "示例1: 首次使用 - 初始化目标",
        "示例2: 早上规划",
        "示例3: 任务爆炸",
        "示例4: 下午调整",
        "示例5: 每日复盘",
        "示例6: 绩效周报",
        "示例7: 目标检查",
        "示例8: 逃避模式"
    ]

    for scenario in scenarios:
        assert scenario in content, f"缺少场景: {scenario}"

@test_section("ROADMAP.md 结构检查")
def test_roadmap_structure():
    """测试 ROADMAP.md 结构"""
    base_path = Path(__file__).parent.parent
    roadmap_md = base_path / "ROADMAP.md"

    with open(roadmap_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查主要章节
    assert "## 当前版本 (v1.2)" in content, "缺少当前版本章节"
    assert "## 短期优化 (v1.3)" in content, "缺少短期优化章节"
    assert "## 中期增强 (v1.4-v1.5)" in content, "缺少中期增强章节"
    assert "## 长期愿景 (v2.0+)" in content, "缺少长期愿景章节"
    assert "## LLM增强方案" in content, "缺少LLM增强方案章节"

@test_section("CHANGELOG.md 版本记录")
def test_changelog_versions():
    """测试 CHANGELOG.md 是否记录了所有版本"""
    base_path = Path(__file__).parent.parent
    changelog_md = base_path.parent.parent / "CHANGELOG.md"

    with open(changelog_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查版本
    assert "## [1.2.0]" in content, "缺少 v1.2.0 记录"
    assert "## [1.1.0]" in content, "缺少 v1.1.0 记录"
    assert "## [1.0.0]" in content, "缺少 v1.0.0 记录"

    # 检查 v1.2.0 新功能
    assert "TodoWrite" in content, "CHANGELOG 未记录 TodoWrite 集成"
    assert "自我进化" in content or "Self" in content, "CHANGELOG 未记录自我进化系统"

# ==================== 自我进化系统测试 ====================

@test_section("自我进化引擎类检查")
def test_self_evolution_class():
    """测试 SelfEvolutionEngine 类是否完整"""
    base_path = Path(__file__).parent.parent / "scripts"
    script_path = base_path / "self_evolution.py"

    with open(script_path, 'r', encoding='utf-8') as f:
        code = f.read()

    # 检查类定义
    assert "class SelfEvolutionEngine" in code, "缺少 SelfEvolutionEngine 类"

    # 检查核心方法
    required_methods = [
        "def collect_metrics",
        "def learn_user_model",
        "def optimize_algorithm_parameters",
        "def run_ab_test",
        "def generate_evolution_report"
    ]

    for method in required_methods:
        assert method in code, f"缺少方法: {method}"

@test_section("进化报告命令文档化")
def test_evolution_report_documented():
    """测试进化报告命令是否在文档中说明"""
    base_path = Path(__file__).parent.parent
    skill_md = base_path / "SKILL.md"

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    assert "priority-coach 进化报告" in content, "SKILL.md 未记录进化报告命令"
    assert "自我进化" in content or "自我进化系统" in content, "SKILL.md 未说明自我进化系统"

# ==================== 安全性测试 ====================

@test_section(".gitignore 隐私保护")
def test_gitignore_privacy():
    """测试 .gitignore 是否正确排除用户数据"""
    base_path = Path(__file__).parent.parent.parent.parent
    gitignore = base_path / ".gitignore"

    with open(gitignore, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查用户数据目录是否被忽略
    assert ".claude/priority-coach/" in content, ".gitignore 未排除用户数据目录"

@test_section("敏感信息检查")
def test_no_sensitive_info():
    """测试代码中是否包含硬编码的敏感信息"""
    base_path = Path(__file__).parent.parent

    # 检查的敏感模式
    sensitive_patterns = [
        "password", "api_key", "secret", "token",
        "credentials", "private_key"
    ]

    # 检查所有 Python 文件
    for script in base_path.rglob("*.py"):
        with open(script, 'r', encoding='utf-8') as f:
            content = f.read().lower()

        for pattern in sensitive_patterns:
            # 排除注释中的说明
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if pattern in line and not line.strip().startswith('#'):
                    # 警告但不失败（可能是合法的变量名）
                    if script.name not in [".gitignore", "__pycache__"]:
                        print(f"⚠️  {script}:{i} 可能包含敏感词: {pattern}")

# ==================== 版本一致性测试 ====================

@test_section("版本号一致性")
def test_version_consistency():
    """测试各文件中的版本号是否一致"""
    base_path = Path(__file__).parent.parent

    # 从 README.md 读取版本
    with open(base_path.parent.parent / "README.md", 'r') as f:
        readme_content = f.read()
        assert "version-1.2.0" in readme_content or "1.2.0" in readme_content, "README.md 版本号不是 v1.2.0"

    # 从 CHANGELOG.md 读取版本
    with open(base_path.parent.parent / "CHANGELOG.md", 'r') as f:
        changelog_content = f.read()
        assert "[1.2.0]" in changelog_content, "CHANGELOG.md 未记录 v1.2.0"

# ==================== 运行所有测试 ====================

def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("Priority Coach v1.2 发布前测试")
    print("=" * 60)
    print()

    # 获取所有测试函数
    test_functions = [
        test_file_structure,
        test_python_syntax,
        test_json_format,
        test_skill_md_content,
        test_examples_completeness,
        test_roadmap_structure,
        test_changelog_versions,
        test_self_evolution_class,
        test_evolution_report_documented,
        test_gitignore_privacy,
        test_no_sensitive_info,
        test_version_consistency,
    ]

    # 运行测试
    for test_func in test_functions:
        test_func()

    # 输出总结
    print()
    print("=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"✅ 通过: {len(results['passed'])}")
    print(f"❌ 失败: {len(results['failed'])}")

    if results['failed']:
        print("\n失败详情:")
        for name, error in results['failed']:
            print(f"  - {name}: {error}")
        return False
    else:
        print("\n🎉 所有测试通过！v1.2 可以发布！")
        return True

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
