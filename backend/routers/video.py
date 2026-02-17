"""视频合成路由"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.video_service import compose_video

router = APIRouter()


class SceneData(BaseModel):
    index: int
    narration: str
    image_path: str
    audio_path: str
    duration: float


class VideoRequest(BaseModel):
    project_id: str
    scenes: list[SceneData]
    bgm_path: str = ""
    bgm_volume: float = 0.15
    resolution: str = "1080x1920"  # 宽x高
    fps: int = 30
    transition: str = "fade"  # fade / slide / none


class VideoResponse(BaseModel):
    video_url: str
    local_path: str
    duration: float
    file_size: int


@router.post("/compose", response_model=VideoResponse)
async def compose(req: VideoRequest):
    """合成最终视频"""
    if not req.scenes:
        raise HTTPException(400, "没有分镜数据")

    result = await compose_video(
        project_id=req.project_id,
        scenes=[s.model_dump() for s in req.scenes],
        bgm_path=req.bgm_path,
        bgm_volume=req.bgm_volume,
        resolution=req.resolution,
        fps=req.fps,
        transition=req.transition,
    )
    return result
