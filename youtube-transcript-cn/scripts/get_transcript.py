#!/usr/bin/env python3
"""
YouTube Transcript Extractor
Extract subtitles/transcripts from YouTube videos and output in Chinese.
Requires: pip install youtube-transcript-api
"""

import sys
import re
import json
import argparse
import subprocess

def ensure_dependency():
    """Ensure youtube-transcript-api is installed."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        return YouTubeTranscriptApi
    except ImportError:
        print("Installing youtube-transcript-api...", file=sys.stderr)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "youtube-transcript-api", "-q"])
        from youtube_transcript_api import YouTubeTranscriptApi
        return YouTubeTranscriptApi

def extract_video_id(url: str) -> str:
    """Extract video ID from various YouTube URL formats."""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Cannot extract video ID from: {url}")

def format_timestamp(seconds: float) -> str:
    """Convert seconds to HH:MM:SS format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"

def get_transcript(video_id: str, lang_priority: list = None):
    """Fetch transcript using youtube-transcript-api."""
    YouTubeTranscriptApi = ensure_dependency()

    if lang_priority is None:
        lang_priority = ['zh-Hans', 'zh-Hant', 'zh', 'zh-CN', 'zh-TW', 'en', 'en-US', 'en-GB']

    try:
        # Create API instance
        ytt_api = YouTubeTranscriptApi()

        # List available transcripts
        transcript_list = ytt_api.list(video_id)

        # Try to find transcript in preferred language order
        transcript = None
        used_lang = None
        is_generated = False

        # First try manual transcripts
        for lang in lang_priority:
            try:
                transcript = transcript_list.find_transcript([lang])
                used_lang = lang
                is_generated = transcript.is_generated
                break
            except:
                continue

        # Then try auto-generated
        if not transcript:
            for lang in lang_priority:
                try:
                    transcript = transcript_list.find_generated_transcript([lang])
                    used_lang = lang
                    is_generated = True
                    break
                except:
                    continue

        # Fallback to any available
        if not transcript:
            try:
                for t in transcript_list:
                    transcript = t
                    used_lang = t.language_code
                    is_generated = t.is_generated
                    break
            except:
                pass

        if not transcript:
            return {"error": "No transcript available", "segments": [], "language": None}

        segments = transcript.fetch()
        # Convert FetchedTranscript to list of dicts
        segment_list = [{"start": s.start, "duration": s.duration, "text": s.text} for s in segments]

        return {
            "segments": segment_list,
            "language": used_lang,
            "is_generated": is_generated
        }
    except Exception as e:
        return {"error": str(e), "segments": [], "language": None}

def format_output(video_id: str, transcript_data: dict, output_format: str = "markdown",
                  include_timestamps: bool = False) -> str:
    """Format the transcript output."""
    segments = transcript_data.get("segments", [])
    error = transcript_data.get("error")

    lines = []

    if output_format == "markdown":
        lines.append(f"# YouTube 视频文字稿")
        lines.append("")
        lines.append(f"- **Video ID**: `{video_id}`")
        lines.append(f"- **链接**: https://www.youtube.com/watch?v={video_id}")
        if transcript_data.get("language"):
            lines.append(f"- **语言**: {transcript_data['language']}")
        if transcript_data.get("is_generated"):
            lines.append("- **字幕类型**: 自动生成")
        lines.append("")
        lines.append("---")
        lines.append("")

    if error:
        lines.append(f"❌ 错误: {error}")
        return "\n".join(lines)

    if not segments:
        lines.append("❌ 没有找到字幕内容")
        return "\n".join(lines)

    if output_format == "markdown":
        lines.append("## 文字稿")
        lines.append("")

    if include_timestamps:
        for seg in segments:
            ts = format_timestamp(seg.get("start", 0))
            text = seg.get("text", "").strip()
            lines.append(f"**[{ts}]** {text}")
            lines.append("")
    else:
        # Merge into paragraphs
        current_paragraph = []
        paragraph_start = 0

        for i, seg in enumerate(segments):
            text = seg.get("text", "").strip()
            start = seg.get("start", 0)

            # New paragraph every ~60 seconds or on long pause
            if current_paragraph:
                if start - paragraph_start > 60:
                    lines.append(" ".join(current_paragraph))
                    lines.append("")
                    current_paragraph = []
                    paragraph_start = start
            else:
                paragraph_start = start

            if text:
                current_paragraph.append(text)

        if current_paragraph:
            lines.append(" ".join(current_paragraph))

    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Extract YouTube video transcripts")
    parser.add_argument("url", help="YouTube video URL or video ID")
    parser.add_argument("-f", "--format", choices=["text", "markdown", "json"],
                        default="markdown", help="Output format (default: markdown)")
    parser.add_argument("-t", "--timestamps", action="store_true",
                        help="Include timestamps in output")
    parser.add_argument("-l", "--lang", default="zh,en",
                        help="Preferred languages, comma-separated (default: zh,en)")
    parser.add_argument("-o", "--output", help="Output file path (default: stdout)")

    args = parser.parse_args()

    try:
        video_id = extract_video_id(args.url)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Parse language preference
    lang_priority = []
    for lang in args.lang.split(","):
        lang = lang.strip()
        if lang == "zh":
            lang_priority.extend(['zh-Hans', 'zh-Hant', 'zh', 'zh-CN', 'zh-TW'])
        elif lang == "en":
            lang_priority.extend(['en', 'en-US', 'en-GB'])
        else:
            lang_priority.append(lang)

    # Get transcript
    transcript_data = get_transcript(video_id, lang_priority)

    # Format output
    if args.format == "json":
        output = json.dumps({
            "video_id": video_id,
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "transcript": transcript_data
        }, ensure_ascii=False, indent=2)
    else:
        output = format_output(video_id, transcript_data, args.format, args.timestamps)

    # Write output
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"✅ Saved to: {args.output}", file=sys.stderr)
    else:
        print(output)

if __name__ == "__main__":
    main()
