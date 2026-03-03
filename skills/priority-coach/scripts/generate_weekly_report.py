#!/usr/bin/env python3
"""
绩效周报生成器 (Weekly Report Generator)

自动分析一周数据，生成成就报告和下周建议。

功能：
- 统计本周完成的番茄钟数
- 计算各目标推进度
- 识别TOP3逃避任务
- 生成Markdown格式周报
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict


class WeeklyReportGenerator:
    """绩效周报生成器"""

    def __init__(self, data_dir: Optional[str] = None):
        """
        初始化周报生成器

        Args:
            data_dir: 用户数据目录，默认为 ~/.claude/priority-coach/
        """
        if data_dir is None:
            data_dir = Path.home() / ".claude" / "priority-coach"
        else:
            data_dir = Path(data_dir)

        self.data_dir = Path(data_dir)
        self.plans_dir = self.data_dir / "daily_plans"
        self.goals_file = self.data_dir / "user_goals.json"
        self.patterns_file = self.data_dir / "analytics" / "escape_patterns.json"
        self.reports_dir = self.data_dir / "weekly_reports"

        # 确保目录存在
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def load_goals(self) -> Dict:
        """加载用户目标"""
        if not self.goals_file.exists():
            return {}

        try:
            with open(self.goals_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    def load_week_plans(self, weeks_back: int = 0) -> List[Dict]:
        """
        加载一周的每日计划

        Args:
            weeks_back: 0=本周, 1=上周, 2=上上周

        Returns:
            每日计划列表
        """
        today = datetime.now()
        # 计算本周的周一
        monday = today - timedelta(days=today.weekday())
        # 减去指定的周数
        start_date = monday - timedelta(weeks=weeks_back)
        end_date = start_date + timedelta(days=6)

        plans = []
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
                    pass

            current_date += timedelta(days=1)

        return plans

    def calculate_weekly_stats(self, plans: List[Dict]) -> Dict:
        """
        计算本周统计数据

        Returns:
            本周统计
        """
        total_pomodoros = 0
        completed_tasks = 0
        total_tasks = 0
        total_value_score = 0
        daily_stats = []

        for plan in plans:
            # 番茄钟统计
            total_pomodoros += plan.get("total_pomodoros", 0)

            # 任务统计
            tasks = plan.get("tasks", [])
            completed = sum(1 for t in tasks if t.get("status") == "completed")

            completed_tasks += completed
            total_tasks += len(tasks)

            # 价值分数
            total_value_score += sum(
                t.get("value_score", 0)
                for t in tasks
                if t.get("status") == "completed"
            )

            # 每日统计
            daily_stats.append({
                "date": plan.get("date", ""),
                "pomodoros": plan.get("total_pomodoros", 0),
                "completion_rate": completed / len(tasks) if tasks else 0,
                "completed": completed,
                "total": len(tasks)
            })

        completion_rate = completed_tasks / total_tasks if total_tasks > 0 else 0

        return {
            "total_pomodoros": total_pomodoros,
            "completed_tasks": completed_tasks,
            "total_tasks": total_tasks,
            "completion_rate": completion_rate,
            "total_value_score": total_value_score,
            "daily_stats": daily_stats,
            "days_with_data": len(plans)
        }

    def calculate_goal_weekly_progress(
        self,
        plans: List[Dict],
        goals: Dict
    ) -> List[Dict]:
        """
        计算各目标本周推进情况

        Returns:
            各目标的周推进数据
        """
        goal_list = goals.get("goals", [])

        # 统计每个目标的数据
        goal_stats = {}

        for goal in goal_list:
            goal_id = goal.get("id")
            goal_title = goal.get("title")

            goal_stats[goal_id] = {
                "goal_id": goal_id,
                "goal_title": goal_title,
                "category": goal.get("category"),
                "completed_value_5": 0,  # 价值5分的任务数
                "completed_value_4": 0,  # 价值4分的任务数
                "total_value_score": 0,
                "total_tasks": 0,
                "completed_tasks": 0,
                "keywords": goal.get("keywords", [])
            }

        # 遍历所有计划
        for plan in plans:
            tasks = plan.get("tasks", [])

            for task in tasks:
                if task.get("status") != "completed":
                    continue

                # 找到对应的目标
                task_desc = task.get("description", "").lower()
                value_score = task.get("value_score", 0)

                matched_goal_id = None
                for goal_id, goal_data in goal_stats.items():
                    keywords = goal_data["keywords"]
                    if any(kw.lower() in task_desc for kw in keywords):
                        matched_goal_id = goal_id
                        break

                if matched_goal_id:
                    stats = goal_stats[matched_goal_id]
                    stats["completed_tasks"] += 1
                    stats["total_value_score"] += value_score

                    if value_score >= 4.5:
                        stats["completed_value_5"] += 1
                    elif value_score >= 4.0:
                        stats["completed_value_4"] += 1

        # 计算总数
        for plan in plans:
            tasks = plan.get("tasks", [])
            for task in tasks:
                task_desc = task.get("description", "").lower()

                for goal_id, goal_data in goal_stats.items():
                    keywords = goal_data["keywords"]
                    if any(kw.lower() in task_desc for kw in keywords):
                        goal_stats[goal_id]["total_tasks"] += 1
                        break

        # 转换为列表并排序
        goal_progress = list(goal_stats.values())
        goal_progress.sort(key=lambda x: x["total_value_score"], reverse=True)

        return goal_progress

    def identify_top_achievements(
        self,
        plans: List[Dict],
        goals: Dict
    ) -> List[Dict]:
        """
        识别本周TOP3成就

        Returns:
            TOP3成就列表
        """
        # 收集所有完成的任务
        all_completed = []

        for plan in plans:
            tasks = plan.get("tasks", [])

            for task in tasks:
                if task.get("status") == "completed":
                    all_completed.append({
                        "description": task.get("description", ""),
                        "value_score": task.get("value_score", 0),
                        "category": task.get("category", ""),
                        "date": plan.get("date", "")
                    })

        # 按价值分数排序
        all_completed.sort(key=lambda x: x["value_score"], reverse=True)

        # 取TOP3
        return all_completed[:3]

    def identify_escape_tasks(self, plans: List[Dict]) -> List[Dict]:
        """
        识别逃避任务（反复推迟的任务）

        Returns:
            逃避任务列表
        """
        task_delay_count = defaultdict(int)
        task_examples = defaultdict(list)

        for plan in plans:
            tasks = plan.get("tasks", [])

            for task in tasks:
                status = task.get("status", "")
                description = task.get("description", "")

                if status in ["delayed", "postponed", "not_started"]:
                    # 简化任务描述
                    task_key = self._normalize_task(description)
                    task_delay_count[task_key] += 1
                    task_examples[task_key].append({
                        "description": description,
                        "date": plan.get("date", ""),
                        "value_score": task.get("value_score", 0)
                    })

        # 筛选出推迟>=2次的任务
        escape_tasks = []
        for task_key, count in task_delay_count.items():
            if count >= 2:
                examples = task_examples[task_key][:2]  # 最多2个示例
                escape_tasks.append({
                    "task_key": task_key,
                    "delay_count": count,
                    "examples": examples,
                    "avg_value_score": sum(e["value_score"] for e in examples) / len(examples)
                })

        # 按推迟次数排序
        escape_tasks.sort(key=lambda x: x["delay_count"], reverse=True)

        return escape_tasks[:3]  # TOP3

    def _normalize_task(self, description: str) -> str:
        """标准化任务描述"""
        desc = description.lower().strip()

        # 移除常见前缀
        prefixes = ["完成", "做", "写", "准备", "创建"]
        for prefix in prefixes:
            if desc.startswith(prefix):
                desc = desc[len(prefix):].strip()

        # 提取核心（前8个字符）
        return desc[:8] if len(desc) > 8 else desc

    def generate_next_week_suggestions(
        self,
        week_stats: Dict,
        goal_progress: List[Dict],
        goals: Dict
    ) -> List[str]:
        """
        生成本周建议

        Returns:
            建议列表
        """
        suggestions = []

        # 基于完成率的建议
        completion_rate = week_stats["completion_rate"]

        if completion_rate >= 0.8:
            suggestions.append("🎉 本周表现优秀！继续保持这个节奏")
        elif completion_rate >= 0.6:
            suggestions.append("👍 本周表现不错，下周争取完成率突破80%")
        else:
            suggestions.append("💪 本周遇到一些挑战，分析原因后重新出发")

        # 基于番茄钟数的建议
        total_pomodoros = week_stats["total_pomodoros"]
        if total_pomodoros < 20:
            suggestions.append(f"⏰ 本周番茄钟数较少({total_pomodoros}个)，考虑是否任务量不足或遇到阻碍")

        # 基于目标进度的建议
        goal_list = goals.get("goals", [])

        for goal in goal_list:
            deadline = goal.get("deadline")
            if not deadline:
                continue

            try:
                deadline_date = datetime.strptime(deadline, "%Y-%m-%d").date()
                today = datetime.now().date()
                days_left = (deadline_date - today).days

                if days_left <= 14:  # 2周内
                    goal_title = goal.get("title")
                    suggestions.append(f"🔥 {goal_title} deadline还有{days_left}天，下周需要重点推进")
            except:
                pass

        # 基于逃避任务的建议
        escape_tasks = self.identify_escape_tasks(self.load_week_plans(0))
        if escape_tasks:
            top_escape = escape_tasks[0]
            suggestions.append(
                f"⚠️  注意: '{top_escape['task_key']}' 被推迟了{top_escape['delay_count']}次\n"
                f"   考虑拆解任务或寻找帮助"
            )

        return suggestions

    def generate_report(self, weeks_back: int = 0) -> str:
        """
        生成绩效周报

        Args:
            weeks_back: 0=本周, 1=上周

        Returns:
            Markdown格式的周报
        """
        # 确定日期范围
        today = datetime.now()
        monday = today - timedelta(days=today.weekday())
        start_date = monday - timedelta(weeks=weeks_back)
        end_date = start_date + timedelta(days=6)

        week_num = start_date.isocalendar()[1]
        year = start_date.year

        # 格式化日期范围
        date_range = f"{start_date.month}月{start_date.day}日 - {end_date.month}月{end_date.day}日"

        # 加载数据
        plans = self.load_week_plans(weeks_back)
        goals = self.load_goals()

        if not plans:
            return f"""
📊 **绩效周报** - {year}年第{week_num}周

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ℹ️  本周({date_range})暂无数据

💡 **提示**:
- 需要每天使用 priority-coach 创建今日计划
- 数据积累后才能生成周报

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        # 计算统计
        week_stats = self.calculate_weekly_stats(plans)
        goal_progress = self.calculate_goal_weekly_progress(plans, goals)
        top_achievements = self.identify_top_achievements(plans, goals)
        escape_tasks = self.identify_escape_tasks(plans)
        suggestions = self.generate_next_week_suggestions(week_stats, goal_progress, goals)

        # 生成报告
        report = f"""
📊 **绩效周报** - {year}年第{week_num}周
📅 {date_range}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 📈 本周概览

{'✅' if week_stats['completion_rate'] >= 0.8 else '⚠️' if week_stats['completion_rate'] >= 0.5 else '❌'}
**完成率**: {week_stats['completion_rate']*100:.0f}%
   ({week_stats['completed_tasks']}/{week_stats['total_tasks']} 个任务)

🍅 **番茄钟**: {week_stats['total_pomodoros']}个
   (有数据的{week_stats['days_with_data']}天)

💎 **价值得分**: {week_stats['total_value_score']:.1f}分
   (所有完成任务的价值总分)

---

## 🎯 目标推进情况

"""

        # 目标推进详情
        if goal_progress:
            for goal in goal_progress:
                goal_title = goal["goal_title"]
                if len(goal_title) > 20:
                    goal_title = goal_title[:17] + "..."

                completed = goal["completed_tasks"]
                total = goal["total_tasks"]
                value_score = goal["total_value_score"]

                if total > 0:
                    progress_rate = completed / total
                    bar = "█" * int(progress_rate * 10) + "░" * (10 - int(progress_rate * 10))

                    report += f"""
### {goal_title}

进度: [{bar}] {progress_rate*100:.0f}%
完成: {completed}/{total} 个任务
价值得分: {value_score:.1f}分

"""
                else:
                    report += f"""
### {goal_title}

本周暂无相关任务
"""
        else:
            report += "\n本周暂无目标推进数据\n\n"

        # TOP3成就
        if top_achievements:
            report += f"""
---

## 🏆 本周TOP3成就

"""
            for i, achievement in enumerate(top_achievements, 1):
                desc = achievement["description"]
                if len(desc) > 30:
                    desc = desc[:27] + "..."
                value = achievement["value_score"]

                report += f"""
**{i}. {desc}**
   价值: {value:.1f}分 | 日期: {achievement['date']}
"""
        else:
            report += f"""
---

## 🏆 本周TOP3成就

本周暂无完成的任务
"""

        # 逃避任务
        if escape_tasks:
            report += f"""
---

## ⚠️  逃避任务TOP{len(escape_tasks)}

"""
            for i, task in enumerate(escape_tasks, 1):
                task_key = task["task_key"]
                count = task["delay_count"]
                value = task["avg_value_score"]

                report += f"""
**{i}. {task_key}**
   推迟: {count}次 | 平均价值: {value:.1f}分
"""

                # 显示示例
                if task["examples"]:
                    example = task["examples"][0]
                    desc = example["description"]
                    if len(desc) > 40:
                        desc = desc[:37] + "..."
                    report += f"   示例: {desc}\n"
        else:
            report += f"""
---

## ⚠️  逃避任务

✅ 太棒了！本周没有明显的逃避行为
"""

        # 下周建议
        if suggestions:
            report += f"""
---

## 💡 下周建议

"""
            for suggestion in suggestions:
                report += f"{suggestion}\n\n"

        # 每日数据
        daily_stats = week_stats["daily_stats"]
        if daily_stats:
            report += f"""
---

## 📅 每日数据

| 日期 | 番茄钟 | 完成率 | 完成/总数 |
|------|--------|--------|-----------|
"""
            for day_stat in daily_stats:
                date_str = day_stat["date"].split("/")[-1]  # 只显示日
                pomodoros = day_stat["pomodoros"]
                rate = day_stat["completion_rate"]
                completed = day_stat["completed"]
                total = day_stat["total"]

                report += f"| {date_str}日 | {pomodoros}个 | {rate*100:.0f}% | {completed}/{total} |\n"

        # 鼓励语
        completion_rate = week_stats["completion_rate"]
        if completion_rate >= 0.8:
            report += f"""

---

## 🎉 本周总结

优秀的一周！完成率达到{completion_rate*100:.0f}%，你的努力得到了回报。

继续保持这个节奏，你的目标正在一步步实现！💪🚀
"""
        elif completion_rate >= 0.5:
            report += f"""

---

## 🎯 本周总结

还不错的一周，完成率{completion_rate*100:.0f}%。

分析一下未完成的任务原因，下周做得更好！你可以的！🌟
"""
        else:
            report += f"""

---

## 🌱 本周总结

这周有些挑战，完成率{completion_rate*100:.0f}%。

但没关系，每个挑战都是成长的机会。重新出发，下周会更好！💪
"""

        report += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 **生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M")}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        return report

    def save_report(self, report: str, weeks_back: int = 0):
        """保存周报到文件"""
        today = datetime.now()
        year = today.year
        week_num = today.isocalendar()[1] - weeks_back

        filename = f"{year}-W{week_num:02d}.md"
        report_file = self.reports_dir / filename

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        return report_file


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="生成绩效周报",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成本周周报
  python generate_weekly_report.py

  # 生成上周周报
  python generate_weekly_report.py --last-week

  # 保存周报到文件
  python generate_weekly_report.py --save
        """
    )

    parser.add_argument(
        "--last-week",
        action="store_true",
        help="生成上周的周报"
    )

    parser.add_argument(
        "--save",
        action="store_true",
        help="保存周报到文件"
    )

    args = parser.parse_args()

    generator = WeeklyReportGenerator()
    weeks_back = 1 if args.last_week else 0

    report = generator.generate_report(weeks_back)
    print(report)

    if args.save:
        report_file = generator.save_report(report, weeks_back)
        print(f"\n✅ 周报已保存到: {report_file}")


if __name__ == "__main__":
    main()
