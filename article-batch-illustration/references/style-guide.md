# 文章配图风格指南与提示词模板

## 全局风格指令模板

在生成提示词前，必须先根据文章主题生成一个全局风格指令块：

```
STYLE INSTRUCTIONS:
- 整体风格: [根据文章主题选择风格1或风格2]
- 色彩方案: [白底为主，辅以主题相关的点缀色]
- 比例: 16:9 横版
- 分辨率: 2K
- 文字量: 极少，仅保留核心关键词
- 视觉语言: 逻辑图、流程图、概念图为主
- 一致性: 所有图片保持统一的线条粗细、留白比例、排版网格
```

## 风格 1：简约手绘风格

**特征**: 黑色线条、白底、手绘质感逻辑图

**提示词前缀**:
```
A clean minimalist hand-drawn style illustration on a pure white background.
Black ink line art with slight hand-drawn texture. No photography, no gradients.
Simple geometric shapes connected by clean lines to form a logic diagram.
Aspect ratio 16:9. Minimal text, only 1-3 keywords. ALL text and labels in the
image MUST be written in Chinese (Simplified Chinese characters, 中文), using a
clean sans-serif Chinese font. Technical terms and abbreviations (e.g. AI, API,
LLM, RAG) may remain in English. All other text must be Chinese.
```

**适用场景**: 概念解释、流程说明、对比分析、分类说明

**视觉元素**:
- 手绘风格圆形/方框节点
- 简洁的箭头连线
- 虚线表示隐含关系
- 图标式简笔画辅助说明

## 风格 2：建筑蓝图编辑风格

**特征**: 精致极简、高端技术期刊感、精准清晰

**提示词前缀**:
```
A clean, refined, minimalist editorial-style diagram inspired by architectural
blueprints and premium tech journals. Pure white background with subtle light
gray grid lines. Precise thin lines in dark charcoal (#333333) with accent
color highlights. Professional typography, geometric precision. Intellectual
elegance. Aspect ratio 16:9. Minimal text, only 1-3 keywords. ALL text and
labels in the image MUST be written in Chinese (Simplified Chinese characters,
中文), using a refined sans-serif Chinese font. Technical terms and abbreviations
(e.g. AI, API, LLM, RAG) may remain in English. All other text must be Chinese.
```

**适用场景**: 系统架构、数据流、技术概念、专业分析

**视觉元素**:
- 精确的几何线条
- 细微的网格底纹
- 层次分明的灰度
- 点缀色标记重点
- 等距排列的模块

## 图片类型与提示词结构

### 概念解释图
```
[风格前缀] The diagram illustrates the concept of "[核心概念]".
Central element labeled "中文核心词". Connected to [N] surrounding elements
labeled "要素A", "要素B", "要素C". Clean arrows show relationships.
ALL text, labels, and annotations MUST be primarily in Chinese (Simplified Chinese, 中文). Use clean Chinese font. Technical terms and abbreviations (e.g. AI, API, LLM) may remain in English.
```

### 流程/步骤图
```
[风格前缀] A horizontal flow diagram showing [N] steps of a process.
Each step is represented by [形状] with a brief icon inside.
Steps flow left to right connected by arrows.
Step labels: "步骤一名称" → "步骤二名称" → "步骤三名称"
ALL text, labels, and annotations MUST be primarily in Chinese (Simplified Chinese, 中文). Use clean Chinese font. Technical terms and abbreviations (e.g. AI, API, LLM) may remain in English.
```

### 对比/矩阵图
```
[风格前缀] A 2x2 matrix diagram. Horizontal axis labeled "维度A中文",
vertical axis labeled "维度B中文". Four quadrants contain simple icons
with labels "象限1中文", "象限2中文", "象限3中文", "象限4中文".
ALL text, labels, and annotations MUST be primarily in Chinese (Simplified Chinese, 中文). Use clean Chinese font. Technical terms and abbreviations (e.g. AI, API, LLM) may remain in English.
```

### 层次/架构图
```
[风格前缀] A layered architecture diagram with [N] horizontal layers.
Top layer labeled "顶层中文名", middle layer labeled "中层中文名",
bottom layer labeled "底层中文名". Each layer contains [N] modules shown
as rounded rectangles with Chinese labels.
ALL text, labels, and annotations MUST be primarily in Chinese (Simplified Chinese, 中文). Use clean Chinese font. Technical terms and abbreviations (e.g. AI, API, LLM) may remain in English.
```

### 关系/网络图
```
[风格前缀] A network diagram showing relationships between [N] key concepts.
Central node labeled "核心中文词" connects to surrounding nodes labeled
"概念A", "概念B", "概念C". Line thickness indicates relationship strength.
ALL text, labels, and annotations MUST be primarily in Chinese (Simplified Chinese, 中文). Use clean Chinese font. Technical terms and abbreviations (e.g. AI, API, LLM) may remain in English.
```

## 提示词优化规则

1. **叙述性描述** > 关键词堆砌（Gemini 理解完整语句更好）
2. **明确指定**白色背景、16:9比例、极少文字
3. **具体化**视觉元素（箭头方向、节点形状、布局方式）
4. **中文为主** - 每个提示词末尾必须包含：`ALL text, labels, and annotations MUST be primarily in Chinese (Simplified Chinese, 中文). Technical terms (e.g. AI, API, LLM) may remain in English.`
5. **中文标签**需用引号包裹，限制在1-3个关键词，直接写中文（如 "数据采集"）
6. **避免**复杂场景、多色渐变、真实照片元素
7. **一致性**：同一篇文章的所有配图使用相同风格前缀
