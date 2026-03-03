#!/usr/bin/env python3
"""
每日复盘生成器 (Daily Review Generator)

自动分析当天的任务完成情况，生成复盘总结和明日优化建议。

功能：
- 计划vs实际完成对比
- 时间估算偏差分析
- 目标推进度计算
- 明日优化建议
- 更新逃避模式数据
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class DailyReviewGenerator:
    """每日复盘生成器"""

    def __init__(self, data_dir: Optional[str] = None):
        """
        初始化复盘生成器

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
        self.analytics_dir = self.data_dir / "analytics"
        self.time_accuracy_file = self.analytics_dir / "time_accuracy.json"

        # 确保目录存在
        self.analytics_dir.mkdir(parents=True, exist_ok=True)

    def load_goals(self) -> Dict:
        """加载用户目标"""
        if not self.goals_file.exists():
            return {}

        try:
            with open(self.goals_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    def load_today_plan(self) -> Optional[Dict]:
        """加载今日计划"""
        today = datetime.now()
        date_str = today.strftime("%Y/%m/%d")
        plan_file = self.plans_dir / f"{date_str}.json"

        if not plan_file.exists():
            return None

        try:
            with open(plan_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None

    def calculate_completion_rate(self, plan: Dict) -> Tuple[float, int, int]:
        """
        计算完成率

        Returns:
            (完成率, 完成数, 总数)
        """
        tasks = plan.get("tasks", [])
        if not tasks:
            return 0.0, 0, 0

        total = len(tasks)
        completed = sum(1 for t in tasks if t.get("status") == "completed")
        completion_rate = completed / total if total > 0 else 0.0

        return completion_rate, completed, total

    def calculate_pomodoro_stats(self, plan: Dict) -> Tuple[float, float]:
        """
        计算番茄钟统计

        Returns:
            (计划番茄钟数, 实际完成番茄钟数)
        """
        planned = plan.get("total_pomodoros", 0)

        tasks = plan.get("tasks", [])
        actual = sum(
            task.get("actual_pomodoros", task.get("estimated_pomodoros", 0))
            for task in tasks
            if task.get("status") == "completed"
        )

        return planned, actual

    def analyze_time_deviation(self, plan: Dict) -> Dict:
        """
        分析时间估算偏差

        Returns:
            偏差分析结果
        """
        tasks = plan.get("tasks", [])
        deviations = []

        for task in tasks:
            if task.get("status") != "completed":
                continue

            estimated = task.get("estimated_pomodoros", 0)
            actual = task.get("actual_pomodoros", estimated)

            if estimated > 0:
                deviation = (actual - estimated) / estimated
                deviations.append({
                    "task": task.get("description", ""),
                    "estimated": estimated,
                    "actual": actual,
                    "deviation": deviation
                })

        if not deviations:
            return {"average_deviation": 0, "details": []}

        avg_deviation = sum(d["deviation"] for d in deviations) / len(deviations)

        # 保存到历史记录
        self._save_time_accuracy(avg_deviation)

        return {
            "average_deviation": avg_deviation,
            "details": deviations
        }

    def _save_time_accuracy(self, deviation: float):
        """保存时间准确度数据"""
        data = {}
        if self.time_accuracy_file.exists():
            try:
                with open(self.time_accuracy_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except:
                pass

        history = data.get("history", [])
        history.append({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "deviation": deviation
        })

        # 只保留最近30天的数据
        history = history[-30:]

        # 计算累计平均偏差
        cumulative_avg = sum(h["deviation"] for h in history) / len(history)

        data["history"] = history
        data["cumulative_average_deviation"] = cumulative_avg
        data["last_updated"] = datetime.now().isoformat()

        with open(self.time_accuracy_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def calculate_goal_progress(self, plan: Dict, goals: Dict) -> List[Dict]:
        """
        计算目标推进度

        Returns:
            各目标的推进情况
        """
        goal_list = goals.get("goals", [])
        tasks = plan.get("tasks", [])

        progress = []

        for goal in goal_list:
            goal_id = goal.get("id")
            goal_title = goal.get("title")

            # 找出相关的任务
            related_tasks = [
                t for t in tasks
                if t.get("goal_id") == goal_id or
                any(kw in t.get("description", "").lower()
                    for kw in goal.get("keywords", []))
            ]

            if not related_tasks:
                continue

            total = len(related_tasks)
            completed = sum(1 for t in related_tasks if t.get("status") == "completed")
            progress_rate = completed / total if total > 0 else 0.0

            total_value = sum(t.get("value_score", 0) for t in related_tasks if t.get("status") == "completed")

            progress.append({
                "goal_id": goal_id,
                "goal_title": goal_title,
                "completed_tasks": completed,
                "total_tasks": total,
                "progress_rate": progress_rate,
                "total_value_score": total_value
            })

        # 按价值分数降序排序
        progress.sort(key=lambda x: x["total_value_score"], reverse=True)

        return progress

    def generate_optimization_suggestions(
        self,
        time_analysis: Dict,
        goals_data: Dict
    ) -> List[str]:
        """
        生成明日优化建议

        Returns:
            建议列表
        """
        suggestions = []

        # 基于时间偏差的建议
        avg_dev = time_analysis.get("average_deviation", 0)

        if avg_dev > 0.3:
            suggestions.append(
                f"⏰ **时间估算偏大**: 任务平均耗时超出预期{int(avg_dev*100)}%\n"
                f"   → 建议: 明日估算时乘以1.{int((1+avg_dev)*10-10)}倍系数"
            )
        elif avg_dev < -0.2:
            suggestions.append(
                f"⏰ **时间估算偏小**: 你完成任务很快！\n"
                f"   → 建议: 可以尝试更 challenging 的任务量"
            )

        # 基于累计偏差的建议
        if self.time_accuracy_file.exists():
            try:
                with open(self.time_accuracy_file, 'r', encoding='utf-8') as f:
                    accuracy_data = json.load(f)

                cumulative = accuracy_data.get("cumulative_average_deviation", 0)

                if cumulative > 0.2:
                    suggestions.append(
                        f"📊 **长期趋势**: 你倾向于低估任务时间\n"
                        f"   → 建议: 系统已自动校准，明日估算会更准确"
                    )
            except:
                pass

        # 基于目标进度的建议
        goals_list = goals_data.get("goals", [])
        for goal in goals_list:
            deadline = goal.get("deadline")
            if deadline:
                try:
                    deadline_date = datetime.strptime(deadline, "%Y-%m-%d").date()
                    today = datetime.now().date()
                    days_left = (deadline_date - today).days

                    if days_left <= 7 and days_left > 0:
                        suggestions.append(
                            f"🔥 **紧急提醒**: {goal.get('title')} deadline还有{days_left}天\n"
                            f"   → 建议: 明日优先分配时间给这个目标"
                        )
                except:
                    pass

        return suggestions

    def calculate_days_to_deadline(self, goals: Dict) -> List[Dict]:
        """计算距离各目标deadline的天数"""
        goal_list = goals.get("goals", [])
        deadlines = []

        for goal in goal_list:
            deadline = goal.get("deadline")
            if not deadline:
                continue

            try:
                deadline_date = datetime.strptime(deadline, "%Y-%m-%d").date()
                today = datetime.now().date()
                days_left = (deadline_date - today).days

                deadlines.append({
                    "goal_title": goal.get("title"),
                    "deadline": deadline,
                    "days_left": days_left,
                    "urgent": days_left <= 7
                })
            except:
                pass

        # 按紧急程度排序
        deadlines.sort(key=lambda x: x["days_left"])

        return deadlines

    def generate_review(self) -> str:
        """
        生成每日复盘报告

        Returns:
            Markdown格式的复盘报告
        """
        today = datetime.now()
        today_str = today.strftime("%Y年%m月%d日")
        weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][today.weekday()]

        # 加载数据
        plan = self.load_today_plan()
        goals = self.load_goals()

        if not plan:
            return f"""
🌙 **每日复盘** - {today_str} {weekday}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ℹ️  未找到今日计划数据

💡 **提示**:
- 早上使用 `priority-coach 帮我规划今天` 创建今日计划
- 晚上使用 `priority-coach 今日总结` 生成复盘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        # 计算各项指标
        completion_rate, completed, total = self.calculate_completion_rate(plan)
        planned_pomodoros, actual_pomodoros = self.calculate_pomodoro_stats(plan)
        time_analysis = self.analyze_time_deviation(plan)
        goal_progress = self.calculate_goal_progress(plan, goals)
        suggestions = self.generate_optimization_suggestions(time_analysis, goals)
        deadlines = self.calculate_days_to_deadline(goals)

        # 生成报告
        report = f"""
🌙 **每日复盘** - {today_str} {weekday}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **今日完成度**

{'✅' if completion_rate >= 0.8 else '⚠️' if completion_rate >= 0.5 else '❌'} 完成率: {completion_rate*100:.0f}%
   完成任务: {completed}/{total}

🍅 **番茄钟统计**
   计划: {planned_pomodoros}个 | 实际: {actual_pomodoros:.1f}个
   完成率: {actual_pomodoros/planned_pomodoros*100:.0f}% (如果计划>0)
"""

        # 目标推进度
        if goal_progress:
            report += f"""
🎯 **目标推进度**

"""
            for progress in goal_progress[:3]:  # 只显示前3个
                goal_title = progress["goal_title"]
                if len(goal_title) > 15:
                    goal_title = goal_title[:12] + "..."
                rate = progress["progress_rate"]
                value = progress["total_value_score"]

                report += f"{goal_title}: {rate*100:.0f}%"
                if value > 0:
                    report += f" (价值{value:.1f}分)"
                report += "\n"

        # 时间偏差分析
        if time_analysis.get("details"):
            avg_dev = time_analysis["average_deviation"]

            report += f"""
⏰ **时间偏差分析**

"""

            if avg_dev > 0.2:
                report += f"⚠️  平均超出预期 {int(avg_dev*100)}%\n"
                report += f"→ 你的任务比预期更复杂\n"
            elif avg_dev < -0.2:
                report += f"✨ 平均节省 {int(abs(avg_dev)*100)}% 时间\n"
                report += f"→ 你的效率很高！\n"
            else:
                report += f"✅ 时间估算基本准确\n"

            # 显示偏差最大的任务
            details = time_analysis["details"]
            if details:
                details.sort(key=lambda x: abs(x["deviation"]), reverse=True)

                if len(details) > 0:
                    worst = details[0]
                    task_desc = worst["task"]
                    if len(task_desc) > 20:
                        task_desc = task_desc[:17] + "..."

                    dev = worst["deviation"]
                    if dev > 0.3:
                        report += f"\n最大偏差: {task_desc}\n"
                        report += f"   预估{worst['estimated']}番茄钟 → 实际{worst['actual']}番茄钟\n"

        # deadline提醒
        if deadlines:
            urgent_deadlines = [d for d in deadlines if d["days_left"] <= 7]
            if urgent_deadlines:
                report += f"""
🔥 **Deadline提醒**

"""
                for dl in urgent_deadlines[:2]:
                    days = dl["days_left"]
                    if days <= 0:
                        report += f"⚠️  {dl['goal_title']} - 已到期！\n"
                    elif days == 1:
                        report += f"⚠️  {dl['goal_title']} - 明天到期！\n"
                    else:
                        report += f"   {dl['goal_title']} - 还有{days}天\n"

        # 明日优化建议
        if suggestions:
            report += f"""
💡 **明日优化建议**

"""
            for i, suggestion in enumerate(suggestions, 1):
                report += f"{i}. {suggestion}\n"

        # 鼓励语
        if completion_rate >= 0.8:
            report += f"""
🎉 **太棒了！**

今天完成率{completion_rate*100:.0f}%，你的表现非常出色！

明天继续保持这个节奏，你离目标又近了一步！💪
"""
        elif completion_rate >= 0.5:
            report += f"""
👍 **不错！**

今天完成率{completion_rate*100:.0f}%，有些进展。

明天看看能不能把未完成的任务搞定？你可以的！🌟
"""
        else:
            report += f"""
💪 **加油！**

今天完成率{completion_rate*100:.0f}%，可能遇到了一些挑战。

别气馁，分析一下原因，明天重新开始！每个挑战都是成长的机会。🌱
"""

        report += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 **明日计划**

记得早上使用: `priority-coach 帮我规划今天`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        return report

    def save_review(self, review: str):
        """保存复盘到文件"""
        today = datetime.now()
        date_str = today.strftime("%Y/%m")
        review_file = self.analytics_dir / f"daily_reviews_{date_str}.md"

        # 追加模式写入
        with open(review_file, 'a', encoding='utf-8') as f:
            f.write(review + "\n\n")


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="生成每日复盘报告",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--save",
        action="store_true",
        help="保存复盘到文件"
    )

    args = parser.parse_args()

    generator = DailyReviewGenerator()
    review = generator.generate_review()

    print(review)

    if args.save:
        generator.save_review(review)
        print(f"✅ 复盘已保存到: {generator.analytics_dir}/daily_reviews_*.md")


if __name__ == "__main__":
    main()
