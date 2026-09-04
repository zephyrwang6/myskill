#!/usr/bin/env python3
"""
Image Generator - 调用 Google AI Studio 或 Atlas Cloud API 生成图片

Usage:
    python3 generate_image.py --prompt "..." --output /path/to/output.png [--api-key KEY] [--aspect-ratio 16:9] [--resolution 2K]
    python3 generate_image.py --provider atlas --prompt "..." --output /path/to/output.png

Env:
    GEMINI_API_KEY     - Google AI Studio key（默认 provider，也可用 --api-key 传）
    ATLASCLOUD_API_KEY - Atlas Cloud key（--provider atlas 时使用）
"""

import argparse
import base64
import json
import os
import sys
import time
import urllib.request
import urllib.error

DEFAULT_API_URL = "https://generativelanguage.googleapis.com"
DEFAULT_MODEL = "gemini-3-pro-image-preview"
DEFAULT_ASPECT_RATIO = "16:9"
DEFAULT_RESOLUTION = "2K"
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# --- Atlas Cloud（可选 provider，Gemini 官方 API 不可直连时用）---
ATLAS_API_URL = "https://api.atlascloud.ai/api/v1/model"
# seedream-v4 精确遵守请求尺寸，所以能保住本 Skill 的 2K 默认值
ATLAS_DEFAULT_MODEL = "bytedance/seedream-v4"
ATLAS_POLL_INTERVAL = 5
ATLAS_POLL_TIMEOUT = 300
# api.atlascloud.ai 会用 403(error code 1010) 拒掉 urllib 的默认 User-Agent
ATLAS_USER_AGENT = "logo-batch-generator/1"
# 长边像素：Gemini 的 1K/2K/4K 在 Atlas 侧没有对应字段，换算成具体尺寸
ATLAS_LONG_EDGE = {"1K": 1024, "2K": 2048, "4K": 4096}


def atlas_size(aspect_ratio, resolution):
    """把 Gemini 的 (aspect_ratio, resolution) 换算成 Atlas 的 宽*高。"""
    long_edge = ATLAS_LONG_EDGE.get(resolution.upper())
    if long_edge is None:
        raise ValueError(f"unsupported resolution: {resolution}")
    try:
        w_ratio, h_ratio = (float(v) for v in aspect_ratio.split(":", 1))
        if w_ratio <= 0 or h_ratio <= 0:
            raise ValueError
    except ValueError:
        raise ValueError(f"unsupported aspect ratio: {aspect_ratio}")
    if w_ratio == h_ratio:
        return f"{long_edge}*{long_edge}"
    short_edge = int(round(long_edge * min(w_ratio, h_ratio) / max(w_ratio, h_ratio) / 16)) * 16
    return f"{long_edge}*{short_edge}" if w_ratio > h_ratio else f"{short_edge}*{long_edge}"


def _fix_extension(output_path, content):
    """按图片真实字节修正扩展名，避免把 JPEG 写进 .png。"""
    if content[:3] == b"\xff\xd8\xff":
        actual = ".jpg"
    elif content[:8] == b"\x89PNG\r\n\x1a\n":
        actual = ".png"
    elif content[:4] == b"RIFF" and content[8:12] == b"WEBP":
        actual = ".webp"
    else:
        return output_path
    root, ext = os.path.splitext(output_path)
    if ext.lower() == actual or (actual == ".jpg" and ext.lower() == ".jpeg"):
        return output_path
    fixed = root + actual
    print(f"[INFO] Provider returned {actual[1:].upper()}, saving as {os.path.basename(fixed)}")
    return fixed


def _atlas_request(url, api_key, payload=None):
    headers = {"Authorization": f"Bearer {api_key}", "User-Agent": ATLAS_USER_AGENT}
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers=headers, method="POST" if payload is not None else "GET"
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def generate_image_atlas(prompt, output_path, api_key, api_url=ATLAS_API_URL,
                         model=ATLAS_DEFAULT_MODEL, aspect_ratio=DEFAULT_ASPECT_RATIO,
                         resolution=DEFAULT_RESOLUTION):
    """通过 Atlas Cloud 生成图片：提交任务 -> 轮询 -> 下载。成功返回实际落盘路径。"""
    body = {"model": model, "prompt": prompt}
    if "nano-banana" in model:
        # 实测：nano-banana 系列忽略 size，但认 aspect_ratio；分辨率由模型决定
        body["aspect_ratio"] = aspect_ratio
        if resolution.upper() != "1K":
            print(f"[WARN] {model} 不支持 {resolution}，返回模型默认分辨率", file=sys.stderr)
    else:
        body["size"] = atlas_size(aspect_ratio, resolution)

    for attempt in range(MAX_RETRIES):
        try:
            submitted = _atlas_request(f"{api_url}/generateImage", api_key, body)
            prediction_id = (submitted.get("data") or {}).get("id")
            if not prediction_id:
                print(f"[WARN] No prediction id: {json.dumps(submitted)[:200]}", file=sys.stderr)
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                return None

            deadline = time.monotonic() + ATLAS_POLL_TIMEOUT
            while True:
                time.sleep(ATLAS_POLL_INTERVAL)
                result = _atlas_request(f"{api_url}/prediction/{prediction_id}", api_key)
                data = result.get("data") or {}
                status = data.get("status")
                if status == "completed":
                    outputs = data.get("outputs") or []
                    if not outputs:
                        print("[WARN] No outputs in completed prediction", file=sys.stderr)
                        return None
                    req = urllib.request.Request(
                        outputs[0], headers={"User-Agent": ATLAS_USER_AGENT}
                    )
                    with urllib.request.urlopen(req, timeout=180) as resp:
                        img_data = resp.read()
                    target = _fix_extension(output_path, img_data)
                    os.makedirs(os.path.dirname(target), exist_ok=True)
                    with open(target, "wb") as f:
                        f.write(img_data)
                    print(f"[OK] Image saved: {target} ({len(img_data)} bytes)")
                    return target
                if status == "failed":
                    print(f"[ERROR] Atlas failed: {data.get('error')}", file=sys.stderr)
                    return None
                if time.monotonic() > deadline:
                    print(f"[ERROR] Atlas prediction {prediction_id} timed out", file=sys.stderr)
                    return None

        except urllib.error.HTTPError as e:
            body_text = e.read().decode("utf-8", errors="replace")
            print(f"[ERROR] HTTP {e.code}: {body_text[:500]}", file=sys.stderr)
            if e.code == 429 or e.code >= 500:
                if attempt < MAX_RETRIES - 1:
                    wait = RETRY_DELAY * (attempt + 1)
                    print(f"[INFO] Retrying in {wait}s...", file=sys.stderr)
                    time.sleep(wait)
                    continue
            return None
        except Exception as e:
            print(f"[ERROR] {e}", file=sys.stderr)
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
            return None

    return None


def generate_image(prompt, output_path, api_key, api_url=DEFAULT_API_URL,
                   model=DEFAULT_MODEL, aspect_ratio=DEFAULT_ASPECT_RATIO,
                   resolution=DEFAULT_RESOLUTION):
    """Call Gemini API to generate an image from prompt and save to output_path."""
    endpoint = f"{api_url}/v1beta/models/{model}:generateContent"

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {
                "aspectRatio": aspect_ratio,
                "imageSize": resolution
            }
        }
    }

    headers = {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json"
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(endpoint, data=data, headers=headers, method="POST")

    for attempt in range(MAX_RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read().decode("utf-8"))

            # Extract image from response
            candidates = result.get("candidates", [])
            if not candidates:
                print(f"[WARN] No candidates in response", file=sys.stderr)
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                return None

            content = candidates[0].get("content", {})
            parts = content.get("parts", [])

            text_response = None
            image_saved = False

            for part in parts:
                if "text" in part and not part.get("thought"):
                    text_response = part["text"]
                elif "inlineData" in part and not part.get("thought"):
                    inline = part["inlineData"]
                    mime_type = inline.get("mimeType", "image/png")
                    img_data = base64.b64decode(inline["data"])

                    # Ensure output directory exists
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)

                    with open(output_path, "wb") as f:
                        f.write(img_data)

                    image_saved = True
                    print(f"[OK] Image saved: {output_path} ({len(img_data)} bytes)")

            if text_response:
                print(f"[INFO] Model text: {text_response[:200]}")

            if image_saved:
                return output_path
            else:
                print(f"[WARN] No image data in response (attempt {attempt+1}/{MAX_RETRIES})", file=sys.stderr)
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)

        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            print(f"[ERROR] HTTP {e.code}: {body[:500]}", file=sys.stderr)
            if e.code == 429 or e.code >= 500:
                if attempt < MAX_RETRIES - 1:
                    wait = RETRY_DELAY * (attempt + 1)
                    print(f"[INFO] Retrying in {wait}s...", file=sys.stderr)
                    time.sleep(wait)
                    continue
            return None
        except Exception as e:
            print(f"[ERROR] {e}", file=sys.stderr)
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
            return None

    return None


def main():
    parser = argparse.ArgumentParser(description="Generate image via Gemini or Atlas Cloud API")
    parser.add_argument("--prompt", "-p", required=True, help="Image generation prompt")
    parser.add_argument("--output", "-o", required=True, help="Output file path")
    parser.add_argument("--provider", choices=["gemini", "atlas"], default="gemini",
                        help="gemini（默认，Google 官方 API）或 atlas（Atlas Cloud）")
    parser.add_argument("--api-key", default="",
                        help="API key（默认读 GEMINI_API_KEY / atlas 读 ATLASCLOUD_API_KEY）")
    parser.add_argument("--api-url", default="", help="API base URL（默认按 provider 取）")
    parser.add_argument("--model", default="", help="Model name（默认按 provider 取）")
    parser.add_argument("--aspect-ratio", default=DEFAULT_ASPECT_RATIO,
                        help="Aspect ratio: 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9")
    parser.add_argument("--resolution", default=DEFAULT_RESOLUTION,
                        help="Resolution: 1K, 2K, 4K")
    args = parser.parse_args()

    key_var = "ATLASCLOUD_API_KEY" if args.provider == "atlas" else "GEMINI_API_KEY"
    api_key = args.api_key or os.environ.get(key_var, "")
    if not api_key:
        print(f"[ERROR] No API key provided. Use --api-key or set {key_var}.", file=sys.stderr)
        sys.exit(1)

    if args.provider == "atlas":
        result = generate_image_atlas(
            prompt=args.prompt,
            output_path=args.output,
            api_key=api_key,
            api_url=args.api_url or ATLAS_API_URL,
            model=args.model or ATLAS_DEFAULT_MODEL,
            aspect_ratio=args.aspect_ratio,
            resolution=args.resolution
        )
    else:
        result = generate_image(
            prompt=args.prompt,
            output_path=args.output,
            api_key=api_key,
            api_url=args.api_url or DEFAULT_API_URL,
            model=args.model or DEFAULT_MODEL,
            aspect_ratio=args.aspect_ratio,
            resolution=args.resolution
        )

    if result:
        print(f"[OK] Done: {result}")
        sys.exit(0)
    else:
        print("[ERROR] Failed to generate image.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
