#!/usr/bin/env python3
"""
价值评分计算器 (Value Score Calculator)

计算任务的价值分数（1-5分），基于用户长期目标和任务特征。

算法公式：
Value = (goal_weight × relevance) × (urgency × 0.3 + importance × 0.7)

其中：
- goal_weight: 目标权重（从user_goals.json读取，0-1）
- relevance: 任务与目标的相关性（0-1，AI判断）
- urgency: 紧迫性（1-5，基于截止日期）
- importance: 重要性（1-5，基于影响范围）
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ValueScoreCalculator:
    """价值评分计算器"""

    def __init__(self, data_dir: Optional[str] = None):
        """
        初始化计算器

        Args:
            data_dir: 用户数据目录，默认为 ~/.claude/priority-coach/
        """
        if data_dir is None:
            data_dir = Path.home() / ".claude" / "priority-coach"
        else:
            data_dir = Path(data_dir)

        self.data_dir = Path(data_dir)
        self.goals_file = self.data_dir / "user_goals.json"

    def load_user_goals(self) -> Dict:
        """
        加载用户长期目标

        Returns:
            用户目标字典，如果文件不存在返回默认目标

        默认目标：
        - 职业发展（50%权重）
        - 个人成长（30%权重）
        - 生活平衡（20%权重）
        """
        if not self.goals_file.exists():
            return self._get_default_goals()

        try:
            with open(self.goals_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"⚠️  警告: 无法读取用户目标文件 ({e})")
            print("使用默认目标")
            return self._get_default_goals()

    def _get_default_goals(self) -> Dict:
        """获取默认目标"""
        return {
            "version": "1.0",
            "last_updated": "2025-03-03",
            "goals": [
                {
                    "id": "goal_career",
                    "title": "职业发展",
                    "category": "career",
                    "priority_weight": 0.5,
                    "keywords": ["工作", "项目", "技能", "学习", "职业", "业务"]
                },
                {
                    "id": "goal_growth",
                    "title": "个人成长",
                    "category": "self_development",
                    "priority_weight": 0.3,
                    "keywords": ["健康", "运动", "阅读", "冥想", "成长"]
                },
                {
                    "id": "goal_life",
                    "title": "生活平衡",
                    "category": "life_balance",
                    "priority_weight": 0.2,
                    "keywords": ["家庭", "朋友", "休闲", "娱乐", "生活"]
                }
            ]
        }

    def calculate_relevance(self, task: str, goals: List[Dict]) -> Tuple[float, Optional[Dict]]:
        """
        计算任务与目标的相关性

        Args:
            task: 任务描述
            goals: 目标列表

        Returns:
            (相关性分数, 最相关的目标)
            相关性分数范围: 0-1
        """
        task_lower = task.lower()
        max_relevance = 0.0
        best_goal = None

        for goal in goals:
            keywords = goal.get("keywords", [])
            relevance = 0.0

            # 检查关键词匹配
            for keyword in keywords:
                if keyword.lower() in task_lower:
                    relevance += 0.3

            # 限制最大相关性为1.0
            relevance = min(relevance, 1.0)

            if relevance > max_relevance:
                max_relevance = relevance
                best_goal = goal

        # 如果没有匹配关键词，使用启发式规则
        if max_relevance == 0.0:
            max_relevance = self._heuristic_relevance(task)
            best_goal = goals[0]  # 默认第一个目标

        return max_relevance, best_goal

    def _heuristic_relevance(self, task: str) -> float:
        """
        启发式相关性判断

        基于任务特征的简单规则：
        - 工作/业务相关: 0.8
        - 学习/成长相关: 0.7
        - 生活/娱乐相关: 0.4
        - 琐碎任务: 0.2
        """
        task_lower = task.lower()

        # 工作/业务相关
        work_keywords = ["项目", "报告", "会议", "客户", "代码", "开发", "设计", "方案"]
        if any(kw in task_lower for kw in work_keywords):
            return 0.8

        # 学习/成长相关
        growth_keywords = ["学习", "阅读", "课程", "研究", "练习"]
        if any(kw in task_lower for kw in growth_keywords):
            return 0.7

        # 生活/健康相关
        life_keywords = ["健身", "运动", "医生", "家庭", "朋友"]
        if any(kw in task_lower for kw in life_keywords):
            return 0.4

        # 琐碎任务
        trivial_keywords = ["邮件", "消息", "通知", "整理", "打扫"]
        if any(kw in task_lower for kw in trivial_keywords):
            return 0.2

        # 默认中等相关性
        return 0.5

    def calculate_urgency(self, task: str, deadline: Optional[str] = None) -> float:
        """
        计算紧迫性（1-5分）

        Args:
            task: 任务描述
            deadline: 截止日期（YYYY-MM-DD格式）

        Returns:
            紧迫性分数（1-5）
        """
        # 如果有明确的deadline
        if deadline:
            try:
                deadline_date = datetime.strptime(deadline, "%Y-%m-%d").date()
                today = datetime.now().date()
                days_left = (deadline_date - today).days

                if days_left <= 0:
                    return 5.0  # 已过期或今天到期
                elif days_left <= 1:
                    return 4.5  # 明天到期
                elif days_left <= 3:
                    return 4.0  # 3天内
                elif days_left <= 7:
                    return 3.0  # 一周内
                elif days_left <= 14:
                    return 2.0  # 两周内
                else:
                    return 1.0  # 不紧急
            except:
                pass

        # 基于任务描述的启发式判断
        task_lower = task.lower()

        # 高紧急性指标
        urgent_keywords = ["紧急", "立即", "马上", "今天", "明天", "明天前", "asap", "urgent"]
        if any(kw in task_lower for kw in urgent_keywords):
            return 4.5

        # 中紧急性指标
        medium_keywords = ["本周", "这周", "week"]
        if any(kw in task_lower for kw in medium_keywords):
            return 3.0

        # 低紧急性指标
        low_keywords = ["有空", "稍后", "以后", "someday", "maybe"]
        if any(kw in task_lower for kw in low_keywords):
            return 1.0

        # 默认中等紧迫性
        return 2.5

    def calculate_importance(self, task: str) -> float:
        """
        计算重要性（1-5分）

        Args:
            task: 任务描述

        Returns:
            重要性分数（1-5）
        """
        task_lower = task.lower()

        # 高重要性指标
        high_keywords = ["核心", "关键", "重要", "必须", "里程碑", "mvp", "deadline"]
        if any(kw in task_lower for kw in high_keywords):
            return 5.0

        # 中高重要性
        medium_high_keywords = ["应该", "需要", "最好"]
        if any(kw in task_lower for kw in medium_high_keywords):
            return 4.0

        # 中等重要性
        medium_keywords = ["计划", "安排", "可以"]
        if any(kw in task_lower for kw in medium_keywords):
            return 3.0

        # 低重要性
        low_keywords = ["琐碎", "顺便", "如果", "可能"]
        if any(kw in task_lower for kw in low_keywords):
            return 2.0

        # 默认中等重要性
        return 3.0

    def score_task(self, task: str, deadline: Optional[str] = None) -> Dict:
        """
        计算任务的综合价值分数

        Args:
            task: 任务描述
            deadline: 截止日期（可选）

        Returns:
            包含以下字段的字典：
            - value_score: 价值分数（1-5）
            - goal_alignment: 目标对齐信息
            - urgency: 紧迫性分数
            - importance: 重要性分数
            - explanation: 评分说明
        """
        # 加载用户目标
        goals_data = self.load_user_goals()
        goals = goals_data.get("goals", [])

        # 计算相关性
        relevance, best_goal = self.calculate_relevance(task, goals)

        # 获取目标权重
        goal_weight = best_goal.get("priority_weight", 0.5) if best_goal else 0.5

        # 计算紧迫性和重要性
        urgency = self.calculate_urgency(task, deadline)
        importance = self.calculate_importance(task)

        # 计算价值分数
        # Value = (goal_weight × relevance) × (urgency × 0.3 + importance × 0.7)
        weighted_goal = goal_weight * relevance
        weighted_importance = (urgency * 0.3 + importance * 0.7)
        raw_score = weighted_goal * weighted_importance * 5  # 放大到5分制

        # 限制在1-5分范围
        value_score = max(1.0, min(5.0, raw_score))

        # 生成说明
        explanation = self._generate_explanation(
            task, value_score, best_goal, relevance, urgency, importance
        )

        return {
            "value_score": round(value_score, 1),
            "goal_alignment": {
                "goal_id": best_goal.get("id") if best_goal else None,
                "goal_title": best_goal.get("title") if best_goal else "未明确",
                "relevance": round(relevance, 2),
                "goal_weight": goal_weight
            },
            "urgency": round(urgency, 1),
            "importance": round(importance, 1),
            "explanation": explanation
        }

    def _generate_explanation(
        self,
        task: str,
        value_score: float,
        goal: Optional[Dict],
        relevance: float,
        urgency: float,
        importance: float
    ) -> str:
        """生成评分说明"""
        lines = []

        # 价值等级
        if value_score >= 4.5:
            lines.append("🔥 最高价值任务（5分）")
            lines.append("→ 直接推进核心目标，必须优先完成")
        elif value_score >= 4.0:
            lines.append("⭐ 高价值任务（4分）")
            lines.append("→ 重要但不紧急，规划固定时间块")
        elif value_score >= 3.0:
            lines.append("📌 中等价值任务（3分）")
            lines.append("→ 维持性工作，安排在合适时段")
        elif value_score >= 2.0:
            lines.append("🔹 低价值任务（2分）")
            lines.append("→ 可延后或委派")
        else:
            lines.append("⚪️ 极低价值任务（1分）")
            lines.append("→ 建议删除或严格限制时间")

        lines.append("")  # 空行

        # 目标对齐
        if goal:
            lines.append(f"🎯 目标对齐: {goal.get('title', 'N/A')}")
            lines.append(f"   相关性: {int(relevance * 100)}% | 权重: {int(goal.get('priority_weight', 0.5) * 100)}%")

        # 紧迫性和重要性
        lines.append(f"⏰ 紧迫性: {urgency:.1f}/5")
        lines.append(f"💎 重要性: {importance:.1f}/5")

        return "\n".join(lines)

    def batch_score_tasks(self, tasks: List[str]) -> List[Dict]:
        """
        批量计算任务价值分数

        Args:
            tasks: 任务描述列表

        Returns:
            评分结果列表，按价值分数降序排列
        """
        results = []
        for task in tasks:
            result = self.score_task(task)
            result["task"] = task
            results.append(result)

        # 按价值分数降序排序
        results.sort(key=lambda x: x["value_score"], reverse=True)
        return results


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法: python calculate_value_score.py <任务描述>")
        print("示例: python calculate_value_score.py '完成AI教练产品MVP开发'")
        sys.exit(1)

    task = " ".join(sys.argv[1:])

    calculator = ValueScoreCalculator()
    result = calculator.score_task(task)

    print(f"\n📊 任务价值评分结果")
    print(f"{'='*50}")
    print(f"任务: {task}")
    print(f"{'='*50}")
    print(result["explanation"])
    print(f"{'='*50}")
    print(f"最终价值分数: {result['value_score']}/5")


if __name__ == "__main__":
    main()
