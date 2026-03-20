---
name: podcast-script-generator
description: Transform structured podcast notes into engaging video scripts with a conversational, first-person broadcasting style. Use when user asks to "generate podcast script", "convert to broadcast style", "make video script", "rewrite for video", "口播脚本", "改成口播", or wants to turn podcast summaries into presenter-style content for short videos.
---

# Podcast Script Generator

Transform structured podcast notes into engaging, presenter-style video scripts.

## When to Use

Use this skill when the user wants to:
- Convert structured notes into presenter-style video scripts
- Rewrite podcast summaries for short video content
- Create conversational broadcast content from formal notes
- Generate scripts with strong personal voice and recommendations

## Workflow

### Step 1: Get Source Material

Ask the user for the content source:

1. **Direct paste**: User pastes text directly
2. **Daily podcast file**: File from `/Users/ugreen/Documents/obsidian/每日播客/`
3. **Other file path**: Any other markdown file

If user provides a file path, read it with Read tool.

### Step 2: Analyze Content Structure

Identify:
- **Title & Guest**: Podcast name and main speaker
- **Core Theme**: Main topic discussed
- **Key Points**: Numbered list of insights (usually 3-12 points)
- **Highlights**: Dialogue excerpts or quotes
- **Data/Examples**: Statistics, case studies, comparisons

### Step 3: Apply Broadcasting Style

Read `references/style-reference.md` and `references/example-conversions.md` to internalize the target style.

#### Opening (Varied, Natural)

**Avoid the fixed template.** Instead, choose from these natural openings based on content:

- "今天要给你推荐一期播客..."
- "最近听到一期特别有意思的节目..."
- "这期是我最近听到的对[领域]非共识观点最多的一期..."
- "这个月听到的最有收获的一期播客..."
- "如果你关注[话题]，这期播客你一定要听..."

Then introduce the guest naturally:
- "嘉宾是[名字]，[一句话身份]..."
- "介绍一下[名字]，[成就/背景]..."

Add a hook specific to the content:
- "她几个月前演讲说'不要相信设计流程'，3个月后自己就觉得过时了..."
- "他可能是华尔街唯一一个既能看懂财务报表，又能看懂火箭发动机的人..."

#### Content Transformation Rules

**Rule 1: No "发言人" markers**

- Direct output without speaker labels
- Use paragraph breaks to indicate natural pauses

**Rule 2: Banned sentence patterns**

DO NOT use these rigid contrasting patterns:
- ❌ "不是...而是..."
- ❌ "是...不是..."
- ❌ "被...倒逼着..."
- ❌ "从...变成...，从...变成..." (overly structured parallel)

Instead, express contrast naturally:
- ✅ "设计不是主动想变，是工程端的变化逼着你必须变"
- ✅ "以前大家把这套流程当真理，但现在基本已经死了"
- ✅ "工程师已经转向命令行和agent模式，而设计师开始用IDE了"

**Rule 3: Use conversational connectors SPARINGLY**

Limit these phrases (max 1-2 per section):
- "说白了" → use "意思是" or just omit
- "这什么意思呢" → use "为什么？" or just explain directly
- "所以你看" → use "结果就是" or just show the result

**Rule 4: Natural transitions**

Instead of rigid structure markers, use:
- "第一个让我意外的点是..."
- "还有一个特别反直觉的发现..."
- "这里有个特别有意思的地方..."
- "更夸张的是..."
- "说到这个，就不得不提..."

**Rule 5: Personal commentary**

Insert reactions naturally:
- "我觉得这个点特别值得思考"
- "特别反直觉"
- "特别有意思"
- "让我特别意外"

**Rule 6: Explain concepts conversationally**

When explaining complex ideas:
- Start with the problem or context
- Walk through the logic step by step
- Use "打个比方" for analogies when needed
- End with "就是说" or just the conclusion

#### Closing

End naturally:
- "好了，今天就聊到这..."
- "今天就分享到这里..."
- "今天就聊到这，如果你也[相关话题]，强烈建议去听听完整播客..."
- "我是[昵称]，下次见"

### Step 4: Output Format

Produce:

1. **Full script** without speaker markers, with natural paragraph breaks
2. **Estimated duration** (250 words ≈ 1 minute)
3. **3-5 suggested titles** for the video
4. **Recommended hashtags/topics**

## Style Guidelines

### Paragraph Structure
- Each paragraph: 2-4 short sentences
- Use empty lines between paragraphs for pacing
- One idea per paragraph
- Key data/quotes can stand alone

### Tone
- Conversational, like talking to a friend
- First person "我" perspective
- Natural enthusiasm without exaggeration
- Occasional rhetorical questions

### Language
- Avoid written-style transitions
- Prefer short sentences
- Use spoken Chinese patterns
- Keep technical terms but explain them naturally

## Reference Materials

- `references/style-reference.md` - Full example of target style
- `references/example-conversions.md` - Before/after conversion examples with techniques

## Constraints

1. Preserve all factual information - change style, not substance
2. Maintain accuracy of data, quotes, and attributions
3. Target length: 750-1500 words (3-6 minutes of video)
4. If source is too long, ask user which points to prioritize
5. NO "发言人" markers
6. NO rigid "不是...而是" patterns
7. Use "说白了" max 1-2 times in entire script
