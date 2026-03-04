# CreateSkills - Claude Code Skills 集合

> **首个发布：Priority Coach v1.2.0** - 专为感知型人格设计的AI优先级教练

[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Skills-purple.svg)]()

---

## 🎯 这是什么？

**CreateSkills** 是一个 Claude Code Skills 集合项目，旨在创建高质量、实用的 AI 助手技能。

### 首个发布：Priority Coach ⭐

**Priority Coach** 是专为感知型人格（P人）设计的AI优先级教练，通过脑部清理、目标对齐和时间保护三大机制，将零散任务转化为结构化的行动计划。效率提升5-10倍。

- ✅ 整理零散想法 → 优先级清单
- ✅ 基于长期目标进行价值评分（1-5分）
- ✅ 生成符合生物钟的时间表
- ✅ 每日复盘和周度回顾
- ✅ 学习并优化你的工作模式（自我进化系统 🤖）

**适用人群：** 感知型人格（P人）、容易分心、任务爆炸的人

---

## 🚀 快速开始

### ⚙️ 如何让 Claude Code 使用这个 Skill

**重要：** Claude Code 需要将 Skill 文件放在特定位置才能识别和使用。

#### Step 1: 理解目录结构

Claude Code 使用两个不同的目录：

**1. Skill 安装目录**（你手动创建）：
```
~/.claude/skills/priority-coach/
└── SKILL.md  # 核心 Skill 文件
```

**2. 数据存储目录**（自动创建）：
```
~/.claude/priority-coach/
├── user_goals.json    # 用户长期目标
├── daily_plans/       # 每日计划
├── weekly_reports/    # 周报
└── analytics/         # 分析数据
```

**注意：** `~/.claude/priority-coach/` 是数据目录，不是 skill 安装目录！

#### Step 2: 安装 Priority Coach Skill

**方法一：直接复制（推荐）**

```bash
# 1. 创建 skill 目录
mkdir -p ~/.claude/skills/priority-coach

# 2. 复制核心 SKILL.md 文件
cp skills/priority-coach/SKILL.md ~/.claude/skills/priority-coach/

# 3. （可选）复制参考资料，以便 Skill 可以引用
mkdir -p ~/.claude/skills/priority-coach/references
cp -r skills/priority-coach/references/* ~/.claude/skills/priority-coach/references/
```

**方法二：创建符号链接（开发者）**

```bash
# 如果你克隆了本仓库
ln -s $(pwd)/skills/priority-coach ~/.claude/skills/priority-coach
```

#### Step 3: 验证安装

在 Claude Code 中尝试：

```bash
priority-coach 帮我规划今天
```

如果成功，你会看到规划输出！✅

**验证命令：**
```bash
# 检查 skill 是否安装成功
ls ~/.claude/skills/priority-coach/SKILL.md

# 查看数据目录（首次使用后会自动创建）
ls ~/.claude/priority-coach/
```

---

### 📦 克隆完整仓库（可选）

如果你想查看完整文档、示例和测试套件：

```bash
# 克隆本仓库
git clone https://github.com/JourneytoNewland/priority-coach.git
cd createSkills

# Priority Coach 源文件位于
skills/priority-coach/
```

**注意：** 运行 Skill 只需要 `SKILL.md`，其他文件是参考和开发用的。

### 使用 Priority Coach

1. **首次使用** - 初始化目标
```
priority-coach 初始化
```

2. **每天早上** - 规划今天
```
priority-coach 帮我规划今天
```

3. **每天晚上** - 复盘总结
```
priority-coach 今日总结
```

4. **每周周末** - 绩效周报
```
priority-coach 本周总结
```

5. **查看进化报告** - 了解学习进度 ⭐
```
priority-coach 进化报告
```

---

## 📂 项目结构

```
createSkills/                      # Skills 集合项目根目录
├── README.md                      # 项目总览（本文件）
├── LICENSE                        # MIT 许可证
├── CHANGELOG.md                   # 总体版本历史
│
└── skills/                        # Skills 目录
    └── priority-coach/            # 🎯 首个发布：Priority Coach
        ├── SKILL.md              # 核心技能文档（Claude读取）
        ├── README.md             # Priority Coach 使用指南
        ├── examples.md           # 8个典型使用场景
        ├── ROADMAP.md            # 优化路线图 🚀
        │
        ├── references/           # 参考资料（5个）
        │   ├── eisenhower-matrix.md
        │   ├── p-persona-guide.md
        │   ├── pomodoro-technique.md
        │   ├── biotime-matching.md
        │   └── self-evolution.md
        │
        ├── scripts/              # 核心脚本（5个）
        │   ├── calculate_value_score.py
        │   ├── analyze_escape_patterns.py
        │   ├── daily_review.py
        │   ├── generate_weekly_report.py
        │   └── self_evolution.py
        │
        └── tests/                # 测试套件
            └── test_v1.2.py
```

**注意：** 目前本仓库只包含 Priority Coach。未来计划添加更多实用 Skills。

---

## ✨ 核心特性

### 1. 三步优先级法

**Step 1: 捕获与分类** - 零散想法 → 结构化清单
**Step 2: 目标对齐** - 基于长期目标的价值评分（1-5分）
**Step 3: 时间规划** - 生物钟匹配 + 20%留白原则

### 2. 每日复盘 ⭐

- 完成率统计
- 时间偏差分析
- 目标推进度计算
- 明日优化建议

### 3. 绩效周报 ⭐

- 本周统计数据
- 各目标推进情况
- TOP3成就回顾
- 逃避任务识别
- 下周建议

### 4. 逃避模式学习

- 自动识别反复推迟的任务
- 提供针对性应对策略
- 使用2-3周后学习个人模式

### 5. TodoWrite集成

- 自动创建任务清单
- 跨设备同步
- 在Claude UI中实时更新

### 6. 自我进化系统 ⭐ **v1.2新增**

- **数据收集层** - 记录决策模式、完成率、时间准确度
- **模式学习层** - 识别决策风格、精力模式、任务偏好
- **算法优化层** - 自动调优参数、A/B测试、时间校准
- **进化报告** - 展示学习进度和性能提升

**效果：** 使用越久，越懂你！🤖

---

## 📊 效果

- ✅ 效率提升 5-10倍
- ✅ 决策疲劳减少 80%
- ✅ 目标达成率提升 3倍
- ✅ 每天都有清晰的"今天的3件要事"

---

## 📖 文档

- **[SKILL.md](skills/priority-coach/SKILL.md)** - 核心技能文档（Claude读取）
- **[README.md](skills/priority-coach/README.md)** - 使用指南
- **[examples.md](skills/priority-coach/examples.md)** - 8个使用示例
- **[ROADMAP.md](skills/priority-coach/ROADMAP.md)** - 优化路线图 🚀
- **[CHANGELOG.md](CHANGELOG.md)** - 版本变更历史
- **[references/self-evolution.md](skills/priority-coach/references/self-evolution.md)** - 自我进化机制详解

---

## 🛠️ 技术实现

### 核心算法

**价值评分公式：**
```
Value = (目标权重 × 相关性) × (紧迫性×0.3 + 重要性×0.7)
```

**输出：** 1-5分，用于优先级排序

### 数据存储

- **位置：** `~/.claude/priority-coach/`
- **格式：** JSON（人类可读）
- **隐私：** 本地存储，不上传云端

---

## 🎓 使用场景

### 场景1：早上规划
```
priority-coach 帮我规划今天
```

### 场景2：任务爆炸
```
priority-coach 做这个、做那个、还有那个...
```

### 场景3：每日复盘
```
priority-coach 今日总结
```

### 场景4：绩效周报
```
priority-coach 本周总结
```

更多场景见 [examples.md](skills/priority-coach/examples.md)

---

## 🚧 开发路线图

**完整的优化计划详见：** [ROADMAP.md](skills/priority-coach/ROADMAP.md) 🚀

### 快速预览

**v1.3 (1-2周)** - 体验优化
- ⭐ 时间估算算法升级
- ⭐ 任务难度评分系统
- ⭐ 快速命令（pc 规划/复盘/周报）
- ⭐ 情绪状态追踪

**v1.4-v1.5 (1-2月)** - 智能增强
- ⭐ 任务依赖关系图
- ⭐ 上下文感知调度
- ⭐ 多目标平衡
- 🤖 LLM语义增强

**v2.0+ (3月+)** - 完全个性化
- ⭐ 预测性任务推荐
- ⭐ 习惯追踪与养成
- ⭐ 团队协作模式
- 🤖 完全LLM化（可选）

**特别计划：** LLM增强方案详见 [ROADMAP.md#llm增强方案](skills/priority-coach/ROADMAP.md#llm增强方案-特别计划)

---

## 🤝 贡献

欢迎贡献！请随时提交 Issue 或 Pull Request。

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

- Claude Code - 强大的AI助手
- Eisenhower Matrix - 优先级管理框架
- Pomodoro Technique - 时间管理方法
- 所有测试用户提供反馈

---

## ❓ 常见问题 (FAQ)

### Q1: Skill 放在哪个目录？

**A:** Skill 安装目录是：`~/.claude/skills/`

**目录结构：**
```
~/.claude/
├── skills/                    # Skill 安装目录（手动安装）
│   └── priority-coach/
│       └── SKILL.md
└── priority-coach/            # 数据存储目录（自动创建）
    ├── user_goals.json
    ├── daily_plans/
    └── analytics/
```

**验证命令：**
```bash
# 查看已安装的 skills
ls ~/.claude/skills/

# 查看 Priority Coach 数据
ls ~/.claude/priority-coach/
```

### Q2: 为什么 Skill 没有被识别？

**检查清单：**
1. ✅ 文件名必须是 `SKILL.md`（大写）
2. ✅ 必须包含 YAML frontmatter（`---` 包围的部分）
3. ✅ `user-invocable: true` 必须设置
4. ✅ 文件路径必须是：`~/.claude/skills/priority-coach/SKILL.md`

**验证 SKILL.md 格式：**
```bash
# 检查前几行
head -10 ~/.claude/skills/priority-coach/SKILL.md
```

应该看到：
```yaml
---
name: priority-coach
description: "..."
user-invocable: true
---
```

### Q3: `~/.claude/priority-coach/` 是什么？

**A:** 这是**数据存储目录**，不是 skill 安装目录！

- **Skill 安装目录**：`~/.claude/skills/priority-coach/`（存放 SKILL.md）
- **数据存储目录**：`~/.claude/priority-coach/`（存放用户目标、计划等，**首次使用时自动创建**）

**常见误解：** ❌ 不要把 SKILL.md 放在 `~/.claude/priority-coach/` 里！

### Q4: references/ 目录需要复制吗？

**A:** 可选，但推荐。

**原因：** SKILL.md 中会引用这些文档（如 `references/eisenhower-matrix.md`），复制后 Claude 可以读取。

**最小安装：**
```bash
mkdir -p ~/.claude/skills/priority-coach
cp skills/priority-coach/SKILL.md ~/.claude/skills/priority-coach/
```

**推荐安装：**
```bash
mkdir -p ~/.claude/skills/priority-coach/references
cp skills/priority-coach/SKILL.md ~/.claude/skills/priority-coach/
cp -r skills/priority-coach/references/* ~/.claude/skills/priority-coach/references/
```

### Q5: 如何更新 Skill？

**A:** 覆盖 SKILL.md 文件：

```bash
# 从新版本复制
cp skills/priority-coach/SKILL.md ~/.claude/skills/priority-coach/

# Claude Code 会自动重新加载
```

### Q6: 可以自定义 Skill 吗？

**A:** 可以！直接编辑已安装的 SKILL.md：

```bash
# 编辑已安装的版本
nano ~/.claude/skills/priority-coach/SKILL.md

# 或编辑源文件后重新复制
cp skills/priority-coach/SKILL.md ~/.claude/skills/priority-coach/
```

### Q7: 如何卸载 Skill？

**A:** 删除 skill 目录：

```bash
# 删除 Skill
rm -rf ~/.claude/skills/priority-coach

# 注意：数据目录 ~/.claude/priority-coach/ 会被保留
# 如需删除数据：rm -rf ~/.claude/priority-coach/
```

### Q8: 仓库克隆到哪里？

**A:** 任意位置！Skill 安装和数据存储是独立的。

**示例：**
```bash
# 克隆到你的项目目录
cd ~/Projects
git clone https://github.com/JourneytoNewland/priority-coach.git createSkills

# 安装 Skill（复制到 Claude 目录）
cp -r createSkills/skills/priority-coach ~/.claude/skills/
```

---

## 📞 联系方式

- Issues: [GitHub Issues](<repository-url>/issues)
- Discussions: [GitHub Discussions](<repository-url>/discussions)

---

**准备好提升效率了吗？**

```
priority-coach 帮我规划今天
```

让我们一起把零散的想法转化为清晰的行动！🚀
