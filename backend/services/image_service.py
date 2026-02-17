"""图像生成服务 - 统一封装多个图像生成 API"""
import uuid
import httpx
from pathlib import Path
from openai import AsyncOpenAI
from config import OUTPUT_DIR


# ── OpenAI 兼容图像供应商配置 ─────────────────────────
IMAGE_PROVIDER_DEFAULTS = {
    "dall-e":           {"base_url": "https://api.openai.com/v1", "model": "dall-e-3"},
    "gemini-image":     {"base_url": "https://generativelanguage.googleapis.com/v1beta/openai/", "model": "imagen-4.0-generate-001"},
    "qwen-image":       {"base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "model": "wanx-v1"},
    "zhipu-image":      {"base_url": "https://open.bigmodel.cn/api/paas/v4/", "model": "cogview-3-flash"},
    "siliconflow-image": {"base_url": "https://api.siliconflow.cn/v1", "model": "black-forest-labs/FLUX.1-schnell"},
    "doubao-image":     {"base_url": "https://ark.cn-beijing.volces.com/api/v3", "model": "doubao-seedream-3-0-t2i-250415"},
}


async def generate_image(
    prompt: str,
    width: int = 1024,
    height: int = 1024,
    provider: str = "openai",
    api_key: str = "",
    base_url: str = "",
    model: str = "",
) -> dict:
    """生成图像"""
    if provider in ("openai", "dall-e"):
        return await _generate_dalle(prompt, width, height, api_key, base_url, model)
    elif provider == "stability":
        return await _generate_stability(prompt, width, height, api_key)
    elif provider == "gemini-image":
        return await _generate_gemini_native(prompt, width, height, api_key, model)
    elif provider in IMAGE_PROVIDER_DEFAULTS:
        # 智谱CogView / SiliconFlow(FLUX) / 豆包 / 通义万相 — 均走 OpenAI 兼容接口
        return await _generate_openai_compat(prompt, width, height, api_key, base_url, model, provider)
    else:
        raise ValueError(f"不支持的图像供应商: {provider}")


async def _generate_dalle(
    prompt: str, width: int, height: int,
    api_key: str, base_url: str = "", model: str = "",
) -> dict:
    """使用 DALL-E 生成"""
    client = AsyncOpenAI(api_key=api_key, base_url=base_url or "https://api.openai.com/v1")
    size = _normalize_size(width, height, provider="dall-e")

    response = await client.images.generate(
        model=model or "dall-e-3",
        prompt=prompt,
        size=size,
        quality="standard",
        n=1,
    )

    image_url = response.data[0].url
    local_path = await _download_image(image_url)

    return {"image_url": image_url, "local_path": str(local_path)}


async def _generate_openai_compat(
    prompt: str, width: int, height: int,
    api_key: str, base_url: str = "", model: str = "",
    provider: str = "qwen-image",
) -> dict:
    """通用 OpenAI 兼容图像接口（通义万相 / 智谱CogView / SiliconFlow / 豆包）"""
    defaults = IMAGE_PROVIDER_DEFAULTS.get(provider, {})
    url = base_url or defaults.get("base_url", "")
    model_name = model or defaults.get("model", "")
    
    # 自动修正 Gemini 模型名称（处理用户缓存的旧配置）
    if provider == "gemini-image":
        if not model_name or "gemini" in model_name:
            model_name = "imagen-3.0-generate-001"

    client = AsyncOpenAI(api_key=api_key, base_url=url)
    size = _normalize_size(width, height, provider=provider)

    response = await client.images.generate(
        model=model_name,
        prompt=prompt,
        size=size,
        n=1,
        response_format="b64_json",
    )

    image_data = response.data[0].b64_json
    import base64
    
    filename = f"img_{uuid.uuid4().hex[:8]}.png"
    filepath = OUTPUT_DIR / "images" / filename
    filepath.parent.mkdir(exist_ok=True)
    
    filepath.write_bytes(base64.b64decode(image_data))
    
    return {"image_url": f"/output/images/{filename}", "local_path": str(filepath)}


async def _generate_stability(
    prompt: str, width: int, height: int, api_key: str,
) -> dict:
    """使用 Stability AI 生成"""
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            "https://api.stability.ai/v2beta/stable-image/generate/sd3",
            headers={"Authorization": f"Bearer {api_key}", "Accept": "image/*"},
            files={"none": ""},
            data={
                "prompt": prompt,
                "width": width,
                "height": height,
                "output_format": "png",
            },
        )
        response.raise_for_status()

        filename = f"img_{uuid.uuid4().hex[:8]}.png"
        filepath = OUTPUT_DIR / "images" / filename
        filepath.parent.mkdir(exist_ok=True)
        filepath.write_bytes(response.content)

        return {"image_url": f"/output/images/{filename}", "local_path": str(filepath)}


async def _generate_gemini_native(
    prompt: str, width: int, height: int, api_key: str, model: str = "",
) -> dict:
    """使用 Google Gemini 原生 API 生成图像 (Imagen 4)"""
    model_name = "imagen-4.0-generate-001"
    if model and "gemini" not in model:  # 如果用户指定了非 gemini 的 model 名（如 imagen-3.0），则使用之
        model_name = model
    
    # 计算宽高比
    aspect_ratio = "1:1"
    ratio = width / height
    if 1.7 < ratio < 1.8:  # 16:9 (1.77)
        aspect_ratio = "16:9"
    elif 0.5 < ratio < 0.6:  # 9:16 (0.56)
        aspect_ratio = "9:16"
    elif 1.3 < ratio < 1.4:  # 4:3 (1.33)
        aspect_ratio = "4:3"
    elif 0.7 < ratio < 0.8:  # 3:4 (0.75)
        aspect_ratio = "3:4"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:predict"
    
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": aspect_ratio,
        },
    }
    
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            url,
            headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
            json=payload,
        )
        if response.status_code != 200:
            error_msg = response.text
            try:
                error_data = response.json()
                if "error" in error_data:
                    error_msg = error_data["error"].get("message", error_msg)
            except:
                pass
            raise ValueError(f"Gemini API Error: {error_msg}")
            
        data = response.json()
        if not data.get("predictions"):
             raise ValueError("Gemini API 返回结果为空")
             
        b64_image = data["predictions"][0]["bytesBase64Encoded"]
        
        import base64
        filename = f"img_{uuid.uuid4().hex[:8]}.png"
        filepath = OUTPUT_DIR / "images" / filename
        filepath.parent.mkdir(exist_ok=True)
        filepath.write_bytes(base64.b64decode(b64_image))
        
        return {"image_url": f"/output/images/{filename}", "local_path": str(filepath)}


def _normalize_size(width: int, height: int, provider: str = "dall-e") -> str:
    """标准化尺寸为 API 可接受的格式"""
    if provider in ("dall-e", "gemini-image"):
        valid = ["1024x1024", "1024x1792", "1792x1024"]
        target = f"{width}x{height}"
        if target in valid:
            return target
        # 自动选择最接近的尺寸
        if width > height:
            return "1792x1024"
        elif height > width:
            return "1024x1792"
        return "1024x1024"
    return f"{width}x{height}"


async def _download_image(url: str) -> Path:
    """下载远程图片到本地"""
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(url)
        resp.raise_for_status()

    filename = f"img_{uuid.uuid4().hex[:8]}.png"
    filepath = OUTPUT_DIR / "images" / filename
    filepath.parent.mkdir(exist_ok=True)
    filepath.write_bytes(resp.content)
    return filepath


async def test_image_connection(
    provider: str, api_key: str, base_url: str = "",
) -> bool:
    """测试图像服务连接"""
    if provider in ("openai", "dall-e"):
        client = AsyncOpenAI(api_key=api_key, base_url=base_url or "https://api.openai.com/v1")
        await client.models.list()
        return True
    elif provider == "stability":
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://api.stability.ai/v1/user/balance",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            resp.raise_for_status()
            return True
    elif provider in IMAGE_PROVIDER_DEFAULTS:
        defaults = IMAGE_PROVIDER_DEFAULTS.get(provider, {})
        url = base_url or defaults.get("base_url", "")
        client = AsyncOpenAI(api_key=api_key, base_url=url)
        await client.models.list()
        return True
    return False
