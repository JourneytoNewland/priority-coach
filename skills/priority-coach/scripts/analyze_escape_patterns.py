#!/usr/bin/env python3
"""
逃避模式分析器 (Escape Patterns Analyzer)

分析用户的逃避模式，识别反复推迟的任务，并提供针对性建议。

分析维度：
- 任务类型（写作、规划、沟通等）
- 任务特征（复杂度、创造性、模板可用性）
- 推迟原因（不知道从哪开始、怕做不好、没兴趣等）
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict


class EscapePatternAnalyzer:
    """逃避模式分析器"""

    def __init__(self, data_dir: Optional[str] = None):
        """
        初始化分析器

        Args:
            data_dir: 用户数据目录，默认为 ~/.claude/priority-coach/
        """
        if data_dir is None:
            data_dir = Path.home() / ".claude" / "priority-coach"
        else:
            data_dir = Path(data_dir)

        self.data_dir = Path(data_dir)
        self.plans_dir = self.data_dir / "daily_plans"
        self.patterns_file = self.data_dir / "analytics" / "escape_patterns.json"

        # 确保目录存在
        self.plans_dir.mkdir(parents=True, exist_ok=True)
        self.patterns_file.parent.mkdir(parents=True, exist_ok=True)

    def load_history(self, days: int = 30) -> List[Dict]:
        """
        加载历史每日计划

        Args:
            days: 加载最近多少天的数据

        Returns:
            每日计划列表
        """
        plans = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # 遍历日期目录
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y/%m/%d")
            plan_file = self.plans_dir / f"{date_str}.json"

            if plan_file.exists():
                try:
                    with open(plan_file, 'r', encoding='utf-8') as f:
                        plan_data = json.load(f)
                        plans.append(plan_data)
                except Exception as e:
                    print(f"⚠️  警告: 无法读取 {plan_file} ({e})")

            current_date += timedelta(days=1)

        return plans

    def identify_delayed_tasks(self, plans: List[Dict]) -> List[Dict]:
        """
        识别反复推迟的任务

        Args:
            plans: 历史计划列表

        Returns:
            推迟任务列表，包含推迟次数和任务信息
        """
        # 统计每个任务的推迟次数
        task_delay_count = defaultdict(lambda: {"count": 0, "tasks": []})

        for plan in plans:
            date = plan.get("date", "")
            tasks = plan.get("tasks", [])

            for task in tasks:
                # 检查任务状态
                status = task.get("status", "")
                description = task.get("description", "")

                # 如果任务被推迟或未完成
                if status in ["delayed", "postponed", "not_started"]:
                    # 使用任务描述的简化版本作为key
                    task_key = self._normalize_task(description)
                    task_delay_count[task_key]["count"] += 1
                    task_delay_count[task_key]["tasks"].append({
                        "date": date,
                        "description": description,
                        "value_score": task.get("value_score", 0),
                        "category": task.get("category", "")
                    })

        # 筛选出推迟次数>=3的任务
        delayed_tasks = []
        for task_key, data in task_delay_count.items():
            if data["count"] >= 3:
                delayed_tasks.append({
                    "task_key": task_key,
                    "delay_count": data["count"],
                    "examples": data["tasks"][:5]  # 最多保留5个示例
                })

        # 按推迟次数降序排序
        delayed_tasks.sort(key=lambda x: x["delay_count"], reverse=True)

        return delayed_tasks

    def _normalize_task(self, description: str) -> str:
        """
        标准化任务描述（用于聚类）

        Args:
            description: 原始任务描述

        Returns:
            标准化后的任务key
        """
        # 转小写
        desc = description.lower().strip()

        # 移除常见前缀
        prefixes = ["完成", "做", "写", "准备", "创建"]
        for prefix in prefixes:
            if desc.startswith(prefix):
                desc = desc[len(prefix):].strip()

        # 提取核心关键词（前10个字符）
        core = desc[:10] if len(desc) > 10 else desc

        return core

    def extract_features(self, task: str) -> Dict[str, any]:
        """
        提取任务特征

        Args:
            task: 任务描述

        Returns:
            特征字典
        """
        task_lower = task.lower()

        features = {
            "complexity": "unknown",
            "creativity": "unknown",
            "template_availability": "unknown",
            "type": "unknown"
        }

        # 判断任务类型
        if any(kw in task_lower for kw in ["写", "创作", "设计", "文章"]):
            features["type"] = "writing"
        elif any(kw in task_lower for kw in ["规划", "计划", "方案", "策略"]):
            features["type"] = "planning"
        elif any(kw in task_lower for kw in ["学", "研究", "读"]):
            features["type"] = "learning"
        elif any(kw in task_lower for kw in ["会", "沟通", "讨论"]):
            features["type"] = "communication"
        elif any(kw in task_lower for kw in ["代码", "开发", "编程"]):
            features["type"] = "coding"

        # 判断复杂度
        complex_keywords = ["复杂", "系统", "架构", "全面", "完整"]
        if any(kw in task_lower for kw in complex_keywords):
            features["complexity"] = "high"
        elif any(kw in task_lower for kw in ["简单", "快速", "小"]):
            features["complexity"] = "low"
        else:
            features["complexity"] = "medium"

        # 判断创造性
        creative_keywords = ["创意", "创新", "设计", "原创", "构思"]
        if any(kw in task_lower for kw in creative_keywords):
            features["creativity"] = "high"
        elif any(kw in task_lower for kw in ["整理", "复制", "修改"]):
            features["creativity"] = "low"
        else:
            features["creativity"] = "medium"

        # 判断模板可用性
        if features["type"] in ["writing", "planning"]:
            features["template_availability"] = "maybe"
        elif features["type"] in ["communication", "coding"]:
            features["template_availability"] = "yes"
        else:
            features["template_availability"] = "unknown"

        return features

    def cluster_by_features(self, delayed_tasks: List[Dict]) -> List[Dict]:
        """
        按特征聚类推迟任务

        Args:
            delayed_tasks: 推迟任务列表

        Returns:
            模式聚类列表
        """
        patterns = defaultdict(lambda: {
            "pattern_id": "",
            "name": "",
            "frequency": 0,
            "examples": [],
            "common_features": set(),
            "task_types": defaultdict(int)
        })

        for delayed_task in delayed_tasks:
            # 获取示例任务
            examples = delayed_task.get("examples", [])
            if not examples:
                continue

            # 使用第一个示例提取特征
            first_example = examples[0]
            task_desc = first_example.get("description", "")
            features = self.extract_features(task_desc)

            # 生成模式ID
            pattern_id = self._generate_pattern_id(features)

            # 更新模式数据
            patterns[pattern_id]["pattern_id"] = pattern_id
            patterns[pattern_id]["frequency"] += delayed_task["delay_count"]
            patterns[pattern_id]["examples"].extend(examples[:3])  # 每个模式最多3个示例
            patterns[pattern_id]["task_types"][features["type"]] += 1

            # 收集共同特征
            for key, value in features.items():
                if value != "unknown":
                    patterns[pattern_id]["common_features"].add(f"{key}:{value}")

        # 生成模式名称
        for pattern_id, pattern_data in patterns.items():
            pattern_data["name"] = self._generate_pattern_name(
                pattern_id, pattern_data["task_types"]
            )
            pattern_data["common_features"] = list(pattern_data["common_features"])

        # 转换为列表并排序
        pattern_list = list(patterns.values())
        pattern_list.sort(key=lambda x: x["frequency"], reverse=True)

        return pattern_list

    def _generate_pattern_id(self, features: Dict) -> str:
        """生成模式ID"""
        return f"{features['type']}_{features['complexity']}_{features['creativity']}"

    def _generate_pattern_name(self, pattern_id: str, task_types: Dict) -> str:
        """生成模式名称"""
        # 获取最常见的任务类型
        most_common_type = max(task_types.items(), key=lambda x: x[1])[0]

        type_names = {
            "writing": "写作",
            "planning": "规划",
            "learning": "学习",
            "communication": "沟通",
            "coding": "编程",
            "unknown": "任务"
        }

        type_name = type_names.get(most_common_type, "任务")

        # 根据模式ID生成名称
        if "high" in pattern_id:
            return f"复杂{type_name}逃避"
        elif "planning" in pattern_id:
            return f"{type_name}逃避"
        else:
            return f"{type_name}推迟"

    def generate_pattern_report(self, patterns: List[Dict]) -> Dict:
        """
        生成模式分析报告

        Args:
            patterns: 模式列表

        Returns:
            分析报告
        """
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_patterns": len(patterns),
            "patterns": []
        }

        for pattern in patterns:
            pattern_report = {
                "pattern_id": pattern["pattern_id"],
                "name": pattern["name"],
                "frequency": pattern["frequency"],
                "examples": [ex["description"] for ex in pattern["examples"][:3]],
                "common_features": pattern["common_features"],
                "suggested_solution": self._suggest_solution(pattern)
            }
            report["patterns"].append(pattern_report)

        return report

    def _suggest_solution(self, pattern: Dict) -> str:
        """
        为模式生成解决方案建议

        Args:
            pattern: 模式数据

        Returns:
            解决方案建议
        """
        pattern_id = pattern["pattern_id"]
        name = pattern["name"]

        # 根据模式类型提供建议
        if "planning" in pattern_id and "high" in pattern_id:
            return (
                "💡 建议拆解为小任务：\n"
                "1. 先列出大纲或框架（5分钟）\n"
                "2. 填充每个部分的具体内容（15分钟/部分）\n"
                "3. 使用模板加速（搜索相关模板）"
            )
        elif "writing" in pattern_id:
            return (
                "💡 应对写作逃避：\n"
                "1. 接受'初稿可以是垃圾'的心态\n"
                "2. 先写，不修改（写作和编辑分开）\n"
                "3. 设定小目标（如'先写100字'）\n"
                "4. 使用番茄钟（25分钟）"
            )
        elif "learning" in pattern_id:
            return (
                "💡 应对学习拖延：\n"
                "1. 设定具体的学习目标（不是'学Python'而是'学会用Python读取文件'）\n"
                "2. 使用项目驱动学习（边做边学）\n"
                "3. 找学习伙伴或社群（增加外部压力）"
            )
        elif "communication" in pattern_id:
            return (
                "💡 应对沟通回避：\n"
                "1. 准备话术或提纲\n"
                "2. 先用文字而非语音/当面\n"
                "3. 设定时间上限（如'只聊15分钟'）\n"
                "4. 练习常见场景的应对"
            )
        else:
            return (
                "💡 通用建议：\n"
                "1. 任务拆解（将大任务拆为小步骤）\n"
                "2. 2分钟规则（如果<2分钟，立即做）\n"
                "3. 找 accountability 伙伴\n"
                "4. 奖励自己（完成小任务后给小奖励）"
            )

    def save_patterns(self, patterns_report: Dict):
        """
        保存模式分析结果

        Args:
            patterns_report: 模式分析报告
        """
        with open(self.patterns_file, 'w', encoding='utf-8') as f:
            json.dump(patterns_report, f, ensure_ascii=False, indent=2)

    def load_patterns(self) -> Optional[Dict]:
        """
        加载已保存的模式分析

        Returns:
            模式分析报告，如果不存在返回None
        """
        if not self.patterns_file.exists():
            return None

        try:
            with open(self.patterns_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None

    def check_escape_pattern(self, task: str) -> Optional[Dict]:
        """
        检查任务是否触发已知逃避模式

        Args:
            task: 任务描述

        Returns:
            如果触发模式返回预警信息，否则返回None
        """
        patterns_report = self.load_patterns()
        if not patterns_report:
            return None

        # 提取任务特征
        features = self.extract_features(task)
        pattern_id = self._generate_pattern_id(features)

        # 查找匹配的模式
        for pattern in patterns_report.get("patterns", []):
            if pattern["pattern_id"] == pattern_id and pattern["frequency"] >= 5:
                return {
                    "warning": f"⚠️  检测到可能触发 '{pattern['name']}' 模式",
                    "pattern_name": pattern["name"],
                    "frequency": pattern["frequency"],
                    "examples": pattern["examples"][:2],
                    "suggestion": pattern["suggested_solution"],
                    "alternative": "建议拆解为小任务或使用模板"
                }

        return None

    def analyze(self, days: int = 30) -> Dict:
        """
        执行完整的逃避模式分析

        Args:
            days: 分析最近多少天的数据

        Returns:
            分析报告
        """
        print(f"📊 分析最近{days}天的逃避模式...")

        # 加载历史数据
        plans = self.load_history(days)
        if not plans:
            print("⚠️  未找到历史计划数据")
            print("   提示: 需要使用priority-coach Skill至少3天才能分析模式")
            return {"error": "no_data"}

        print(f"✓ 加载了 {len(plans)} 天的计划数据")

        # 识别推迟任务
        delayed_tasks = self.identify_delayed_tasks(plans)
        if not delayed_tasks:
            print("✓ 未发现明显的逃避模式")
            return {"patterns": []}

        print(f"✓ 发现 {len(delayed_tasks)} 个反复推迟的任务")

        # 聚类分析
        patterns = self.cluster_by_features(delayed_tasks)
        print(f"✓ 识别出 {len(patterns)} 个逃避模式")

        # 生成报告
        report = self.generate_pattern_report(patterns)

        # 保存报告
        self.save_patterns(report)
        print(f"✓ 报告已保存到 {self.patterns_file}")

        return report

    def print_report(self, report: Dict):
        """
        打印分析报告

        Args:
            report: 分析报告
        """
        if "error" in report:
            return

        patterns = report.get("patterns", [])
        if not patterns:
            print("\n✅ 太棒了！未发现明显的逃避模式。")
            return

        print(f"\n{'='*60}")
        print(f"📊 逃避模式分析报告")
        print(f"{'='*60}")
        print(f"分析时间: {report.get('generated_at', 'N/A')[:10]}")
        print(f"识别模式数: {report.get('total_patterns', 0)}")
        print(f"{'='*60}\n")

        for i, pattern in enumerate(patterns, 1):
            print(f"模式 {i}: {pattern['name']}")
            print(f"  频率: {pattern['frequency']} 次推迟")
            print(f"  特征: {', '.join(pattern['common_features'])}")

            print(f"  示例任务:")
            for example in pattern['examples'][:3]:
                print(f"    - {example}")

            print(f"\n{pattern['suggested_solution']}\n")
            print(f"{'─'*60}\n")


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="分析任务逃避模式",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 分析最近30天的数据
  python analyze_escape_patterns.py

  # 分析最近60天的数据
  python analyze_escape_patterns.py --days 60

  # 检查特定任务是否触发逃避模式
  python analyze_escape_patterns.py --check "完成Q1报告"
        """
    )

    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="分析最近多少天的数据（默认30天）"
    )

    parser.add_argument(
        "--check",
        type=str,
        metavar="TASK",
        help="检查特定任务是否触发逃避模式"
    )

    args = parser.parse_args()

    analyzer = EscapePatternAnalyzer()

    if args.check:
        # 检查任务模式
        result = analyzer.check_escape_pattern(args.check)
        if result:
            print(f"\n{result['warning']}")
            print(f"模式频率: {result['frequency']} 次")
            print(f"建议: {result['suggestion']}")
        else:
            print(f"\n✅ 任务 '{args.check}' 未触发已知逃避模式")
    else:
        # 执行完整分析
        report = analyzer.analyze(args.days)
        analyzer.print_report(report)


if __name__ == "__main__":
    main()
