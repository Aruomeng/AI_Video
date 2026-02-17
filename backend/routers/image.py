"""图像生成路由"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.image_service import generate_image

router = APIRouter()


class ImageRequest(BaseModel):
    prompt: str
    style_prefix: str = ""
    width: int = 1024
    height: int = 1024
    provider: str = "openai"  # openai / stability / qwen
    api_key: str = ""
    base_url: str = ""
    model: str = ""


class ImageResponse(BaseModel):
    image_url: str
    local_path: str = ""


@router.post("/generate", response_model=ImageResponse)
async def generate(req: ImageRequest):
    """生成单张配图"""
    if not req.prompt.strip():
        raise HTTPException(400, "提示词不能为空")
    if not req.api_key:
        raise HTTPException(400, "请先配置图像生成 API Key")

    full_prompt = f"Unified Style: {req.style_prefix}\nScene Content: {req.prompt}".strip() if req.style_prefix else req.prompt

    result = await generate_image(
        prompt=full_prompt,
        width=req.width,
        height=req.height,
        provider=req.provider,
        api_key=req.api_key,
        base_url=req.base_url,
        model=req.model,
    )
    return result
