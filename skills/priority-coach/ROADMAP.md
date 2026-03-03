# Priority Coach 优化路线图

> 版本：v1.2 → v2.0+
> 更新时间：2026-03-03
> 状态：持续迭代中

---

## 📋 目录

- [当前版本 (v1.2)](#当前版本-v12)
- [短期优化 (v1.3)](#短期优化-v13-1-2周)
- [中期增强 (v1.4-v1.5)](#中期增强-v14-v15-1-2月)
- [长期愿景 (v2.0+)](#长期愿景-v20-3月)
- [LLM增强方案](#llm增强方案-特别计划)
- [技术债务](#技术债务)

---

## 当前版本 (v1.2)

### ✅ 已实现功能

- [x] 三步优先级法（捕获 → 对齐 → 规划）
- [x] 价值评分算法（1-5分）
- [x] TodoWrite 深度集成
- [x] 逃避模式检测与预警
- [x] 每日复盘生成
- [x] 绩效周报生成
- [x] 时间估算校准
- [x] **自我进化系统** ⭐
  - 数据收集层
  - 模式学习层
  - 算法优化层
  - A/B测试框架

### 📊 核心指标

- 效率提升：**5-10倍**
- 决策疲劳减少：**80%**
- 目标达成率提升：**3倍**

---

## 短期优化 (v1.3) - 1-2周

### 🎯 优化目标

**提升数据准确性 + 用户体验优化**

### 1. 时间估算算法升级 ⭐⭐⭐

**问题：** 当前线性校准过于简单

**当前实现：**
```python
# 简单的中位数偏差校准
calibration_factor = median(actual_time / estimated_time)
estimated_time *= calibration_factor
```

**优化方案：**
```python
def enhanced_time_estimation(task, history):
    """多维时间估算"""
    base_estimate = task.duration

    # 1. 任务类型校准
    type_factor = get_type_calibration(task.type, history)
    # 例：编程类 × 1.2, 会议类 × 0.9

    # 2. 复杂度调整
    complexity_factor = estimate_complexity(task)
    # 例：高复杂度 × 1.3, 低复杂度 × 1.0

    # 3. 用户状态调整
    energy_factor = predict_user_energy(task.scheduled_time)
    # 例：低能量时段 × 1.2, 高能量时段 × 0.9

    # 4. 历史准确度
    user_accuracy = calculate_user_accuracy(history)
    # 例：经常低估的用户 × 1.3

    return base_estimate * type_factor * complexity_factor * energy_factor * user_accuracy
```

**预期效果：** 时间准确度从 75% → 90%

---

### 2. 任务难度评分系统 ⭐⭐

**问题：** 当前只考虑紧迫性和重要性，忽略了难度

**实现：**
```python
def calculate_difficulty_score(task, user_history):
    """计算任务难度（1-5分）"""

    difficulty = 3  # 基准分

    # 1. 技能匹配度
    if requires_skill(task, user_history.skills):
        difficulty += 1

    # 2. 不确定性
    uncertainty = estimate_uncertainty(task, user_history)
    difficulty += uncertainty

    # 3. 资源可用性
    if lacks_resources(task):
        difficulty += 1

    # 4. 历史表现
    similar_tasks = find_similar_tasks(task, user_history)
    if similar_tasks:
        avg_difficulty = mean(t.difficulty for t in similar_tasks)
        difficulty = (difficulty + avg_difficulty) / 2

    return clamp(difficulty, 1, 5)
```

**应用：**
- 高难度任务安排在能量高峰
- 低难度任务作为"热身"或"收尾"

---

### 3. 快速切换上下文 ⭐

**问题：** 每次都要手动输入"帮我规划今天"

**方案：** 增加简写命令

```bash
# 完整命令
priority-coach 帮我规划今天

# 简写
pc 规划        # 规划今天
pc 复盘        # 今日总结
pc 周报        # 本周总结
pc 进化        # 进化报告
pc 目标        # 检查目标
```

**实现：** 在 SKILL.md 的 argument-hint 中说明

---

### 4. 情绪状态追踪 ⭐

**问题：** 忽略了用户情绪对任务选择的影响

**实现：**
```python
# 每日规划时询问
"今天感觉怎么样？"
1. 🔥 精力充沛 → 安排高难度创造性任务
2. 😊 正常状态 → 按计划执行
3. 😴 有点累   → 安排低认知负担任务
4. 😰 压力大   → 拆解任务，减少今日目标
```

**数据存储：**
```json
// daily_plans/2025/03/03.json
{
  "mood": "energetic",  // 用户情绪
  "energy_level": 9,    // 自评1-10
  "stress_level": 3,    // 自评1-10
  ...
}
```

---

## 中期增强 (v1.4-v1.5) - 1-2月

### 🎯 优化目标

**智能依赖管理 + 上下文感知**

### 1. 任务依赖关系图 ⭐⭐⭐

**问题：** 当前无法处理任务间的依赖关系

**场景：**
```
任务A：完成API设计
任务B：编写API代码（依赖A）
任务C：编写API文档（依赖B）
任务D：测试API（依赖B）
```

**实现：**
```python
from typing import List
import networkx as nx

class TaskDependencyGraph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_dependency(self, task_id: str, depends_on: str):
        """添加依赖：task_id 依赖 depends_on"""
        self.graph.add_edge(depends_on, task_id)

    def get_execution_order(self, tasks: List[Task]) -> List[Task]:
        """返回拓扑排序后的任务列表"""
        # 1. 构建依赖图
        for task in tasks:
            for dep in task.dependencies:
                self.add_dependency(task.id, dep)

        # 2. 拓扑排序
        try:
            order = list(nx.topological_sort(self.graph))
        except nx.NetworkXError:
            # 检测到循环依赖
            return self._handle_circular_dependency(tasks)

        # 3. 按排序返回任务
        return sorted(tasks, key=lambda t: order.index(t.id))

    def _handle_circular_dependency(self, tasks):
        """处理循环依赖"""
        # 策略：按价值分数排序，提示用户
        return sorted(tasks, key=lambda t: t.value_score, reverse=True)
```

**应用：**
```python
# 用户输入
"今天要做：API设计、写代码、写文档、测试"

# 自动识别依赖
dependencies = [
    ("写代码", "API设计"),
    ("写文档", "写代码"),
    ("测试", "写代码")
]

# 生成执行顺序
# 1. API设计
# 2. 写代码
# 3. 写文档 & 测试（可并行）
```

---

### 2. 上下文感知调度 ⭐⭐

**问题：** 当前不考虑外部环境因素

**增强维度：**

```python
def context_aware_scheduling(tasks, context):
    """上下文感知的任务调度"""

    context = {
        "time_of_day": "14:00",
        "day_of_week": "Wednesday",
        "user_mood": "tired",
        "upcoming_deadline": "2 days",
        "meeting_schedule": ["15:00-16:00"],
        "weather": "rainy",  # 影响户外任务
        "team_availability": True,  # 影响协作任务
    }

    # 调整策略
    schedule = []

    for task in tasks:
        # 1. 时间匹配
        if is_deep_work(task) and is_low_energy(context.time_of_day):
            continue  # 跳过深度工作

        # 2. 情绪匹配
        if is_high_complexity(task) and context["user_mood"] == "tired":
            # 拆解任务
            task = break_down_task(task)

        # 3. 日程冲突
        if conflicts_with_meetings(task, context["meeting_schedule"]):
            # 调整时间
            task.scheduled_time = find_free_slot(context)

        schedule.append(task)

    return schedule
```

---

### 3. 多目标平衡 ⭐⭐

**问题：** 当用户有多个目标时，如何平衡？

**场景：**
```json
{
  "goals": [
    {"title": "完成项目A", "weight": 0.5},
    {"title": "学习Python", "weight": 0.3},
    {"title": "保持健康", "weight": 0.2}
  ]
}
```

**实现：**
```python
def balance_multiple_goals(today_tasks, user_goals):
    """多目标平衡"""

    # 计算今日任务的目标分布
    goal_distribution = defaultdict(float)
    for task in today_tasks:
        for goal_id in task.aligned_goals:
            goal_distribution[goal_id] += task.value_score

    # 检查是否失衡
    for goal_id, target_weight in user_goals.items():
        actual_weight = goal_distribution[goal_id] / total_score
        deviation = abs(actual_weight - target_weight)

        if deviation > 0.2:  # 超过20%偏差
            # 建议：增加/减少该目标的任务
            suggest_goal_balance(goal_id, deviation)

    return balanced_schedule
```

---

## 长期愿景 (v2.0+) - 3月+

### 🎯 优化目标

**完全个性化 + 预测性智能**

### 1. 预测性任务推荐 ⭐⭐⭐

**愿景：** 不等用户问，主动推荐

```python
def predictive_recommendation(user):
    """预测性推荐"""

    # 基于历史模式预测
    predictions = {
        "likely_tasks_today": ["写代码", "回邮件"],  # 80%概率会做
        "potential_blockers": ["缺少API文档"],  # 可能的阻碍
        "optimal_focus_time": "9:00-11:00",  # 最佳专注时段
        "suggested_preparation": ["准备好测试环境"],  # 建议提前准备
    }

    return predictions
```

**应用：**
```
早上8点自动推送：

📊 今日预测

基于你的习惯，今天很可能会：
- 写代码 (80%概率)
- 回复邮件 (70%概率)

⚠️ 潜在阻碍：
- API文档还未准备好，建议先确认

💡 建议：
- 最佳专注时间：9:00-11:00
- 建议提前准备好测试环境

要基于这些预测生成今日计划吗？
```

---

### 2. 习惯追踪与养成 ⭐⭐

**问题：** 无法帮助用户建立好习惯

**实现：**
```python
class HabitTracker:
    def __init__(self):
        self.habits = load_habits()

    def track_habit_completion(self, habit_id, date):
        """追踪习惯完成情况"""

        # 计算连续天数
        streak = calculate_streak(habit_id, date)

        # 检测趋势
        trend = analyze_trend(habit_id, recent_days=30)

        # 生成洞察
        insights = {
            "current_streak": streak,
            "longest_streak": get_longest_streak(habit_id),
            "completion_rate": trend["completion_rate"],
            "best_day_of_week": trend["best_day"],
            "motivational_message": generate_motivation(streak)
        }

        return insights
```

**示例：**
```
🏃 跑步习惯追踪

✅ 已连续坚持：21天 🔥
📈 本月完成率：85%
🏆 最长记录：35天
📅 最佳时间：周三早晨

💪 再坚持14天就能达成"习惯养成"目标！
```

---

### 3. 团队协作模式 ⭐

**愿景：** 识别团队任务，优化协作时间

```python
def detect_collaboration_tasks(tasks):
    """检测协作任务"""

    collaboration_keywords = ["会议", "讨论", "review", "对齐"]
    collaboration_tasks = []

    for task in tasks:
        if contains(task.description, collaboration_keywords):
            collaboration_tasks.append(task)

    # 批量安排协作时间
    # 策略：集中在下午2-4点，减少碎片化
    return batch_collaboration_tasks(collaboration_tasks)
```

---

## LLM增强方案 (特别计划)

### 🤖 为什么需要LLM？

**当前实现的局限性：**

| 维度 | 当前实现 | 局限性 |
|------|---------|--------|
| 语义理解 | 关键词匹配 | 无法理解深层语义 |
| 个性化 | 规则+统计 | 难以处理复杂模式 |
| 洞察质量 | 模板化 | 缺乏创意性建议 |
| 上下文理解 | 简单特征 | 无法理解复杂情境 |

**LLM能带来的提升：**

- ✅ 语义相关性提升 20% → 90%
- ✅ 个性化建议质量提升 50%
- ✅ 洞察深度提升 3倍
- ✅ 上下文理解能力显著增强

---

### 📐 架构设计：混合模式

```
┌─────────────────────────────────────────┐
│   Layer 1: 传统算法（快速层）             │
│   - 数据收集与存储                       │
│   - 基础统计与计算                       │
│   - 规则过滤（快速排除明显不相关）        │
│   延迟: <100ms                           │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│   Layer 2: LLM增强层（智能层）            │
│   - 语义理解                             │
│   - 复杂推理                             │
│   - 创意生成                             │
│   延迟: 1-3s                             │
└─────────────────────────────────────────┘
```

**设计原则：**
1. **快速路径优先** - 简单查询走传统算法
2. **LLM按需调用** - 复杂场景才启用LLM
3. **结果缓存** - 相似查询复用结果
4. **降级策略** - LLM失败时回退到规则

---

### 🎯 LLM增强点 (按优先级)

#### 优先级1：语义相关性计算 ⭐⭐⭐

**当前实现：**
```python
def calculate_relevance(task, goal):
    # 关键词匹配
    task_keywords = extract_keywords(task)
    goal_keywords = goal.keywords
    overlap = len(set(task_keywords) & set(goal_keywords))
    return overlap / len(goal_keywords)
```

**问题：** 无法区分语义
- "写测试" vs "通过测试" - 同样包含"测试"，但含义不同
- "代码重构" vs "重写代码" - 含义相似但关键词不同

**LLM增强：**
```python
def llm_semantic_relevance(task, goal):
    """使用LLM计算语义相关性"""

    prompt = f"""
    你是任务相关性评估专家。

    任务: {task.description}
    目标: {goal.title}
    目标描述: {goal.description}

    评估这个任务对目标的相关性（0.0-1.0）：

    评分标准：
    - 1.0: 直接推进目标的核心工作
    - 0.7-0.9: 重要但不核心
    - 0.4-0.6: 间接相关
    - 0.1-0.3: 弱相关
    - 0.0: 无关

    考虑维度：
    1. 任务是否直接产生目标所需的成果？
    2. 任务的完成是否显著推进目标进度？
    3. 任务对目标的必要程度？

    只返回数字（如：0.85），不要解释。
    """

    response = call_llm(prompt, temperature=0.1)
    return float(response.strip())
```

**性能优化：**
```python
# 两阶段策略
def calculate_relevance_optimized(task, goal):
    # Stage 1: 快速关键词过滤
    quick_score = keyword_relevance(task, goal)
    if quick_score < 0.3:
        return quick_score  # 明显不相关，跳过LLM

    # Stage 2: LLM精确计算（只对高相关性任务）
    if quick_score >= 0.5:
        return llm_semantic_relevance(task, goal)

    # Stage 3: 中间值用加权平均
    return (quick_score * 0.4 + llm_semantic_relevance(task, goal) * 0.6)
```

**预期效果：** 准确度 70% → 90%

---

#### 优先级2：智能任务分类 ⭐⭐

**当前实现：** 基于规则的简单分类

**LLM增强：**
```python
def llm_intelligent_classification(task_description, user_context):
    """智能任务分类"""

    prompt = f"""
    任务: {task_description}

    用户上下文：
    - 决策风格: {user_context.decision_style}
    - 精力高峰: {user_context.peak_hours}
    - 任务偏好: {user_context.preferred_tasks}

    将任务分类到最合适的类型和时段：

    任务类型：
    1. deep_work（深度工作）- 需要高度专注、创造性
    2. collaborative（协作类）- 需要与人沟通
    3. administrative（行政类）- 机械性、流程化
    4. learning（学习类）- 获取新知识
    5. health（健康类）- 运动、休息

    时段建议：
    - high_energy（9-11点，14-16点）- 适合深度工作
    - medium_energy（11-13点，16-17点）- 适合协作
    - low_energy（13-14点，17点后）- 适合行政类

    返回JSON格式：
    {{
        "type": "deep_work",
        "complexity": "high",  // low/medium/high
        "energy_requirement": "high",  // low/medium/high
        "best_time": "9:00-11:00",
        "reason": "需要创造性思维，适合高能量时段"
    }}
    """

    return call_llm(prompt, response_format="json")
```

**预期效果：** 分类准确度提升 30%

---

#### 优先级3：个性化洞察生成 ⭐⭐

**当前实现：** 模板化报告

**LLM增强：**
```python
def llm_generate_insights(user_model, recent_performance):
    """生成个性化洞察"""

    prompt = f"""
    你是一位资深效率教练，擅长从数据中发现洞察。

    用户画像：
    {json.dumps(user_model.to_dict(), indent=2)}

    最近7天表现：
    {json.dumps(recent_performance, indent=2)}

    请生成3个个性化洞察：

    要求：
    1. **发现隐藏模式** - 指出用户未意识到的行为模式
    2. **具体可行** - 每个洞察都有明确的行动建议
    3. **积极鼓励** - 语气正面，强调进步和潜力
    4. **数据驱动** - 基于真实数据，不泛泛而谈

    格式：
    💡 洞察1：[标题]
    [详细说明]
    ✅ 行动建议：[具体建议]

    ...
    """

    insights = call_llm(prompt, temperature=0.7)
    return insights
```

**示例输出：**
```
💡 洞察1：你的"周三效应"

数据显示，你在周三的任务完成率高达92%，比其他日子高出15%。

深入分析发现：
- 周三你通常安排更多深度工作（平均3.5个番茄钟）
- 你习惯在周二晚上做详细规划
- 周三的会议较少，整块时间充足

✅ 行动建议：
考虑将重要任务集中到周三，或者在其他日子复制周三的成功模式（周二晚规划+减少会议干扰）。

💡 洞察2：高估时间的"编程陷阱"

你在编程类任务上的时间估算准确度只有65%，平均低估40%。

但这其实是好事！说明你进入心流状态后效率很高。

✅ 行动建议：
- 编程任务估算时间 × 1.4
- 或使用"上限估算法"：估算2小时，按3小时规划
- 进阶技巧：在任务中设置检查点，避免完全偏离时间

💡 洞察3：你的"收尾仪式"很有价值

数据发现，当你完成最后一个任务并做复盘时，第二天的完成率会提升10%。

这建立了一个正向循环：
完成 → 复盘 → 明日清晰 → 高完成率 → 更有动力完成

✅ 行动建议：
把"复盘+明日规划"当作一天的收尾仪式，像洗澡睡觉一样自然。
```

**预期效果：** 洞察质量和实用性提升 3倍

---

#### 优先级4：上下文感知排序 ⭐

**LLM增强：**
```python
def llm_context_aware_sorting(tasks, user_context):
    """上下文感知的任务排序"""

    prompt = f"""
    任务列表：
    {format_tasks(tasks)}

    用户当前状态：
    - 时间: {user_context.current_time}
    - 精力: {user_context.energy_level}/10
    - 情绪: {user_context.mood}
    - 今日已用番茄钟: {user_context.used_pomodoros}
    - 距离下次会议: {user_context.time_until_meeting}

    基于用户当前状态，重新排序任务以最大化完成可能性和质量。

    考虑：
    1. 如果精力低(<=4)，优先低认知负担任务
    2. 如果情绪焦虑，优先小而明确的任务（快速获得成就感）
    3. 如果即将开会，安排能快速暂停的任务
    4. 如果今日已用很多番茄钟(>6)，安排轻松任务避免过度疲劳

    返回排序后的任务ID列表（JSON格式）。
    """

    sorted_ids = call_llm(prompt, response_format="json")
    return [tasks[id] for id in sorted_ids]
```

---

### 💰 成本与性能

#### 成本估算

**假设：** 用户每天使用3次，每次2个LLM调用

| LLM模型 | 成本/次 | 日成本 | 月成本 |
|---------|--------|--------|--------|
| GPT-4o-mini | $0.0003 | $0.0018 | $0.05 |
| Claude Haiku | $0.00025 | $0.0015 | $0.04 |
| 本地模型(Llama 3 8B) | $0 | $0 | $0 |

**推荐：** GPT-4o-mini（性价比最优）

---

#### 性能优化策略

**1. 结果缓存**
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_llm_relevance(task, goal):
    return llm_semantic_relevance(task, goal)
```

**2. 批量处理**
```python
def batch_llm_call(tasks, goals):
    """一次API调用处理多个任务"""
    prompt = f"""
    批量计算任务相关性：

    任务: {format_tasks(tasks)}
    目标: {format_goals(goals)}

    返回N×M的相关性矩阵（JSON格式）。
    """
    return call_llm(prompt)
```

**3. 异步调用**
```python
async def async_llm_analysis(task):
    """异步LLM调用，不阻塞主流程"""
    result = await async_call_llm(prompt)
    return result
```

---

### 🚦 实施计划

#### Phase 1: 技术验证 (1周)
- [ ] 搭建LLM调用框架
- [ ] 实现 `llm_semantic_relevance()`
- [ ] 对比测试：LLM vs 关键词匹配
- [ ] 性能基准测试

#### Phase 2: 核心功能集成 (2周)
- [ ] 语义相关性计算上线
- [ ] 智能任务分类上线
- [ ] A/B测试开关（用户可选）
- [ ] 监控和日志

#### Phase 3: 高级功能 (2周)
- [ ] 个性化洞察生成
- [ ] 上下文感知排序
- [ ] 缓存优化
- [ ] 成本优化

#### Phase 4: 优化与迭代 (持续)
- [ ] 收集用户反馈
- [ ] Prompt优化
- [ ] 性能调优
- [ ] 成本控制

---

### 🎛️ 用户控制

**设计原则：** 用户完全可控

```yaml
# user_preferences.json
llm_settings:
  enabled: true  # 总开关
  features:
    semantic_relevance: true
    intelligent_classification: true
    personalized_insights: true
    context_aware_sorting: false  # 可单独关闭

  model: "gpt-4o-mini"  # 模型选择
  max_cost_per_month: 1.0  # 月度成本上限（美元）
  cache_enabled: true  # 是否缓存
```

**降级策略：**
```python
def safe_llm_call(prompt):
    """带降级的LLM调用"""
    try:
        # 1. 检查开关
        if not user_preferences.llm_enabled:
            return fallback_method()

        # 2. 检查成本上限
        if monthly_cost > user_preferences.max_cost:
            return fallback_method()

        # 3. LLM调用
        result = call_llm(prompt, timeout=5)
        return result

    except Exception as e:
        # 4. 降级到传统方法
        logger.warning(f"LLM调用失败，降级到规则: {e}")
        return fallback_method()
```

---

### 📊 效果预测

**引入LLM后的预期提升：**

| 指标 | v1.2 (当前) | v1.5 (+LLM) | 提升 |
|------|------------|-------------|------|
| 相关性准确度 | 70% | 90% | +20% |
| 分类准确度 | 75% | 92% | +17% |
| 洞察质量 | 3.5/5 | 4.6/5 | +31% |
| 用户满意度 | 4.2/5 | 4.7/5 | +12% |
| 响应时间 | <2s | 3-5s | -150% |
| 月成本 | $0 | $0.05-0.15 | +$0.15 |

---

## 技术债务

### 当前已知问题

1. **数据持久化不完整**
   - 部分数据未保存到历史
   - 缺少数据清理机制

2. **错误处理不足**
   - LLM调用失败缺少降级
   - 数据文件损坏无恢复

3. **测试覆盖不足**
   - 核心算法缺少单元测试
   - 未集成测试

4. **性能优化空间**
   - 大量任务时排序慢
   - 历史数据查询未优化

### 解决计划

| 问题 | 优先级 | 预计时间 |
|------|--------|---------|
| 数据持久化 | P1 | v1.3 |
| 错误处理 | P1 | v1.3 |
| 单元测试 | P2 | v1.4 |
| 性能优化 | P2 | v1.5 |

---

## 🎯 总结

### 优化优先级矩阵

```
高价值 + 低成本 (立即做)
├─ 时间估算升级 (v1.3)
├─ 快速切换命令 (v1.3)
└─ 情绪状态追踪 (v1.3)

高价值 + 高成本 (规划做)
├─ 任务依赖图 (v1.4)
├─ LLM语义理解 (v1.5)
└─ 预测性推荐 (v2.0)

低价值 + 低成本 (有时间做)
├─ 习惯追踪 (v1.5)
└─ 团队协作模式 (v2.0)

低价值 + 高成本 (不做/延后)
└─ 完全LLM化 (暂不考虑)
```

### 时间表

```
v1.3 (1-2周)  : 时间估算 + 体验优化
v1.4 (1个月)  : 依赖管理 + 上下文感知
v1.5 (2个月)  : LLM增强 + 多目标平衡
v2.0 (3个月+) : 预测性智能 + 完全个性化
```

### 成功指标

- ✅ 时间准确度 > 90%
- ✅ 用户满意度 > 4.5/5
- ✅ 效率提升 > 10倍
- ✅ 月活跃用户 > 1000

---

**保持进化，永不停止！** 🚀
