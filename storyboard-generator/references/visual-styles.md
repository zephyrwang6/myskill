# 分镜故事板视觉风格指南

## 8 种故事板风格

### 风格 1：赛博朋克漫画 (Cyberpunk Comic)

**特征**: 高对比、霓虹色、暗色调背景、分格漫画构图、科幻感
**适用故事**: 科技主题、AI 叙事、未来世界、赛博空间
**情绪**: 酷、前卫、紧张感

**风格前缀**:
```
Cyberpunk comic panel style illustration. Dark background with neon blue and pink accent lighting. High contrast, dramatic shadows. Bold comic-style outlines. Cinematic composition. 16:9 aspect ratio.
```

### 风格 2：吉卜力水彩 (Ghibli Watercolor)

**特征**: 柔和水彩质感、温暖色调、细腻光影、宫崎骏式背景、手绘感
**适用故事**: 日常叙事、温馨故事、成长故事、情感表达
**情绪**: 温暖、治愈、怀旧

**风格前缀**:
```
Studio Ghibli inspired watercolor illustration. Soft, warm color palette with gentle light. Delicate hand-painted texture. Dreamy atmospheric perspective. Rich environmental detail. Whimsical and heartwarming mood. 16:9 aspect ratio.
```

### 风格 3：美式动漫 (Motion Graphic / Flat Illustration)

**特征**: 扁平插画、矢量风格、明快配色、几何化人物、现代设计感
**适用故事**: 产品介绍、流程说明、商业故事、教育内容
**情绪**: 清爽、专业、易读

**风格前缀**:
```
Modern flat vector illustration style. Clean geometric shapes, bold solid colors, minimal shading. Simplified character design with clear silhouettes. Bright, contemporary color palette. Infographic-like clarity. 16:9 aspect ratio.
```

### 风格 4：电影分镜 (Cinematic Storyboard)

**特征**: 黑白素描/淡彩、电影镜头构图、透视线、专业分镜手稿感
**适用故事**: 视频脚本、广告分镜、电影叙事、戏剧性故事
**情绪**: 专业、叙事感强、戏剧张力

**风格前缀**:
```
Professional cinematic storyboard sketch. Grayscale pencil drawing with light wash shading. Strong perspective and camera angle indication. Film-like composition with rule of thirds. Motion arrows and camera direction notes. Clean, professional, production-ready feel. 16:9 aspect ratio.
```

### 风格 5：像素艺术 (Pixel Art)

**特征**: 复古像素风、有限色板、8-bit/16-bit 游戏感、怀旧
**适用故事**: 游戏叙事、怀旧故事、极客文化、趣味表达
**情绪**: 趣味、怀旧、极客

**风格前缀**:
```
16-bit pixel art style illustration. Limited color palette with dithering effects. Retro video game aesthetic. Detailed pixel-level craftsmanship. Clean pixel edges, no anti-aliasing. Nostalgic and charming. 16:9 aspect ratio.
```

### 风格 6：中国风水墨 (Chinese Ink Wash)

**特征**: 水墨晕染、留白构图、传统笔触、诗意氛围
**适用故事**: 传统文化、哲理故事、东方叙事、品牌故事
**情绪**: 意境深远、诗意、禅意

**风格前缀**:
```
Traditional Chinese ink wash painting style (水墨画). Black ink on white with subtle gray washes. Generous use of negative space (留白). Flowing brush strokes with varying intensity. Atmospheric perspective with misty elements. Contemplative, poetic mood. 16:9 aspect ratio.
```

### 风格 7：线条漫画 (Ligne Claire / 清线风)

**特征**: 均匀粗线条、扁平上色、无阴影渐变、丁丁历险记风格
**适用故事**: 冒险叙事、儿童故事、幽默故事、品牌IP
**情绪**: 明快、亲切、易读

**风格前缀**:
```
Ligne claire comic style illustration. Uniform bold black outlines, flat colors with no gradients or shadows. Clean, readable compositions inspired by Hergé and Tintin. Simple but expressive character design. Bright, primary color palette. 16:9 aspect ratio.
```

### 风格 8：写实概念艺术 (Realistic Concept Art)

**特征**: 高度写实、数字绘画质感、光影考究、电影级概念设定
**适用故事**: 史诗叙事、科幻世界观、奇幻冒险、重大场景
**情绪**: 震撼、宏大、沉浸

**风格前缀**:
```
Photorealistic digital concept art illustration. Cinematic lighting with volumetric atmosphere. Highly detailed environments and characters. Film production quality. Rich textures and realistic materials. Epic, immersive mood. 16:9 aspect ratio.
```

## 分镜构图规则

### 镜头语言（每个分镜必须指定）

| 镜头 | 英文 | 用途 |
|------|------|------|
| 远景 | Wide/Establishing Shot | 交代环境、气氛、开场 |
| 全景 | Full Shot | 展示人物全身和环境关系 |
| 中景 | Medium Shot | 人物腰部以上，对话场景 |
| 近景 | Close-up | 面部表情、情感表达 |
| 特写 | Extreme Close-up | 关键道具、细节强调 |
| 俯拍 | High Angle / Bird's Eye | 全局感、渺小感 |
| 仰拍 | Low Angle | 权威感、压迫感、高大感 |
| 过肩 | Over-the-shoulder | 对话、互动关系 |

### 叙事节奏模板

典型分镜节奏（以 6-8 帧为例）：

1. **开场** - 远景/全景，交代世界观和环境
2. **引入** - 中景/全景，主角登场，日常状态
3. **转折** - 中景/近景，事件触发、问题出现
4. **发展** - 多种镜头切换，主角行动、过程展现
5. **高潮** - 近景/特写，最有张力的时刻
6. **结局** - 全景/远景，收束、新状态、留白

### 风格一致性指令

每个提示词末尾必须追加风格锚定指令：
```
IMPORTANT: This is panel [N] of [TOTAL] in a storyboard sequence. Maintain exact same art style, color palette, character design, and visual consistency with all other panels. Same character must look identical across all panels.
```

### 中文文字指令

当画面中需要出现文字时：
```
ALL text, signs, labels, and dialogue in the image MUST be primarily in Chinese (Simplified Chinese, 中文). Technical terms and brand names may remain in English.
```

## 故事润色框架

将用户的原始描述润色为分镜脚本时，遵循以下结构：

```
## 故事概要
一句话概括：[故事核心]
情感弧线：[起点情绪] → [转折] → [终点情绪]

## 分镜脚本

### 第 1 帧：[场景标题]
- 镜头：[远景/中景/近景/特写]
- 画面：[具体视觉描述]
- 情绪：[画面传递的情感]
- 文字/对白：[如有]

### 第 2 帧：[场景标题]
...
```
