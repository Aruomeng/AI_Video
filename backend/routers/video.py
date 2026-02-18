from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from services.video_service import compose_video
from routers.auth import get_current_user
from models.user import User
from models.project import Project
from database import get_session
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter()

class Scene(BaseModel):
    index: int
    narration: str
    image_prompt: Optional[str] = ""
    image_url: Optional[str] = ""
    audio_url: Optional[str] = ""
    duration: float = 0

class VideoRequest(BaseModel):
    project_id: str
    scenes: List[Scene]
    bgm_path: Optional[str] = ""
    bgm_volume: float = 0.2
    resolution: str = "1080x1920"
    fps: int = 30
    transition: str = "fade"

class VideoResponse(BaseModel):
    video_url: str
    local_path: str
    duration: float

class ProjectSaveRequest(BaseModel):
    title: str
    scenes: List[dict]
    video_url: str

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

@router.post("/save")
async def save_project(
    req: ProjectSaveRequest, 
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    project = Project(
        user_id=current_user.id,
        title=req.title,
        scenes=req.scenes,
        video_url=req.video_url,
        status="completed"
    )
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return {"status": "ok", "project_id": project.id}
