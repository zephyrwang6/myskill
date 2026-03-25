---
name: skill-logger
description: |
  记录一次 Skill 使用情况到日志文件。每次用完某个 Skill 后调用，追加一条使用记录。
  触发词："记录这次使用"、"记录用了 xxx"、"log skill"、"记录一下"（在使用完某个 Skill 之后）。
  用于追踪 Skill 使用频率和满意度，为 skill-analyzer 提供数据。
---

# Skill 使用日志记录

每次使用完某个 Skill 后，调用本 Skill 记录一条使用日志。日志追加到 `06 计划/skill_usage_log.jsonl`。

## 日志文件位置

```
$OBSIDIAN_VAULT/06 计划/skill_usage_log.jsonl
```

`OBSIDIAN_VAULT` 环境变量需在 `.env` 中配置（见下方）。

## 使用方式

**方式一：用完 Skill 后手动触发**

```
记录这次使用：x-post，场景是把播客笔记改成即刻动态，满意度 4 分，结尾不够有力手动改了
```

**方式二：让 AI 引导填写**

直接说"记录一下"，AI 会依次询问：
1. 用了哪个 Skill？
2. 使用场景是什么？
3. 满意度（1-5 分）？
4. 备注（可选）？

## 工作流程

### Step 1：收集信息

如果用户没有提供完整信息，逐项询问：

- **skill**：Skill 名称（如 `x-post`）
- **scene**：这次用它做了什么（一句话描述）
- **satisfaction**：满意度 1-5 分（1=很差，3=一般，5=完美）
- **note**：备注，比如哪里不满意、手动改了什么（可为空）

### Step 2：运行追加脚本

```bash
python3 scripts/log_skill_usage.py \
  --skill "x-post" \
  --scene "把播客笔记改成即刻动态" \
  --satisfaction 4 \
  --note "结尾不够有力，手动改了"
```

### Step 3：确认写入

脚本输出追加成功后，向用户确认：

```
✅ 已记录：x-post（满意度 4/5）
   场景：把播客笔记改成即刻动态
   备注：结尾不够有力，手动改了
```

## 日志格式

每条记录是一行 JSON：

```json
{"date": "2026-03-24", "weekday": "周二", "week": "W13", "skill": "x-post", "scene": "把播客笔记改成即刻动态", "satisfaction": 4, "note": "结尾不够有力，手动改了"}
```

## 环境变量配置

在 `~/.env` 或项目根目录的 `.env` 文件中配置：

```bash
# Skill 日志文件所在的 Obsidian vault 路径
OBSIDIAN_VAULT=/Users/ugreen/Documents/obsidian
```

脚本通过 `os.environ['OBSIDIAN_VAULT']` 读取，不要把路径硬编码进脚本。
