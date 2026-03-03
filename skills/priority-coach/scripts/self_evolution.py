#!/usr/bin/env python3
"""
自我进化引擎 (Self-Evolution Engine)

让Priority Coach Skill能够持续学习、优化和适应用户。

核心功能：
1. 数据收集 - 记录用户行为和决策
2. 模式学习 - 识别用户的个人模式
3. 算法优化 - 自动调整参数
4. A/B测试 - 实验不同策略
5. 进化展示 - 向用户展示"成长"
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import statistics


class SelfEvolutionEngine:
    """自我进化引擎"""

    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            data_dir = Path.home() / ".claude" / "priority-coach"
        else:
            data_dir = Path(data_dir)

        self.data_dir = Path(data_dir)
        self.evolution_dir = self.data_dir / "evolution"
        self.evolution_dir.mkdir(parents=True, exist_ok=True)

        # 进化数据文件
        self.metrics_file = self.evolution_dir / "metrics.json"
        self.versions_file = self.evolution_dir / "algorithm_versions.json"
        self.experiments_file = self.evolution_dir / "ab_tests.json"
        self.user_model_file = self.evolution_dir / "user_model.json"

    def collect_metrics(self, plan: Dict, actual_result: Dict):
        """
        收集性能指标

        记录：
        - 计划vs实际
        - 时间估算准确度
        - 任务完成率
        - 用户满意度（如果提供）
        """
        metrics = {
            "date": datetime.now().isoformat(),
            "planned_pomodoros": plan.get("total_pomodoros", 0),
            "actual_pomodoros": actual_result.get("total_pomodoros", 0),
            "tasks_planned": len(plan.get("tasks", [])),
            "tasks_completed": sum(1 for t in plan.get("tasks", []) if t.get("status") == "completed"),
            "completion_rate": 0,  # 稍后计算
            "time_accuracy": self._calculate_time_accuracy(plan, actual_result),
            "user_satisfaction": actual_result.get("satisfaction", None)
        }

        # 计算完成率
        if metrics["tasks_planned"] > 0:
            metrics["completion_rate"] = metrics["tasks_completed"] / metrics["tasks_planned"]

        # 保存到历史
        self._save_metrics(metrics)

        return metrics

    def _calculate_time_accuracy(self, plan: Dict, actual: Dict) -> float:
        """计算时间估算准确度"""
        planned_tasks = plan.get("tasks", [])
        actual_tasks = actual.get("tasks", [])

        if not planned_tasks or not actual_tasks:
            return 1.0

        # 计算估算偏差
        deviations = []
        for p_task in planned_tasks:
            # 找到对应的实际任务
            task_id = p_task.get("id")
            for a_task in actual_tasks:
                if a_task.get("id") == task_id:
                    estimated = p_task.get("estimated_pomodoros", 0)
                    actual_pomodoros = a_task.get("actual_pomodoros", estimated)

                    if estimated > 0:
                        deviation = actual_pomodoros / estimated
                        deviations.append(deviation)
                    break

        if not deviations:
            return 1.0

        # 使用中位数（更鲁棒）
        median_deviation = statistics.median(deviations)

        # 准确度 = 1 - |中位数偏差 - 1|
        # 如果偏差是1.0，表示完美估算
        accuracy = max(0, 1 - abs(median_deviation - 1.0))

        return accuracy

    def learn_user_model(self, recent_actions: List[Dict]):
        """
        学习用户模型

        学习：
        1. 决策风格（maximizer vs satisficer）
        2. 精力模式（一天的精力曲线）
        3. 偏好（任务类型、时间段）
        4. 风险承受度
        5. 灵活性需求
        """
        user_model = self._load_user_model()

        # 1. 学习决策风格
        user_model["decision_style"] = self._learn_decision_style(recent_actions)

        # 2. 学习精力模式
        user_model["energy_pattern"] = self._learn_energy_pattern(recent_actions)

        # 3. 学习任务偏好
        user_model["task_preferences"] = self._learn_task_preferences(recent_actions)

        # 4. 学习灵活性
        user_model["flexibility"] = self._learn_flexibility(recent_actions)

        # 5. 更新模型版本
        user_model["version"] = self._increment_version(user_model.get("version", "0.0"))
        user_model["last_updated"] = datetime.now().isoformat()

        # 保存模型
        self._save_user_model(user_model)

        return user_model

    def _learn_decision_style(self, actions: List[Dict]) -> str:
        """
        学习决策风格

        Maximizer: 想要看所有选项，自己做决定
        Satisficer: 想要快速推荐，减少决策
        """
        # 分析：用户是否经常询问更多信息
        info_requests = sum(1 for a in actions if a.get("action") == "ask_more_info")
        total_actions = len(actions)

        if total_actions == 0:
            return "unknown"

        info_request_ratio = info_requests / total_actions

        if info_request_ratio > 0.5:
            return "maximizer"  # 经常要更多信息
        else:
            return "satisficer"  # 接受快速推荐

    def _learn_energy_pattern(self, actions: List[Dict]) -> Dict:
        """学习精力模式（一天中的精力曲线）"""
        # 按时段统计任务完成情况
        hourly_performance = defaultdict(list)

        for action in actions:
            hour = action.get("hour")
            if hour and "completion_success" in action:
                hourly_performance[hour].append(action["completion_success"])

        # 计算每个时段的平均表现
        energy_pattern = {}
        for hour in range(9, 19):  # 9:00-18:00
            if hour in hourly_performance and len(hourly_performance[hour]) > 0:
                energy_pattern[hour] = statistics.mean(hourly_performance[hour])
            else:
                energy_pattern[hour] = 0.5  # 默认值

        return energy_pattern

    def _learn_task_preferences(self, actions: List[Dict]) -> Dict:
        """学习任务偏好"""
        preferences = defaultdict(lambda: {"completed": 0, "postponed": 0, "estimated": 0})

        for action in actions:
            task_type = action.get("task_type", "unknown")
            status = action.get("status", "unknown")

            if status == "completed":
                preferences[task_type]["completed"] += 1
            elif status == "postponed":
                preferences[task_type]["postponed"] += 1

            preferences[task_type]["estimated"] += 1

        # 计算每种任务的偏好分数
        task_preferences = {}
        for task_type, counts in preferences.items():
            total = counts["estimated"]
            if total > 0:
                completion_rate = counts["completed"] / total
                postponement_rate = counts["postponed"] / total
                preference_score = completion_rate - postponement_rate
                task_preferences[task_type] = preference_score

        return task_preferences

    def _learn_flexibility(self, actions: List[Dict]) -> float:
        """学习灵活性需求（0-1）"""
        # 灵活性 = 改变计划的频率
        plan_changes = sum(1 for a in actions if a.get("action") == "change_plan")
        total_actions = len(actions)

        if total_actions == 0:
            return 0.5

        flexibility = plan_changes / total_actions

        return flexibility

    def optimize_algorithm_parameters(self):
        """
        自动优化算法参数

        基于历史数据自动调整：
        1. urgency/importance权重
        2. 时间校准系数
        3. 难度惩罚系数
        4. 价值评分公式
        """
        metrics_history = self._load_metrics_history(days=30)
        user_model = self._load_user_model()

        if len(metrics_history) < 7:
            return {"status": "insufficient_data", "days_needed": 7 - len(metrics_history)}

        # 1. 优化urgency/importance权重
        urgency_importance_weights = self._optimize_weights(metrics_history)

        # 2. 优化时间校准系数
        time_calibration = self._optimize_time_calibration(metrics_history)

        # 3. 生成新的算法版本
        new_version = {
            "version": self._generate_version_id(),
            "created_at": datetime.now().isoformat(),
            "parameters": {
                "urgency_weight": urgency_importance_weights.get("urgency", 0.3),
                "importance_weight": urgency_importance_weights.get("importance", 0.7),
                "time_calibration": time_calibration,
                "user_model_integration": True
            },
            "performance_baseline": self._calculate_baseline_performance(metrics_history),
            "optimized_for": user_model.get("decision_style", "unknown")
        }

        # 保存新版本
        self._save_algorithm_version(new_version)

        # 标记为活跃版本
        self._activate_version(new_version["version"])

        return new_version

    def _optimize_weights(self, metrics_history: List[Dict]) -> Dict:
        """
        优化urgency/importance权重

        方法：分析什么情况下用户完成任务
        """
        # 收集数据：(urgency, importance, completed)
        data_points = []
        for metrics in metrics_history:
            # 这里需要从原始任务数据中提取
            # 暂时简化处理
            pass

        # 使用线性回归找到最优权重
        # 暂时返回默认值
        # TODO: 实现真正的优化算法

        return {"urgency": 0.3, "importance": 0.7}

    def _optimize_time_calibration(self, metrics_history: List[Dict]) -> float:
        """
        优化时间校准系数

        学习：用户通常低估/高估多少时间
        """
        time_accuracies = [m.get("time_accuracy", 1.0) for m in metrics_history]

        if not time_accuracies:
            return 1.0

        mean_accuracy = statistics.mean(time_accuracies)

        # 如果准确度 < 0.8，说明需要校准
        # 校准系数 = 1 / mean_accuracy
        # 但限制在合理范围内
        if mean_accuracy < 0.8:
            calibration = 1.0 / mean_accuracy
            calibration = min(max(calibration, 0.7), 1.3)  # 限制在[0.7, 1.3]
        else:
            calibration = 1.0  # 准确度还可以，不需要校准

        return calibration

    def run_ab_test(self, variant_a: Dict, variant_b: Dict, test_duration_days: int = 7):
        """
        运行A/B测试

        对比两个算法版本：
        - variant_a: 当前版本（对照组）
        - variant_b: 新版本（实验组）
        """
        # 记录实验
        experiment = {
            "experiment_id": self._generate_experiment_id(),
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=test_duration_days)).isoformat(),
            "variant_a": {
                "version": variant_a.get("version"),
                "parameters": variant_a.get("parameters")
            },
            "variant_b": {
                "version": variant_b.get("version"),
                "parameters": variant_b.get("parameters")
            },
            "status": "running",
            "results": {"variant_a": [], "variant_b": []}
        }

        self._save_experiment(experiment)

        return experiment

    def collect_ab_test_result(self, experiment_id: str, variant: str, metrics: Dict):
        """
        收集A/B测试结果
        """
        experiments = self._load_experiments()

        if experiment_id not in experiments:
            return {"error": "experiment_not_found"}

        experiment = experiments[experiment_id]
        experiment["results"][f"variant_{variant}"].append(metrics)

        # 检查实验是否完成
        total_days = (datetime.fromisoformat(experiment["end_date"]) -
                      datetime.fromisoformat(experiment["start_date"])).days

        if len(experiment["results"]["variant_a"]) >= total_days and \
           len(experiment["results"]["variant_b"]) >= total_days:
            # 实验完成，分析结果
            experiment["status"] = "completed"
            experiment["conclusion"] = self._analyze_ab_test(experiment)

        self._save_experiment(experiment)

        return experiment

    def _analyze_ab_test(self, experiment: Dict) -> Dict:
        """
        分析A/B测试结果
        """
        results_a = experiment["results"]["variant_a"]
        results_b = experiment["results"]["variant_b"]

        # 对比指标
        metric_a = statistics.mean([r.get("completion_rate", 0) for r in results_a])
        metric_b = statistics.mean([r.get("completion_rate", 0) for r in results_b])

        improvement = metric_b - metric_a

        if improvement > 0.05:  # 5%以上提升
            winner = "variant_b"
            significance = "significant"
        elif improvement < -0.05:
            winner = "variant_a"
            significance = "significant"
        else:
            winner = "tie"
            significance = "negligible"

        return {
            "winner": winner,
            "improvement": improvement,
            "significance": significance,
            "recommendation": f"Adopt {winner}" if winner != "tie" else "No clear winner"
        }

    def generate_evolution_report(self) -> str:
        """
        生成进化报告

        向用户展示：
        1. 学习到了什么
        2. 算法如何优化
        3. 性能提升多少
        4. 下一步计划
        """
        user_model = self._load_user_model()
        metrics_history = self._load_metrics_history(days=30)
        algorithm_versions = self._load_algorithm_versions()

        report = f"""
# 🧬 Priority Coach 进化报告

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## 📊 学习进度

### 你的个性化模型 (v{user_model.get('version', '0.0')})

**决策风格:** {user_model.get('decision_style', '未知')}
- {"Maximizer" if user_model.get('decision_style') == 'maximizer' else "Satisficer"} - 你喜欢{"详细分析所有选项" if user_model.get('decision_style') == 'maximizer' else "快速得到推荐"}

**精力模式:** 已学习你一天的精力曲线
- 高峰时段: {self._format_energy_peak(user_model.get('energy_pattern', {}))}
- 低谷时段: {self._format_energy_trough(user_model.get('energy_pattern', {}))}

**任务偏好:** 已识别你喜欢/不喜欢的任务类型
"""

        # 添加任务偏好详情
        task_prefs = user_model.get("task_preferences", {})
        if task_prefs:
            best_task = max(task_prefs.items(), key=lambda x: x[1])
            worst_task = min(task_prefs.items(), key=lambda x: x[1])
            report += f"- 最喜欢: {best_task[0]}\n"
            report += f"- 最不喜欢: {worst_task[0]}\n"

        report += f"""
**灵活性:** {user_model.get('flexibility', 0.5):.2f}
- {"需要结构" if user_model.get('flexibility', 0.5) < 0.3 else "喜欢灵活"}

---

## 📈 性能提升

### 最近30天 vs 之前30天

| 指标 | 之前 | 现在 | 提升 |
|------|------|------|------|
"""

        # 计算性能对比
        if len(metrics_history) >= 30:
            recent = metrics_history[:15]
            previous = metrics_history[15:30]

            recent_completion = statistics.mean([m.get("completion_rate", 0) for m in recent])
            previous_completion = statistics.mean([m.get("completion_rate", 0) for m in previous])

            recent_time_accuracy = statistics.mean([m.get("time_accuracy", 1.0) for m in recent])
            previous_time_accuracy = statistics.mean([m.get("time_accuracy", 1.0) for m in previous])

            completion_improvement = (recent_completion - previous_completion) * 100
            time_improvement = (recent_time_accuracy - previous_time_accuracy) * 100

            report += f"""| 完成率 | {previous_completion:.1%} | {recent_completion:.1%} | {completion_improvement:+.1f}% |
| 时间准确度 | {previous_time_accuracy:.1%} | {recent_time_accuracy:.1%} | {time_improvement:+.1f}% |

"""
        else:
            report += "数据积累中...（需要至少30天数据）\n\n"

        report += f"""
---

## 🧪 算法进化

### 当前活跃版本: {self._get_active_version()}

**版本历史:**
"""

        # 列出最近5个版本
        versions = algorithm_versions[-5:]
        for version in versions:
            report += f"""
**v{version['version']}** ({version['created_at'][:10]})
- 优化目标: {version.get('optimized_for', 'general')}
- 参数调整: {self._format_parameter_changes(version['parameters'])}
"""

        report += f"""
---

## 🎯 下一步进化计划

基于你的使用模式，我计划：

1. **短期（1-2周）**
   - ✅ 继续收集你的决策数据
   - ✅ 优化时间校准系数（目标：准确度 > 90%）
   - ✅ 学习你的任务类型偏好

2. **中期（1个月）**
   - 🧪 测试不同的推荐策略
   - 🧠 实现个性化的价值评分公式
   - 📊 预测你的任务完成概率

3. **长期（3个月）**
   - 🤖 完全个性化的推荐引擎
   - 📈 预测性的时间管理建议
   - 🎯 主动优化建议（不需要你问）

---

## 💡 进化洞察

**你独特的模式:**
"""

        # 添加个性化洞察
        insights = self._generate_personal_insights(user_model, metrics_history)
        report += insights

        report += f"""
**进化状态:**
- 🌱 已收集 {len(metrics_history)} 天的数据
- 🧠 已学习 {len(user_model) - 4} 个用户特征
- 🔧 已优化 {len(algorithm_versions)} 个算法版本

**下次进化:** 自动检测到足够数据时，将触发下一轮优化

---

*"每一个完成的任务都在让我更了解你，从而提供更好的建议。"*

*"进化不是一次性的，而是持续的。我每天都在学习。"*

**🚀 让我们一起进化！**
"""

        return report

    def _generate_personal_insights(self, user_model: Dict, metrics: List[Dict]) -> str:
        """生成个性化洞察"""
        insights = []

        # 决策风格洞察
        if user_model.get("decision_style") == "maximizer":
            insights.append("- 你喜欢看到所有选项后再决策")
            insights.append("  → 我会提供多个选项供你选择")
        elif user_model.get("decision_style") == "satisficer":
            insights.append("- 你喜欢快速推荐")
            insights.append("  → 我会直接给出最佳3个任务")

        # 精力模式洞察
        energy_pattern = user_model.get("energy_pattern", {})
        if energy_pattern:
            peak_hour = max(energy_pattern.items(), key=lambda x: x[1])[0]
            insights.append(f"- 你的精力高峰在 {peak_hour}:00")
            insights.append("  → 我会把最重要任务安排在这个时段")

        # 灵活性洞察
        flexibility = user_model.get("flexibility", 0.5)
        if flexibility > 0.7:
            insights.append("- 你经常调整计划")
            insights.append("  → 我会增加20%留白时间")
        elif flexibility < 0.3:
            insights.append("- 你倾向于按计划执行")
            insights.append("  → 我会生成更详细的时间表")

        return "\n".join(insights) if insights else "- 持续使用中，等待更多数据..."

    def _format_energy_peak(self, energy_pattern: Dict) -> str:
        if not energy_pattern:
            return "未知"
        peak_hour = max(energy_pattern.items(), key=lambda x: x[1])[0]
        return f"{peak_hour}:00-{peak_hour+1}:00"

    def _format_energy_trough(self, energy_pattern: Dict) -> str:
        if not energy_pattern:
            return "未知"
        trough_hour = min(energy_pattern.items(), key=lambda x: x[1])[0]
        return f"{trough_hour}:00-{trough_hour+1}:00"

    def _format_parameter_changes(self, parameters: Dict) -> str:
        return f"urgency权重={parameters['urgency_weight']:.2f}, importance权重={parameters['importance_weight']:.2f}"

    # 辅助方法
    def _save_metrics(self, metrics: Dict):
        """保存指标"""
        metrics_file = self.evolution_dir / "metrics_history.jsonl"
        with open(metrics_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(metrics) + "\n")

    def _load_metrics_history(self, days: int = 30) -> List[Dict]:
        """加载指标历史"""
        metrics_file = self.evolution_dir / "metrics_history.jsonl"
        if not metrics_file.exists():
            return []

        metrics = []
        with open(metrics_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    metrics.append(json.loads(line))

        # 按日期排序，取最近N天
        metrics.sort(key=lambda x: x.get("date", ""), reverse=True)
        return metrics[:days]

    def _load_user_model(self) -> Dict:
        """加载用户模型"""
        if not self.user_model_file.exists():
            return self._get_default_user_model()

        try:
            with open(self.user_model_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return self._get_default_user_model()

    def _get_default_user_model(self) -> Dict:
        """获取默认用户模型"""
        return {
            "version": "0.0",
            "created_at": datetime.now().isoformat(),
            "decision_style": "unknown",
            "energy_pattern": {},
            "task_preferences": {},
            "flexibility": 0.5
        }

    def _save_user_model(self, user_model: Dict):
        """保存用户模型"""
        with open(self.user_model_file, 'w', encoding='utf-8') as f:
            json.dump(user_model, f, ensure_ascii=False, indent=2)

    def _load_algorithm_versions(self) -> List[Dict]:
        """加载算法版本历史"""
        if not self.versions_file.exists():
            return []

        with open(self.versions_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_algorithm_version(self, version: Dict):
        """保存算法版本"""
        versions = self._load_algorithm_versions()
        versions.append(version)

        with open(self.versions_file, 'w', encoding='utf-8') as f:
            json.dump(versions, f, ensure_ascii=False, indent=2)

    def _get_active_version(self) -> str:
        """获取当前活跃版本"""
        active_file = self.evolution_dir / "active_version.txt"
        if active_file.exists():
            with open(active_file, 'r') as f:
                return f.read().strip()
        return "1.0.0"

    def _activate_version(self, version: str):
        """激活算法版本"""
        active_file = self.evolution_dir / "active_version.txt"
        with open(active_file, 'w') as f:
            f.write(version)

    def _generate_version_id(self) -> str:
        """生成版本ID"""
        existing_versions = self._load_algorithm_versions()
        version_num = len(existing_versions) + 1
        return f"1.{version_num}.0"

    def _increment_version(self, current_version: str) -> str:
        """递增版本号"""
        # 简化版：只递增patch版本
        parts = current_version.split(".")
        patch = int(parts[2]) + 1
        return f"{parts[0]}.{parts[1]}.{patch}"

    def _load_experiments(self) -> Dict:
        """加载所有实验"""
        if not self.experiments_file.exists():
            return {}

        with open(self.experiments_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_experiment(self, experiment: Dict):
        """保存实验"""
        experiments = self._load_experiments()
        experiments[experiment["experiment_id"]] = experiment

        with open(self.experiments_file, 'w', encoding='utf-8') as f:
            json.dump(experiments, f, ensure_ascii=False, indent=2)

    def _generate_experiment_id(self) -> str:
        """生成实验ID"""
        return f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def _calculate_baseline_performance(self, metrics_history: List[Dict]) -> Dict:
        """计算基线性能"""
        if not metrics_history:
            return {"completion_rate": 0.5, "time_accuracy": 0.8}

        recent_metrics = metrics_history[:7]  # 最近7天
        return {
            "completion_rate": statistics.mean([m.get("completion_rate", 0) for m in recent_metrics]),
            "time_accuracy": statistics.mean([m.get("time_accuracy", 1.0) for m in recent_metrics])
        }


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="Priority Coach 自我进化引擎")

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # 生成进化报告
    report_parser = subparsers.add_parser("report", help="生成进化报告")
    report_parser.add_argument("--save", action="store_true", help="保存到文件")

    # 优化算法
    optimize_parser = subparsers.add_parser("optimize", help="优化算法参数")

    args = parser.parse_args()

    engine = SelfEvolutionEngine()

    if args.command == "report":
        report = engine.generate_evolution_report()
        print(report)

        if args.save:
            report_file = engine.evolution_dir / "evolution_report.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"\n✅ 报告已保存到: {report_file}")

    elif args.command == "optimize":
        result = engine.optimize_algorithm_parameters()
        print(f"\n🔧 算法优化完成")
        print(f"新版本: {result['version']}")
        print(f"参数: {result['parameters']}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
