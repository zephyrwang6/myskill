---
name: content-digest
description: >
  Transform long-form content (YouTube videos, podcasts, interviews, articles) into engaging short-form and long-form narratives.
  Extracts core insights and presents them in two styles: concise social media posts (300-800 characters with numbered emoji lists)
  and detailed narrative articles (1500-3000+ characters with story arcs). Use when users provide YouTube links, podcast transcripts,
  long articles, or interview content and want summaries, key insights, or content reformatted for different platforms.
---

# Content Digest

Transform long-form content into compelling short-form and long-form narratives.

## Overview

This skill converts lengthy content (YouTube videos, podcasts, interviews, articles) into two distinct formats:

1. **Short-Form** (短文): Social media-friendly summaries (300-800 characters) with numbered emoji lists (1️⃣2️⃣3️⃣)
2. **Long-Form** (长文): Narrative articles (1500-3000+ characters) with story arcs, section headers, and integrated quotes

## Workflow

### 1. Obtain the Content

**If user provides a URL:**
- YouTube links: Use WebFetch or attempt to extract transcript
- Article URLs: Use WebFetch to retrieve content
- Podcast links: Fetch transcript if available

**If user provides text:**
- Read the full transcript or article text directly

**If content is unclear:**
- Ask: "Please provide the YouTube link, podcast transcript, or article you'd like me to transform."

### 2. Determine Output Format

**If user specifies format:**
- Proceed with their choice (short-form only, long-form only, or both)

**If user does not specify:**
- Ask: "Would you like: (1) Short-form only, (2) Long-form only, or (3) Both versions?"

**Default behavior:**
- Generate both versions to maximize value

### 3. Deep Analysis - Four-Stage Process

**CRITICAL: Follow this systematic process to ensure depth**

#### Stage 1: Extract All Viewpoints (50+ minimum)

Read the entire content thoroughly and extract ALL viewpoints, including:
- Explicit statements and opinions
- Implicit beliefs revealed through stories
- Decision-making rationales
- Observations about the industry/domain
- Personal experiences and lessons
- Counterexamples and contrasts
- Numbers, data points, specific examples

**Goal**: Create a comprehensive list of 50+ viewpoints before filtering. Don't judge quality yet - just extract everything.

#### Stage 2: Filter for Non-Consensus & Depth

From the 50+ viewpoints, identify and mark those that are:
- **Non-consensus** (非共识): Challenges industry conventional wisdom
- **Personal/private insights** (个人私下表达): Things people think but rarely say publicly
- **Counterintuitive** (反直觉): Surprises even informed readers
- **Interesting trivia** (有意思的冷知识): Specific details that reveal deeper patterns
- **Mental models**: Frameworks that explain decision-making
- **Second-order insights**: Not just "what" but "why this matters philosophically"
- **Paradoxes and tensions**: Contradictions that expose underlying principles

**Goal**: Flag the 20-30 viewpoints that pass the "non-obvious test" - would a smart, informed reader already know this?

#### Stage 3: Select Core Narrative Elements

Identify:
- **Core narrative**: What's the main story or theme?
- **Memorable quotes**: Direct quotes that capture big ideas or reveal character
- **Turning points**: Moments of realization or paradigm shifts
- **Dramatic elements**: Irony, contrast, or unexpected outcomes
- **Specific details**: Names, numbers, dates that prove the deeper point

#### Stage 4: Curate Final Insights

From the filtered viewpoints (Stage 2) and narrative elements (Stage 3):
- **For short-form**: Select 10-15 most profound, actionable insights
- **For long-form**: Use the same 10-15 insights as the foundation, then weave in narrative arc

### 4. Generate Short-Form Version

**CRITICAL: Use ONLY the 10-15 curated insights from Stage 4**

Consult [style-guide.md](references/style-guide.md) for detailed guidelines. See [examples.md](references/examples.md) for reference.

**Structure:**
```
# MMDD：[嘉宾名] X [栏目名]：[一句话核心观点]

今天看到 [嘉宾名] 去了 [栏目名] 的播客。

[嘉宾名] [2-3句话介绍嘉宾背景和核心成就，用具体数据]。

这期播客总共录了 [时长]，[嘉宾名] 谈到了 [N] 个有趣的观点：

1、[观点标题/关键词]。[完整的逻辑阐述，包含推理过程，2-4句话]

2、[观点标题/关键词]。[完整的逻辑阐述，包含推理过程，2-4句话]

3、[观点标题/关键词]。[完整的逻辑阐述，包含推理过程，2-4句话]

...
[Continue with 10-15 total points]

---
```

**标题格式 (重要):**
- 格式：`# MMDD：嘉宾名 X 栏目名：一句话观点`
- 示例：`# 0130：Peter Steinberger X The Pragmatic Engineer：一天600次提交，代码比以前更好`
- 一句话观点要抓住最反直觉或最有冲击力的点

**开头格式 (重要):**
- 第一句：简单说看了什么 `今天看到 [嘉宾] 去了 [栏目] 的播客。`
- 第二段：2-3句介绍嘉宾背景，必须有具体数据（数字、公司名、产品名）
- 第三句：过渡句 `这期播客总共录了 [时长]，[嘉宾] 谈到了 [N] 个有趣的观点：`
- 如果不知道时长，可以写"将近两小时"或省略时长

**List Format Rules (重要):**
- **使用数字+顿号格式** (`1、` `2、` `3、`...)
  - 注意是顿号「、」不是点号「.」
- **每条是完整段落**，包含：
  - 观点/结论（第一句）
  - 逻辑推理/因果解释（后续句子）
  - 具体例子或数据（如有）
- **每条 2-4 句话**，50-150 字
- **观点要有深度**：
  - ✅ "AI 应用创业者不会相信 AGI。逻辑很简单，如果真信，就不应该做 AI 应用创业。AGI 如果存在，创业就只剩一件事：去做有机会达成 AGI 的模型。"
  - ❌ "AI 应用创业者不相信 AGI"（太简单，没有逻辑推理）
- **保持 10-15 条**（不是 8-12 条）

**Key principles:**
- 标题要有冲击力，抓住最反直觉的观点
- 开头简洁，快速进入正题
- 每条观点要有完整的逻辑链条
- 观点之间可以有递进或对比关系
- Include specific data when available (numbers, names, percentages)
- Pass the non-obvious test (would informed readers NOT already know this?)
- End with separator line `---`

### 5. Generate Long-Form Version

**CRITICAL: Build ENTIRELY on the same 10-15 curated insights from Stage 4**

The long-form version is NOT a separate summary - it's a narrative expansion of the SHORT-form insights with story arc and analytical depth.

Consult [style-guide.md](references/style-guide.md) for detailed guidelines. See [examples.md](references/examples.md) for reference.

**IMPORTANT: Choose the right style based on content type**

**For interview/podcast/dialogue content → Use Style B (对话式访谈)**
**For solo speech/article/essay → Use Style A (叙事性文章)**

---

**Style A Structure (叙事性文章):**
```
[Compelling Title - derived from core insight]

[Opening: Set the scene using one of the 10-15 insights]

### [Section 1: Background]
"[Key quote]"
[Context - connect to 2-3 of your curated insights]

### [Section 2: Main Content]
[Narrative development - weave in 4-5 curated insights with quotes and analysis]

### [Section 3: Climax]
[Dramatic highlights - reveal most counterintuitive insight]

### [Section 4: Resolution/Turning Point]
"[Pivotal quote]"
[Significance - tie back to mental model or principle]

### [Epilogue: Reflection]
[What happened after / Ironic contrast - connect final insights]

[Optional: Source attribution]
```

**Key principles (Style A):**
- Compelling title derived from your deepest insight
- Clear section headers for navigation
- **Each section develops 2-4 of your 10-15 curated insights** with narrative and quotes
- Integrate direct quotes naturally - use them to prove your curated insights
- Build narrative arc: setup → development → climax → resolution
- Use dramatic irony when relevant ("他不知道的是..." / "He didn't know that...")
- Include specific details (names, numbers, dates) from your curated list
- **Deep analytical layer** - weave in your Stage 2 filtered insights:
  - Why specific choices reveal broader strategic principles
  - How contradictions or tensions expose underlying philosophies
  - What the subject's evolution teaches about the domain
  - Connections between micro-decisions and macro-outcomes
- 2000-3500+ characters to properly develop 10-15 deep insights

---

**Style B Structure (对话式访谈):**
```
[前言/导语 - 编辑者视角]
断断续续，终于看完了...[个人感受]
干货很多。[嘉宾]可能是...[定位评价]
[为什么值得关注]
我今天不忙，把这次访谈全文精编出来，供大家学习。赠人玫瑰，手有余香。
[可选：节日祝福]
下面是 YouTube/播客链接：[链接]

#01 [主题标题 - 简短有力]
主持人：[问题]
嘉宾：[回答 - 保留对话感]

[编辑补充：数据解读、背景、个人观点]
[可用："我觉得这个点真的太重要了" "这太有意思了"]

主持人：[追问]
嘉宾：[深入回答]

[继续分析]
[可选：插入相关文章链接]

#02 [第二主题]
主持人：[新话题]
嘉宾：[回答]

[编辑解读]
...

#03-#0N [按主题继续]
...
```

**Key principles (Style B):**
- **口语化开场**："断断续续看完" "干货很多" 体现真实感
- **编号主题**：用 #01 #02 等清晰分段，主题标题直白有力
- **保留对话**：60-70%保持"主持人：""嘉宾："格式
- **编辑介入**：20-30%加入编辑分析、补充、个人反应
- **口语化表达**："太离谱了" "我觉得" "说实话" "天哪" "完全是这样"
- **具体数据**：必须保留数字、人名、公司名
- **补充链接**：适时插入"文章链接：..." 延伸阅读
- **人情味结尾**："赠人玫瑰，手有余香"
- **主题重组**：不按时间线，按话题逻辑重新组织
- 3000-8000+ 字（根据访谈长度）

### 6. Quality Check

Before delivering, verify you followed the four-stage process:

**Stage 1 verification:**
- [ ] Extracted 50+ viewpoints from source material (can be implicit - doesn't need to be shown to user)

**Stage 2 verification:**
- [ ] Filtered for non-consensus, counterintuitive, and deep insights
- [ ] Identified personal/private expressions and interesting trivia
- [ ] Marked mental models and second-order insights

**Stage 3 & 4 verification:**
- [ ] Selected 10-15 most profound insights for final output
- [ ] Short version uses ALL 10-15 curated insights
- [ ] Long version develops the SAME 10-15 insights with narrative

**Depth check - Each of the 10-15 insights must:**
- [ ] Pass the "non-obvious test": Would an informed reader already know this?
- [ ] Reveal a mental model, framework, or underlying principle
- [ ] Challenge conventional thinking OR expose interesting trivia
- [ ] Connect ideas in an unexpected way OR show second-order effects

**Quality verification:**
- [ ] Quotes are accurate and attributed
- [ ] No editorializing beyond source material
- [ ] Writing is engaging, not robotic
- [ ] Both versions can stand alone
- [ ] Numbers/facts are specific, not vague
- [ ] The "so what?" is clear to readers
- [ ] **Every takeaway reveals WHY it matters**, not just WHAT happened
- [ ] Short and long versions share the same insight foundation

### 7. Deliver Output

**文件保存规范：**
- **保存位置**：`/Users/ugreen/Documents/obsidian/每日播客/`
- **文件命名**：`MMDD-主题关键词.md`
  - `MMDD` 为当天日期（如 0109 表示 1 月 9 日）
  - `主题关键词` 为 2-6 个字的内容概括（如 `Lovable增长策略`、`AI编程工具`）
  - 示例：`0109-Lovable增长策略.md`、`0108-睡眠科学.md`
- **自动保存**：生成内容后，使用 Write 工具将完整内容保存到上述路径

**格式规范：**
- **行距**：段落内不留空行，段落之间留一个空行
- **文档标题**：使用 `# MMDD：嘉宾名 X 栏目名：一句话观点` 格式
- **长文标题**：使用 `# 精华片段`

**结构模板：**
```
# MMDD：[嘉宾名] X [栏目名]：[一句话核心观点]

今天看到 [嘉宾名] 去了 [栏目名] 的播客。

[嘉宾名] [2-3句话介绍嘉宾背景，用具体数据]。

这期播客总共录了 [时长]，[嘉宾名] 谈到了 [N] 个有趣的观点：

1、[观点]。[逻辑推理]

2、[观点]。[逻辑推理]

...（共 10-15 条）

---

# 精华片段

[长文内容 - Style B 对话式访谈格式]

---

[结束语]
```

**开场介绍模板（新格式）：**
```
# 0130：Peter Steinberger X The Pragmatic Engineer：一天600次提交，代码比以前更好

今天看到 Peter Steinberger 去了 The Pragmatic Engineer 的播客。

Peter Steinberger 创建了 PSPDF kit——一个被超过 10 亿设备使用的 PDF 框架，后来经历严重职业倦怠卖掉股份消失了 3 年。2024 年回归后，他用完全不同的方式创建了 Clawdbot，一周从 100 星涨到 3300 星。

这期播客总共录了将近两小时，Peter 谈到了 11 个有趣的观点：
```

**观点列表示例：**
```
1、AI 应用创业者不会相信 AGI。逻辑很简单，如果真信，就不应该做 AI 应用创业。AGI 如果存在，创业就只剩一件事：去做有机会达成 AGI 的模型。

2、创业的产品定位，关键点之一是：要做工作流的上游。上游的产品，不容易被下游的产品吃掉，反过来，发展到一定阶段，上游可以做下游的事。

3、Code Reviews 已死。对 prompts 的兴趣比代码更大，PR 应该叫"Prompt Requests"。因为 prompt 给的信号更高——你是怎么得到这个解决方案的？问了什么？有多少引导？
```

**结束语模板：**
```
---

[嘉宾名字]凭[具体贡献]，[产生的影响]。

用他的话收个尾："[引用一句有力的话]"。[最后一句个人感受或升华]。

YouTube 链接：[链接]
```

If only one format was requested, still include opening and closing sections.

## Core Principles

### Extract Strategically

**What to extract:**
- **Deep, counterintuitive insights** - not surface observations:
  - Mental models and frameworks that drive decision-making
  - Paradoxes and tensions that reveal underlying principles
  - Second-order effects and non-obvious consequences
  - Patterns that connect specific tactics to strategic outcomes
- **Surprising insights that challenge common wisdom**
- **Practical wisdom with WHY** - not just "do X" but "X reveals principle Y"
- Memorable quotes capturing big ideas or philosophical stances
- Turning points and paradigm shifts
- Human moments (vulnerability, humor, authenticity) that reveal character
- Contextual ironies (what they didn't know then vs. now)

**What to avoid:**
- Linear summarization without insight
- Including everything (be selective)
- **Stating the obvious** - if a reasonably informed reader would already know it, dig deeper
- Surface-level descriptions without explaining WHY it matters
- Losing the human voice
- Adding information not in source
- AI-style generic phrasing
- **Shallow takeaways** - "X did Y" without revealing what principle or framework this demonstrates

### Voice & Tone

- **Conversational but insightful**: Like explaining to a smart friend
- **Show, don't tell**: Use quotes to prove points
- **Respect the source**: Don't editorialize or distort
- **Find the story**: Every piece has a narrative arc

### Be Token-Efficient

This skill focuses on creative transformation, not code execution. The writing process happens in-context without requiring scripts.

## Resources

### references/style-guide.md

Detailed writing guidelines for both short-form and long-form styles, including:
- Structure patterns
- Key characteristics
- Writing principles
- What to avoid
- Extraction strategies

Load this when you need detailed guidance on tone, structure, or style.

### references/examples.md

Complete reference examples:
- Short-form example: Boris Cherny's Claude Code workflow
- Long-form example: Manus/Peak Ji interview article

Load this when you need concrete examples of the final output quality and style.

## Notes

- Both styles require full comprehension of source material - don't skim
- Short-form emphasizes actionable takeaways
- Long-form emphasizes narrative and character
- Quotes must be accurate and in context
- Works best with content that has inherent narrative or insight
- Can combine with translation if source is in different language
- Ideal for content creators repurposing long content for different platforms
