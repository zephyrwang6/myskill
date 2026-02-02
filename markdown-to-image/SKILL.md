# Markdown to Image Skill

将 Markdown 内容（特别是 content-digest 输出）转换为精美的小红书风格图片海报。

## 功能特点

- **小红书风格**：紫色渐变背景 + 白色卡片 + 圆角设计
- **自动分页**：内容过长时自动分成多张图片（默认每页 5 个观点）
- **页码指示**：多页时显示 "1/3" 等页码
- **智能解析**：自动提取标题、简介、核心观点
- **本地运行**：使用系统 Chrome 渲染，无需联网

## 使用方式

### 命令行

```bash
python3 ~/.claude/skills/markdown-to-image/scripts/md2img.py "文件路径.md"
```

### 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `input` | 输入的 Markdown 文件路径 | 必填 |
| `-o, --output` | 输出目录 | `obsidian/attachments/MMDD-标题/` |
| `-p, --points-per-page` | 每页显示的观点数量 | 5 |

### 示例

```bash
# 默认用法 - 自动保存到 attachments 目录
python3 ~/.claude/skills/markdown-to-image/scripts/md2img.py ~/Documents/obsidian/每日播客/0129-Sebastian-Raschka-LLM技术现状.md

# 指定输出目录
python3 ~/.claude/skills/markdown-to-image/scripts/md2img.py input.md -o ~/Desktop/output/

# 每页显示 4 个观点
python3 ~/.claude/skills/markdown-to-image/scripts/md2img.py input.md -p 4
```

## 输出目录规则

默认保存到：`/Users/ugreen/Documents/obsidian/attachments/MMDD-标题/`

- `MMDD` 从文件名提取（如 `0129-xxx.md` → `0129`）
- 如果文件名无日期，使用当天日期
- 生成的图片命名为 `page-1.png`, `page-2.png`, ...

## 支持的 Markdown 格式

脚本会自动解析以下结构：

```markdown
# 标题

简介段落...

1、核心观点一。观点说明...

2、核心观点二。观点说明...

...

---

# 精华片段（会被忽略）
```

支持的观点格式：
- `1、观点内容`
- `1. 观点内容`
- `1) 观点内容`
- `1️⃣ 观点内容`

## 依赖

- Python 3.9+
- playwright (`pip3 install playwright`)
- markdown (`pip3 install markdown`)
- Google Chrome（使用系统安装的 Chrome）

## 与 podcast-workflow 集成

在 `podcast-workflow` 中，当 content-digest 处理完成并保存到飞书后，会询问用户是否转为图片。

确认后自动调用此脚本：

```bash
python3 ~/.claude/skills/markdown-to-image/scripts/md2img.py "每日播客/MMDD-xxx.md"
```

生成的图片保存到 `attachments/MMDD-xxx/` 目录下，可直接用于小红书发布。

## 图片效果

- 尺寸：720px 宽度（小红书最佳）
- 背景：紫色渐变（#667eea → #764ba2）
- 卡片：白色圆角卡片，带阴影
- 观点：每个观点独立卡片，带 emoji 编号
- 页码：多页时底部显示页码
