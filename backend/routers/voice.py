"""语音合成路由"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from services.tts_service import synthesize_speech, list_voices

router = APIRouter()


class TTSRequest(BaseModel):
    text: str
    voice: str = "zh-CN-XiaoxiaoNeural"
    rate: str = "+0%"
    volume: str = "+0%"
    provider: str = "edge-tts"  # edge-tts / openai
    api_key: str = ""


class TTSResponse(BaseModel):
    audio_url: str
    local_path: str
    duration: float = 0


@router.post("/synthesize", response_model=TTSResponse)
async def synthesize(req: TTSRequest):
    """合成语音"""
    if not req.text.strip():
        raise HTTPException(400, "文本不能为空")

    result = await synthesize_speech(
        text=req.text,
        voice=req.voice,
        rate=req.rate,
        volume=req.volume,
        provider=req.provider,
        api_key=req.api_key,
    )
    return result


@router.get("/voices")
async def get_voices(provider: str = "edge-tts", language: str = "zh"):
    """获取可用音色列表"""
    voices = await list_voices(provider=provider, language=language)
    return {"voices": voices}
