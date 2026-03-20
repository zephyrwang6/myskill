---
name: ffmpeg-usage
description: "基于Ffmpeg和第三方API的音视频处理，包括，格式转换、视频拼接、合并、尺寸调整、压缩、GIF 制作、音频提取、字幕处理、社交平台优化、文案提取，文案转录等"
---
# ffmpeg 使用指南

## 概述

本技能提供基于 ffmpeg 的全面音视频处理能力，包括经过实战验证的命令和工作流，适用于常见多媒体任务、平台特定优化，以及质量与文件大小管理的最佳实践。

**版本：** 1.0.0
**要求：** ffmpeg >= 4.0，ffprobe（可选但推荐）

当用户提及视频或音频处理任务、格式转换、社交媒体优化或多媒体编辑时，Claude 应使用本技能。

## 适用场景

当用户需要以下操作时使用本技能：
- 视频格式转换（MP4、WebM、MOV 等）
- 分辨率缩放或宽高比调整
- 从视频创建 GIF
- 音频提取或格式转换
- 视频编辑（裁剪、合并、变速、旋转）
- 字幕处理（硬字幕、软字幕、提取字幕）
- 视频压缩或优化
- 平台特定格式化（YouTube、Instagram、TikTok、Twitter）
- 缩略图或帧提取
- 批量处理音视频文件

## 前置条件

使用本技能前，请确保已安装 ffmpeg：

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows（使用 Chocolatey）
choco install ffmpeg
```

验证安装：
```bash
ffmpeg -version
```

## 支持的操作

### 1. 格式转换

在不同视频格式之间转换，并使用优化设置。

**MP4 转 WebM：**
```bash
ffmpeg -i input.mp4 -c:v libvpx-vp9 -crf 30 -b:v 0 -c:a libopus output.webm
```

**MOV 转 MP4：**
```bash
ffmpeg -i input.mov -c:v libx264 -c:a aac -strict experimental output.mp4
```

**任意格式转 MP4（通用兼容）：**
```bash
ffmpeg -i input.* -c:v libx264 -preset medium -crf 23 -c:a aac -b:a 128k output.mp4
```

### 2. 分辨率调整

调整视频尺寸同时保持宽高比。

**缩放到 720p：**
```bash
ffmpeg -i input.mp4 -vf scale=-1:720 -c:a copy output_720p.mp4
```

**缩放到 1080p：**
```bash
ffmpeg -i input.mp4 -vf scale=-1:1080 -c:a copy output_1080p.mp4
```

**缩放到指定宽度（高度自适应）：**
```bash
ffmpeg -i input.mp4 -vf scale=1280:-1 -c:a copy output.mp4
```

**带填充缩放（黑边填充/信箱模式）：**
```bash
ffmpeg -i input.mp4 -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" output.mp4
```

### 3. GIF 制作

从视频创建高质量 GIF，并优化文件大小。

**基本 GIF（10 帧/秒）：**
```bash
ffmpeg -i input.mp4 -vf "fps=10,scale=480:-1:flags=lanczos" output.gif
```

**高质量 GIF（使用调色板）：**
```bash
# 生成调色板
ffmpeg -i input.mp4 -vf "fps=10,scale=480:-1:flags=lanczos,palettegen" palette.png

# 使用调色板创建 GIF
ffmpeg -i input.mp4 -i palette.png -filter_complex "fps=10,scale=480:-1:flags=lanczos[x];[x][1:v]paletteuse" output.gif
```

**从指定时间范围创建 GIF：**
```bash
ffmpeg -ss 00:00:10 -t 5 -i input.mp4 -vf "fps=10,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" output.gif
```

### 4. 音频操作

提取、转换和处理音频流。

**提取音频为 MP3：**
```bash
ffmpeg -i input.mp4 -vn -acodec libmp3lame -q:a 2 output.mp3
```

**提取音频为 WAV：**
```bash
ffmpeg -i input.mp4 -vn -acodec pcm_s16le -ar 44100 -ac 2 output.wav
```

**转换音频格式：**
```bash
ffmpeg -i input.wav -c:a aac -b:a 192k output.m4a
```

**添加背景音乐：**
```bash
ffmpeg -i video.mp4 -i music.mp3 -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest output.mp4
```

**混合音频（叠加）：**
```bash
ffmpeg -i video.mp4 -i music.mp3 -filter_complex "[0:a][1:a]amix=inputs=2:duration=first" -c:v copy output.mp4
```

### 5. 视频编辑

裁剪、拼接和修改视频。

**裁剪视频：**
```bash
# 从第 10 秒到第 30 秒
ffmpeg -i input.mp4 -ss 00:00:10 -to 00:00:30 -c copy output.mp4

# 基于时长（从第 5 秒开始，截取 10 秒）
ffmpeg -i input.mp4 -ss 00:00:05 -t 10 -c copy output.mp4
```

**拼接视频：**

根据格式和兼容性选择方法：

**方法一：Concat 协议（推荐——无需临时文件）**
```bash
# 适用于 MPEG 格式：.ts、.mpg、.mpeg、.mp3、.aac 等
# 直接拼接，无需创建列表文件
ffmpeg -i "concat:file1.mp3|file2.mp3|file3.mp3" -c copy output.mp3
ffmpeg -i "concat:video1.ts|video2.ts|video3.ts" -c copy output.ts

# 支持格式：TS、MPEG-1、MPEG-2、MP3、AAC
# 不支持：MP4、MOV、MKV（请使用方法二）
```

**方法二：Concat 分离器（适用于 MP4、MOV、MKV）**
```bash
# 使用进程替换避免临时文件
ffmpeg -f concat -safe 0 -i <(printf "file '%s'\n" video1.mp4 video2.mp4 video3.mp4) -c copy output.mp4

# 如果 shell 不支持进程替换：
printf "file '%s'\n" video1.mp4 video2.mp4 video3.mp4 > list.txt
ffmpeg -f concat -safe 0 -i list.txt -c copy output.mp4
rm list.txt
```

**方法三：Concat 滤镜（可接受重新编码时使用）**
```bash
# 当视频编码/分辨率不同时使用
ffmpeg -i video1.mp4 -i video2.mp4 -i video3.mp4 \
  -filter_complex "[0:v][0:a][1:v][1:a][2:v][2:a]concat=n=3:v=1:a=1[v][a]" \
  -map "[v]" -map "[a]" output.mp4
```

**格式选择指南：**
- `.mp3`、`.aac`、`.ts`、`.mpg`、`.mpeg` → 使用 concat 协议（方法一）
- `.mp4`、`.mov`、`.mkv` → 使用 concat 分离器（方法二）
- 不同编码/分辨率 → 使用 concat 滤镜（方法三）

**加速/减速：**
```bash
# 2 倍速
ffmpeg -i input.mp4 -filter:v "setpts=0.5*PTS" -an output.mp4

# 0.5 倍速（慢动作）
ffmpeg -i input.mp4 -filter:v "setpts=2.0*PTS" output.mp4
```

**旋转视频：**
```bash
# 顺时针旋转 90 度
ffmpeg -i input.mp4 -vf "transpose=1" output.mp4

# 旋转 180 度
ffmpeg -i input.mp4 -vf "transpose=2,transpose=2" output.mp4
```

### 6. 字幕处理

添加、提取或烧录字幕。

**烧录字幕到视频（硬字幕）：**
```bash
ffmpeg -i input.mp4 -vf subtitles=subtitles.srt output.mp4
```

**添加软字幕：**
```bash
ffmpeg -i input.mp4 -i subtitles.srt -c copy -c:s mov_text output.mp4
```

**提取字幕：**
```bash
ffmpeg -i input.mp4 -map 0:s:0 subtitles.srt
```

### 7. 缩略图提取

从视频中提取帧作为图片。

**在指定时间提取单帧：**
```bash
ffmpeg -i input.mp4 -ss 00:00:05 -vframes 1 thumbnail.jpg
```

**提取多张缩略图：**
```bash
# 每 10 秒提取一帧
ffmpeg -i input.mp4 -vf fps=1/10 thumb%04d.jpg

# 提取前 10 帧
ffmpeg -i input.mp4 -vframes 10 frame%04d.png
```

### 8. 压缩与优化

在保持质量的同时减小文件大小。

**视频压缩（均衡模式）：**
```bash
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset medium -c:a aac -b:a 128k output.mp4
```

**高压缩（更小文件）：**
```bash
ffmpeg -i input.mp4 -c:v libx264 -crf 28 -preset veryslow -c:a aac -b:a 96k output.mp4
```

**Web 优化压缩：**
```bash
ffmpeg -i input.mp4 -c:v libx264 -preset medium -crf 23 -movflags +faststart -c:a aac -b:a 128k output.mp4
```

## 平台特定预设

### YouTube 优化
```bash
ffmpeg -i input.mp4 \
  -c:v libx264 -preset slow -crf 18 \
  -c:a aac -b:a 192k \
  -pix_fmt yuv420p \
  -movflags +faststart \
  youtube.mp4
```

### Instagram 快拍（9:16）
```bash
ffmpeg -i input.mp4 \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" \
  -c:v libx264 -preset medium -crf 23 \
  -c:a aac -b:a 128k \
  -t 15 \
  instagram_story.mp4
```

### Twitter/X（16:9，最长 2 分 20 秒）
```bash
ffmpeg -i input.mp4 \
  -vf scale=1280:720 \
  -c:v libx264 -preset medium -crf 23 \
  -c:a aac -b:a 128k \
  -t 140 \
  twitter.mp4
```

### TikTok（9:16）
```bash
ffmpeg -i input.mp4 \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" \
  -c:v libx264 -preset medium -crf 23 \
  -c:a aac -b:a 128k \
  -t 60 \
  tiktok.mp4
```

## 常见用例

### 屏幕录制优化
```bash
# 减小屏幕录制文件大小
ffmpeg -i screen_recording.mov \
  -c:v libx264 -preset medium -crf 23 \
  -vf "scale=1920:-1" \
  -c:a aac -b:a 128k \
  optimized.mp4
```

### 批量转换
```bash
# 将所有 MOV 文件转换为 MP4
for i in *.mov; do
  ffmpeg -i "$i" -c:v libx264 -crf 23 -c:a aac "${i%.mov}.mp4"
done
```

### 从图片创建视频
```bash
# 从图片序列创建
ffmpeg -framerate 30 -pattern_type glob -i '*.jpg' \
  -c:v libx264 -pix_fmt yuv420p \
  output.mp4

# 单张图片转视频（5 秒）
ffmpeg -loop 1 -i image.jpg -c:v libx264 -t 5 -pix_fmt yuv420p output.mp4
```

## 最佳实践

1. **始终先检查输入文件：**
   ```bash
   ffmpeg -i input.mp4
   # 或使用 ffprobe 获取详细信息
   ffprobe -v quiet -print_format json -show_format -show_streams input.mp4
   ```

2. **尽可能使用 `-c copy` 避免重新编码：**
   ```bash
   ffmpeg -i input.mp4 -ss 00:01:00 -t 30 -c copy output.mp4
   ```

3. **处理前用 `-t` 参数预览效果：**
   ```bash
   # 先测试前 10 秒
   ffmpeg -i input.mp4 -t 10 [其他参数] test.mp4
   ```

4. **使用合适的 CRF 值：**
   - 18 = 视觉无损
   - 23 = 高质量（默认值）
   - 28 = 可接受质量，文件更小
   - 范围：0（无损）到 51（最差质量）

5. **为 Web 视频添加 `-movflags +faststart`：**
   - 启用渐进式播放
   - 将元数据移至文件开头

## 错误处理

使用本技能时，请始终：

1. 验证输入文件存在且可读
2. 处理前检查 ffmpeg 是否已安装
3. 验证输出路径可写
4. 使用适当的提示信息优雅处理错误
5. 处理大文件时显示进度

## Claude 使用指南

当用户请求音视频处理时：

1. **识别任务类型**
2. **从本技能中选择合适的命令**
3. **验证前置条件**（ffmpeg 已安装、输入文件存在）
4. **执行前说明命令的作用**
5. **执行命令**并进行错误处理
6. **验证输出**是否成功创建
7. **提供优化建议**（如适用）

对于复杂工作流，应分步骤执行并逐一说明。

**视频拼接注意事项：** 尽可能使用 printf 配合进程替换来避免临时文件（参见拼接部分的方法二）。仅在必要时使用临时 list.txt 文件。

## 示例

**用户：**"把这个 MOV 文件转成 MP4"
**响应：** 使用 H.264 编码的 MOV 转 MP4 命令

**用户：**"从这个视频做一个 GIF，从第 10 秒开始只要 5 秒"
**响应：** 使用带时间范围的 GIF 创建命令

**用户：**"我需要把这个 4K 视频缩小到 1080p 用于网页"
**响应：** 结合分辨率缩放和 Web 优化预设

**用户：**"提取音频为 MP3"
**响应：** 使用 MP3 编码的音频提取命令

## 参考资料

- FFmpeg 官方文档：https://ffmpeg.org/documentation.html
- FFmpeg Wiki：https://trac.ffmpeg.org/wiki
- 支持的编解码器：https://ffmpeg.org/ffmpeg-codecs.html
- 滤镜文档：https://ffmpeg.org/ffmpeg-filters.html


文案提取和转录功能，当涉及到转录和文案提取功能的时候，参考下面文档：


# Voice Model API (本地语音转录)

应用启动后自动在 `http://127.0.0.1:18923` 开启本地 HTTP 接口，供 Claude Skill 等外部调用方使用。

## 接口列表

### 1. 查询模型状态

```
GET /v1/audio/models/status
```

**响应示例：**

```json
{
  "installed": true,
  "modelDir": "/Users/xxx/.newmax/models/sensevoice-small",
  "modelSize": 239549735
}
```

```json
{
  "installed": false,
  "modelDir": "/Users/xxx/.newmax/models/sensevoice-small",
  "missingFiles": ["model.int8.onnx", "tokens.txt"]
}
```

### 2. 音频转录

```
POST /v1/audio/transcriptions
Content-Type: application/json
```

**请求参数：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| audioPath | string | 是 | 音频文件的本地绝对路径 |
| language | string | 否 | 语言代码（如 `zh`, `en`, `ja`），留空自动检测 |

**请求示例：**

```json
{
  "audioPath": "/Users/xxx/Downloads/interview.mp3",
  "language": "zh"
}
```

**成功响应（200）：**

```json
{
  "success": true,
  "text": "第一段转录文字\n第二段转录文字\n第三段转录文字"
}
```

**失败响应（400/500）：**

```json
{
  "success": false,
  "error": "模型未安装，请先下载模型"
}
```

## 使用说明

- 端口固定为 `18923`，仅监听 `127.0.0.1`（本机访问）
- 支持格式：WAV / MP3 / FLAC / M4A / OGG / AAC（非 WAV 格式需系统安装 ffmpeg）
- 长音频自动按 30 秒分段转录，结果以换行符拼接
- 模型需在设置 → 语音模型中先下载（约 239 MB），否则转录接口会返回未安装错误
- 使用 SenseVoice Small 模型，支持中英日韩粤等 50+ 语种

## curl 快速测试

```bash
# 检查模型是否已安装
curl http://127.0.0.1:18923/v1/audio/models/status

# 转录音频文件
curl -X POST http://127.0.0.1:18923/v1/audio/transcriptions \
  -H 'Content-Type: application/json' \
  -d '{"audioPath": "/path/to/audio.mp3"}'
```

## 在 Claude Skill 中调用

```bash
# 在 skill 脚本中调用转录 API
result=$(curl -s -X POST http://127.0.0.1:18923/v1/audio/transcriptions \
  -H 'Content-Type: application/json' \
  -d "{\"audioPath\": \"$AUDIO_FILE\"}")

echo "$result" | jq -r '.text'
```

