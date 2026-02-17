"""竞品视频分析路由"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.video_analyzer import analyze_video

router = APIRouter()


class AnalyzeRequest(BaseModel):
    video_url: str
    llm_provider: str = "openai"
    api_key: str = ""
    base_url: str = ""
    model: str = ""


class AnalysisStyle(BaseModel):
    tags: list[str] = []
    color_tone: str = ""
    composition: str = ""
    transition_style: str = ""
    subtitle_style: str = ""


class AnalysisScene(BaseModel):
    index: int
    description: str
    narration: str
    image_prompt: str
    duration: float = 0


class AnalysisReport(BaseModel):
    title: str
    summary: str
    style: AnalysisStyle
    scenes: list[AnalysisScene]
    recommended_template: str = ""
    recommended_voice: str = ""
    recommended_bgm: str = ""
    total_duration: float = 0


@router.post("/video", response_model=AnalysisReport)
async def analyze(req: AnalyzeRequest):
    """分析竞品视频，提取风格和脚本"""
    if not req.video_url.strip():
        raise HTTPException(400, "视频链接不能为空")
    if not req.api_key:
        raise HTTPException(400, "请先配置 LLM API Key")

    result = await analyze_video(
        video_url=req.video_url,
        llm_provider=req.llm_provider,
        api_key=req.api_key,
        base_url=req.base_url,
        model=req.model,
    )
    return result
