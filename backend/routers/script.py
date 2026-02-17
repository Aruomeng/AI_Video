"""脚本生成路由"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.llm_service import generate_script

router = APIRouter()


class ScriptRequest(BaseModel):
    topic: str
    style: str = "知识科普"
    duration: str = "short"  # short/medium/long
    language: str = "zh"
    llm_provider: str = "openai"  # openai / deepseek / qwen
    api_key: str = ""
    base_url: str = ""
    model: str = ""


class SceneItem(BaseModel):
    index: int
    narration: str
    image_prompt: str
    duration: float = 0


class ScriptResponse(BaseModel):
    title: str
    scenes: list[SceneItem]
    total_duration: float = 0


@router.post("/generate", response_model=ScriptResponse)
async def generate(req: ScriptRequest):
    """根据主题生成视频脚本（分镜）"""
    if not req.topic.strip():
        raise HTTPException(400, "主题不能为空")
    if not req.api_key:
        raise HTTPException(400, "请先配置 LLM API Key")

    result = await generate_script(
        topic=req.topic,
        style=req.style,
        duration=req.duration,
        language=req.language,
        provider=req.llm_provider,
        api_key=req.api_key,
        base_url=req.base_url,
        model=req.model,
    )
    return result
