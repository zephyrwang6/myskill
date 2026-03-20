import os
import requests
import json

def generate_image(prompt):
    """
    调用 GPTNB API 生成图片

    参数:
        prompt: 图片描述文本

    返回:
        图片URL链接（字符串），失败返回None
    """
    api_key = os.environ.get("SEEDREAM_API_KEY", "")
    url = "https://api.gptnb.ai/v1/images/generations"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": "doubao-seedream-4-0-250828",
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024"
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()

        # 直接返回第一张图片的URL
        if result and "data" in result and len(result["data"]) > 0:
            return result["data"][0].get("url")
        return None
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        if hasattr(e.response, 'text'):
            print(f"错误详情: {e.response.text}")
        return None


if __name__ == "__main__":
    # 示例用法
    prompt = "一只可爱的猫咪在花园里玩耍"

    print(f"正在生成图片，提示词: {prompt}")
    image_url = generate_image(prompt)

    if image_url:
        print(f"\n生成成功！\n图片URL: {image_url}")
    else:
        print("\n生成失败，请检查错误信息")
