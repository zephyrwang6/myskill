---
name: skill-analyzer
description: |
  分析 Skill 使用日志，输出频率排行、满意度趋势、低频 Skill 清单。每周运行一次。
  触发词："分析 Skill 使用情况"、"Skill 周报"、"哪些 Skill 用得多"、"看看 Skill 数据"。
  依赖 skill-logger 写入的 skill_usage_log.jsonl 日志文件。
---

# Skill 使用分析

读取 `06 计划/skill_usage_log.jsonl`，分析 Skill 使用情况，输出本周总结报告。

## 日志文件位置

```
$OBSIDIAN_VAULT/06 计划/skill_usage_log.jsonl
```

## 使用方式

```
分析 Skill 使用情况
```

默认分析最近 7 天。指定时间范围：

```
分析过去两周的 Skill 数据
```

## 工作流程

### Step 1：运行分析脚本

```bash
python3 scripts/analyze_skill_usage.py --days 7
```

指定时间范围：

```bash
python3 scripts/analyze_skill_usage.py --days 14
```

### Step 2：输出分析报告

脚本输出原始数据后，AI 整理成以下格式的报告：

---

**📊 Skill 使用周报（最近 7 天）**

**总览**
- 共使用 Skill N 次，覆盖 X 个不同 Skill
- 平均满意度：X.X / 5

**使用频率排行**

| 排名 | Skill | 使用次数 | 平均满意度 |
|------|-------|---------|-----------|
| 1 | x-post | 8 | 4.2 |
| 2 | podcast-workflow | 5 | 4.6 |
| 3 | content-digest | 4 | 4.0 |

**满意度偏低的 Skill（< 3.5 分）**

| Skill | 平均满意度 | 常见问题 |
|-------|-----------|---------|
| xxx | 3.0 | 备注中反复出现"改了结尾" |

**本周未使用的 Skill**（有记录但本周零调用）

- skill-a
- skill-b

**建议**

- `xxx` 满意度持续下降，建议检查 SKILL.md 是否需要更新规则
- `yyy` 两周未使用，考虑是否仍有需求
- `zzz` 本周高频使用，可以考虑做自动化

---

### Step 3：询问是否归档

```
要把这份报告存到 06 计划/05 周复盘/ 吗？
```

## 环境变量配置

在 `~/.env` 或项目根目录的 `.env` 文件中配置：

```bash
OBSIDIAN_VAULT=/Users/ugreen/Documents/obsidian
```
