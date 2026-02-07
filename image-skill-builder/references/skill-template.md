# Skill 文件生成模板

根据用户回答自动填充以下模板，生成完整的 SKILL.md。

## SKILL.md 模板

```markdown
---
name: {{SKILL_NAME}}
description: {{DESCRIPTION}}
---

# {{DISPLAY_NAME}}

{{ONE_LINE_SUMMARY}}

## 工作流程

{{WORKFLOW_SECTION}}

## 风格配置

{{STYLE_SECTION}}

## API 配置

| 配置项 | 值 |
|-------|---|
| API URL | `https://generativelanguage.googleapis.com` |
| API Key | `AIzaSyDvvGGRbH4Os3Er0dYi0kE_AzE3_2b_Az8` |
| Model | `gemini-3-pro-image-preview` |
| 默认比例 | {{ASPECT_RATIO}} |
| 默认分辨率 | {{RESOLUTION}} |

## 保存路径规范

\```
/Users/ugreen/Documents/obsidian/09image/MMDD-{{PATH_PATTERN}}/
├── 01-{{FILE_PATTERN}}.png
├── 02-{{FILE_PATTERN}}.png
└── ...
\```

## 常见用法

{{USAGE_TABLE}}
```

---

## 工作流模板

### 模板 A: 文章/文档配图工作流

```markdown
### Phase 1: 分析内容 → 生成提示词

1. **读取内容** - 获取用户提供的文章/文档（当前打开文件或指定路径）
2. **结构分析** - 按标题拆分段落，提取每个段落核心思想
3. **生成风格指令** - 根据内容主题生成全局 STYLE INSTRUCTIONS
4. **生成提示词** - 为每个段落创建图片提示词（参考 references/style-guide.md）
5. **展示并确认** - 列出所有提示词，等待用户确认或修改

### Phase 2: 生成图片 → 插入文档

6. **批量生成** - 调用 `scripts/generate_image.py` 逐个生成
7. **保存图片** - 存入 `obsidian/09image/MMDD-主题名/` 目录
8. **插入文档** - 在每个段落标题后插入 `![[图片路径]]` 引用
```

### 模板 B: 品牌/Logo 批量变体工作流

```markdown
### Phase 1: 需求收集

1. **收集信息** - 品牌名、行业/用途、核心理念
2. **展示风格** - 展示可选风格，根据品牌属性推荐
3. **等待选择** - 用户选定风格

### Phase 2: 生成提示词

4. **批量变体** - 为品牌生成 N 个变体提示词：
   - 变体 1-2: 主风格，不同构图
   - 变体 3-4: 主风格，不同配色
   - 变体 5-6: 主风格，不同图标变化
   - 变体 7-N: 交叉风格探索
5. **展示确认** - 列出所有变体概要

### Phase 3: 批量生成

6. **逐个生成** - 调用脚本生成
7. **展示迭代** - 列出结果，询问是否迭代
```

### 模板 C: 分镜/故事板工作流

```markdown
### Phase 1: 故事润色与分镜拆分

1. **接收故事** - 获取用户描述的故事内容
2. **润色故事线** - 补充叙事细节，梳理情感弧线
3. **拆分分镜** - 将故事拆为 6-10 个关键帧
4. **展示脚本** - 以表格展示分镜脚本

### Phase 2: 风格选择

5. **展示风格** - 展示可选风格，推荐最适合的
6. **等待选择** - 用户选定风格

### Phase 3: 生成提示词与出图

7. **生成提示词** - 为每帧生成提示词（含一致性锚定）
8. **批量生成** - 逐帧生成，保持角色和风格一致
9. **展示迭代** - 列出结果，询问是否重新生成某帧
```

### 模板 D: 社交媒体图工作流

```markdown
### Phase 1: 收集需求

1. **确定主题** - 获取用户要发布的内容主题
2. **确定平台** - 小红书/公众号/X 等，决定尺寸
3. **选择模板** - 展示该平台常用的图片模板/风格

### Phase 2: 生成提示词

4. **生成提示词** - 根据主题和模板，生成 N 个变体
5. **展示确认** - 列出所有提示词概要

### Phase 3: 批量生成

6. **逐个生成** - 调用脚本生成
7. **展示挑选** - 列出结果，用户选择最满意的
```

### 模板 E: 通用批量生成工作流

```markdown
### Phase 1: 收集输入

1. **接收描述** - 用户提供主题/内容描述
2. **选择风格** - 展示可选风格，推荐匹配的风格

### Phase 2: 生成提示词

3. **生成提示词** - 根据描述和风格生成 N 个提示词
4. **展示确认** - 列出所有提示词，等待用户确认

### Phase 3: 批量生成

5. **逐个生成** - 调用 `scripts/generate_image.py`
6. **保存图片** - 存入 `obsidian/09image/MMDD-主题名/`
7. **展示迭代** - 列出结果，询问是否迭代或调整
```

---

## style-guide.md 生成模板

```markdown
# {{SKILL_NAME}} 风格指南

## 全局风格指令

\```
STYLE INSTRUCTIONS:
- 整体风格: {{STYLE_NAME}}
- 色彩方案: {{COLOR_SCHEME}}
- 比例: {{ASPECT_RATIO}}
- 分辨率: {{RESOLUTION}}
- 文字规则: {{TEXT_RULE}}
- 一致性: {{CONSISTENCY_RULE}}
\```

## 主风格提示词前缀

\```
{{STYLE_PREFIX}}
\```

{{#IF HAS_SECONDARY_STYLE}}
## 备选风格提示词前缀

\```
{{SECONDARY_STYLE_PREFIX}}
\```
{{/IF}}

## 提示词结构

每个提示词由以下部分组成：
1. **风格前缀** - 上方定义的通用描述
2. **内容描述** - 叙述性语言描述画面内容
3. **文字指令** - {{TEXT_INSTRUCTION}}
4. **一致性锚定** - {{CONSISTENCY_ANCHOR}}
5. **排除项** - {{EXCLUSIONS}}

## 提示词优化规则

1. 叙述性描述 > 关键词堆砌（Gemini 理解完整语句更好）
2. 明确指定背景、比例、文字量
3. 具体化视觉元素
4. 同一批次所有图使用相同风格前缀
```

---

## 变量映射规则

### SKILL_NAME
根据场景类型自动生成：
- 文章配图 → `article-illustration-{style}`
- Logo → `logo-generator-{style}`
- 分镜 → `storyboard-{style}`
- 社交媒体 → `social-media-{platform}`
- 海报 → `poster-{style}`
- 数据可视化 → `dataviz-{style}`
- 角色设计 → `character-{style}`

### DESCRIPTION
组合公式: `{场景动词}{内容描述}。{风格描述}。{触发词列表}。`

示例: `分析文章结构并批量生成赛博朋克风格配图。调用Gemini API为每个段落创建霓虹风格逻辑图。触发词："赛博配图"、"霓虹风格配图"。`

### WORKFLOW_SECTION
根据场景类型选择模板 A-E 并填充。

### STYLE_SECTION
从 style-library.md 提取用户选定的风格，填入风格前缀和配置。

### 脚本调用命令
```bash
python3 scripts/generate_image.py \
  --prompt "提示词" \
  --output "/Users/ugreen/Documents/obsidian/09image/MMDD-主题名/NN-描述.png" \
  --api-key "AIzaSyDvvGGRbH4Os3Er0dYi0kE_AzE3_2b_Az8" \
  --api-url "https://generativelanguage.googleapis.com" \
  --model "gemini-3-pro-image-preview" \
  --aspect-ratio "{{ASPECT_RATIO}}" \
  --resolution "{{RESOLUTION}}"
```
