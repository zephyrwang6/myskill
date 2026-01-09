---
name: ai-writing-assistant
description: AI-powered writing assistant for social media content creation. Provides 6 structured writing methods: conversational writing, outline-based writing, completion-style writing, inspiration generation, revision optimization, and material integration. Use when users need help with: (1) Writing social media posts, articles, or content, (2) Overcoming writer's block or difficulty expressing ideas, (3) Structuring thoughts and improving writing quality, (4) Integrating multiple sources into coherent content.
---

# AI Writing Assistant

## Overview

Enables users to create compelling social media content through structured writing methods. This skill helps transform ideas into polished content by providing guided workflows tailored to different writing scenarios and challenges.

## Quick Diagnosis

Before choosing a method, quickly assess the user's situation:

**Key Questions to Ask:**
- What type of content are you trying to create? (Article, post, reflection, tutorial)
- How much content/ideas do you already have? (None, some scattered thoughts, detailed outline, complete draft)
- What's your main challenge? (Getting started, organizing ideas, polishing quality, finding unique angles)

Based on answers, recommend the most suitable method from the 6 options below.

## Writing Methods

### Method 1: Conversational Writing (对话式创作)

**Best for:** Personal experience sharing, reflections, year-end summaries, project reviews

**When to use:** User has ideas but doesn't know how to start or organize them

**Workflow:**
1. **Set the interview frame**
   ```prompt
   我想写一篇关于【主题】的文章，但还没想清楚怎么写。

   请你扮演一个资深编辑，通过提问帮我梳理思路。规则如下：
   1. 一次只问一个问题
   2. 根据我的回答追问细节
   3. 问题要能挖掘我的真实经历和独特观点
   4. 大概问 8-10 个问题
   5. 问完后帮我整理成文章大纲

   现在开始第一个问题。
   ```

2. **Answer questions naturally** - User responds conversationally without worrying about structure

3. **Integrate into draft**
   ```prompt
   根据我们的对话，请帮我：
   1. 整理成一篇文章的初稿
   2. 保留我的原话和表达风格
   3. 补充必要的过渡段落
   4. 标注哪些地方需要我补充细节
   ```

4. **Manual polishing** - User refines with personal touches, adjusts flow, adds vivid opening/closing

**Key benefits:** Extracts authentic personal experiences, maintains user's voice, reduces mental overhead

### Method 2: Outline-Based Writing (大纲式创作)

**Best for:** Opinion pieces, tutorials, structured articles, technical documentation

**When to use:** User has clear ideas about what to say but needs help with expansion

**Workflow:**
1. **Create detailed outline** with clear sections and key points for each part:
   ```markdown
   ## 文章大纲：[主题]

   ### 一、开头
   - 观点：[核心观点]
   - 预期反应：[读者可能的反应]
   - 承诺：[文章价值]

   ### 二、主体部分
   - 观点1：[分论点1]
     - 案例：[支撑案例]
   - 观点2：[分论点2]
     - 案例：[支撑案例]

   ### 三、结论
   - 总结观点
   - 给出建议
   ```

2. **AI expansion prompt:**
   ```prompt
   请根据以下大纲扩写文章：

   [粘贴大纲]

   要求：
   1. 严格按照大纲结构
   2. 每个观点都要有具体论证
   3. 语气：专业但不学究，像在和朋友聊天
   4. 总字数：2000字左右
   ```

3. **Manual refinement** - Enhance opening, add real examples, remove AI clichés, adjust tone

**Key principle:** The more detailed the outline, the better the AI expansion quality

### Method 3: Completion-Style Writing (补充式创作)

**Best for:** Narrative articles, personal stories, content with clear flow

**When to use:** User knows the structure and main points but struggles with detailed expression

**Workflow:**
1. **Write paragraph starters** (1-2 sentences for each paragraph):
   ```markdown
   ## 文章草稿（请补充完整）

   去年我做了一个决定，现在回头看，这可能是我职业生涯最重要的转折点。[请补充：描述这个决定是什么，当时的背景]

   做这个决定的时候，其实我很犹豫。[请补充：犹豫的原因，内心的挣扎]

   但最终推动我行动的，是一件小事。[请补充：一个具体的触发事件]

   现在一年过去了，我想分享三个最大的收获。[请补充：三个收获，每个100字左右]

   如果你也在类似的十字路口，我的建议是：[请补充：具体建议]
   ```

2. **AI completion prompt:**
   ```prompt
   请根据我的草稿，补充 [请补充] 标注的部分。

   要求：
   1. 保持我的叙述风格
   2. 内容要具体，不要空泛
   3. 补充的内容要和我的开头自然衔接
   ```

3. **Replace and polish** - Substitute generic content with personal experiences, add specific details

**Key benefits:** User controls rhythm and flow while AI handles detailed completion

### Method 4: Inspiration Generation (灵感激发式创作)

**Best for:** Topic selection, finding fresh angles, overcoming creative blocks

**When to use:** User has general direction but needs specific ideas or perspectives

**Three scenarios:**

**Scenario 1: Topic selection**
```prompt
我想写关于【领域】的内容，目标读者是【人群】。

请帮我：
1. 列出 10 个可能的选题角度
2. 每个角度说明：为什么读者会感兴趣、有什么独特价值
3. 标注哪些是常见角度，哪些是新颖角度
```

**Scenario 2: Fresh perspectives**
```prompt
我要写一篇关于【主题】的文章，但感觉没什么新鲜观点可说。

请帮我：
1. 列出关于这个主题的 5 个常见观点
2. 针对每个常见观点，提供一个「反常识」的角度
3. 给出 3 个可能被忽视的切入点
```

**Scenario 3: Structuring approaches**
```prompt
我想表达的核心观点是：[你的观点]

请帮我想 5 种不同的文章结构来呈现这个观点：
1. 每种结构的逻辑主线
2. 各自的优缺点
3. 适合什么样的读者
```

**Key principle:** AI is brainstorming partner, not decision maker

### Method 5: Revision Optimization (改写优化式)

**Best for:** Important articles requiring polishing, improving writing quality

**When to use:** User has a draft but wants to enhance quality and impact

**Workflow:**
1. **Write initial draft** - Don't追求完美，先把想法写出来

2. **AI diagnosis prompt:**
   ```prompt
   从现在起，你是一个冷静刻薄的「内容主编」，禁止恭维和客套，不用迎合我的观点，要站在比我更外部的视角审稿。请你专门按照这 8 点挑毛病：
   1）有没有「活人」的思考过程；
   2）故事节奏有没有起伏；
   3）有没有让读者共鸣的真实痛点；
   4）是否始终围绕目标人设；
   5）读者有没有明确的信息增益；
   6）案例是否足够好玩，有记忆点；
   7）目标受众是谁，范围是否合适；
   8）语气是否像在跟读者对话、能激发评论。

   每一点都请给出具体问题和修改建议，而不是泛泛而谈。

   这是我写的初稿：
   [粘贴初稿]
   ```

3. **Targeted optimization** - Based on diagnosis, ask for specific improvements:
   ```prompt
   请帮我改写文章的开头，要求：
   - 更抓人眼球
   - 快速切入主题
   - 保留我的核心信息

   原开头：[粘贴]
   ```

4. **Manual judgment** - Decide which suggestions to adopt based on maintaining personal voice

### Method 6: Material Integration (素材整合式创作)

**Best for:** Research-based articles, content summaries, integrating multiple sources

**When to use:** User has abundant materials that need synthesis into coherent content

**Workflow:**
1. **Collect materials** - Articles, reports, notes, data, cases

2. **AI integration prompt:**
   ```prompt
   我要写一篇关于【主题】的文章。

   以下是我收集的素材：
   [粘贴素材]

   请根据这些素材：
   1. 提炼出 3-5 个核心观点
   2. 组织成一篇逻辑清晰的文章
   3. 标注哪些是素材中的内容，哪些是你补充的
   ```

3. **Major revision required** - Add personal judgments, rewrite in own voice, supplement with experiences

**Note:** This method often produces "AI-flavored" content and requires significant personal input

## Method Selection Guide

| User Situation | Recommended Method | Key Indicator |
|----------------|-------------------|---------------|
| "I have experiences but don't know how to start" | Method 1: Conversational | Has stories, no structure |
| "I know exactly what I want to say" | Method 2: Outline-based | Clear opinions, needs expansion |
| "I know the flow but struggle with details" | Method 3: Completion-style | Clear structure, incomplete execution |
| "I don't know what to write about" | Method 4: Inspiration | No clear topic or angle |
| "I have a draft but it's not good enough" | Method 5: Revision optimization | Complete draft, quality concerns |
| "I have lots of materials to synthesize" | Method 6: Material integration | Abundant sources, needs organization |

## Best Practices

**For Social Media Content:**
- Focus on relatable experiences and personal insights
- Use conversational tone that feels authentic
- Include concrete examples and data points
- Add clear call-to-actions when appropriate
- Consider platform-specific formats and constraints

**Quality Control:**
- Always maintain user's authentic voice
- Add personal touches that AI cannot generate
- Fact-check claims and verify data
- Ensure content provides genuine value to readers
- Review for flow and coherence

**Common Pitfalls to Avoid:**
- Don't rely solely on AI-generated content
- Avoid generic templates without personalization
- Don't sacrifice authenticity for polish
- Be cautious with controversial claims without proper sourcing
- Remember that AI assists, doesn't replace human judgment

## Emergency Prompts

**When completely stuck:**
```prompt
我想写内容但完全不知道怎么开始，感觉自己没什么可写的。你能通过一些问题帮我挖掘一下自己经历中有价值的故事或观点吗？
```

**When content feels bland:**
```prompt
我写的这篇文章感觉很平淡，没有亮点。你能帮我看看哪些地方可以加入更有趣的个人经历或者更独特的观点吗？
```

**When struggling with structure:**
```prompt
我有很多想法但写出来很乱。你能帮我把这些想法整理成一个清晰的逻辑结构吗？
```