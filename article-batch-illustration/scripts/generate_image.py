#!/usr/bin/env python3
"""
Gemini Image Generator - 调用 Google AI Studio API 生成图片

Usage:
    python3 generate_image.py --prompt "..." --output /path/to/output.png [--api-key KEY] [--aspect-ratio 16:9] [--resolution 2K] [--style 1|2]

Env:
    GEMINI_API_KEY - API key (also accepted via --api-key)
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
    parser = argparse.ArgumentParser(description="Generate image via Gemini API")
    parser.add_argument("--prompt", "-p", required=True, help="Image generation prompt")
    parser.add_argument("--output", "-o", required=True, help="Output file path")
    parser.add_argument("--api-key", default=os.environ.get("GEMINI_API_KEY", ""),
                        help="Gemini API key (or set GEMINI_API_KEY env)")
    parser.add_argument("--api-url", default=DEFAULT_API_URL, help="API base URL")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model name")
    parser.add_argument("--aspect-ratio", default=DEFAULT_ASPECT_RATIO,
                        help="Aspect ratio: 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9")
    parser.add_argument("--resolution", default=DEFAULT_RESOLUTION,
                        help="Resolution: 1K, 2K, 4K")
    args = parser.parse_args()

    if not args.api_key:
        print("[ERROR] No API key provided. Use --api-key or set GEMINI_API_KEY.", file=sys.stderr)
        sys.exit(1)

    result = generate_image(
        prompt=args.prompt,
        output_path=args.output,
        api_key=args.api_key,
        api_url=args.api_url,
        model=args.model,
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
