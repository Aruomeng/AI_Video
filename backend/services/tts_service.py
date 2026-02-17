"""TTS 语音合成服务"""
import uuid
import edge_tts
from pathlib import Path
from config import OUTPUT_DIR


async def synthesize_speech(
    text: str,
    voice: str = "zh-CN-XiaoxiaoNeural",
    rate: str = "+0%",
    volume: str = "+0%",
    provider: str = "edge-tts",
    api_key: str = "",
) -> dict:
    """合成语音"""
    if provider == "edge-tts":
        return await _edge_tts(text, voice, rate, volume)
    elif provider == "openai-tts":
        return await _openai_tts(text, voice, api_key)
    else:
        raise ValueError(f"不支持的 TTS 供应商: {provider}")


async def _edge_tts(text: str, voice: str, rate: str, volume: str) -> dict:
    """使用 Edge-TTS（免费）"""
    filename = f"tts_{uuid.uuid4().hex[:8]}.mp3"
    filepath = OUTPUT_DIR / "audio" / filename
    filepath.parent.mkdir(exist_ok=True)

    communicate = edge_tts.Communicate(text, voice, rate=rate, volume=volume)
    await communicate.save(str(filepath))

    # 估算时长（粗略：中文约 4 字/秒，英文约 3 词/秒）
    char_count = len(text)
    estimated_duration = char_count / 4.0

    return {
        "audio_url": f"/output/audio/{filename}",
        "local_path": str(filepath),
        "duration": round(estimated_duration, 1),
    }


async def _openai_tts(text: str, voice: str, api_key: str) -> dict:
    """使用 OpenAI TTS"""
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=api_key)

    # OpenAI TTS 音色映射
    voice_map = {
        "alloy": "alloy", "echo": "echo", "fable": "fable",
        "onyx": "onyx", "nova": "nova", "shimmer": "shimmer",
    }
    tts_voice = voice_map.get(voice, "alloy")

    response = await client.audio.speech.create(
        model="tts-1",
        voice=tts_voice,
        input=text,
    )

    filename = f"tts_{uuid.uuid4().hex[:8]}.mp3"
    filepath = OUTPUT_DIR / "audio" / filename
    filepath.parent.mkdir(exist_ok=True)

    filepath.write_bytes(response.content)

    char_count = len(text)
    estimated_duration = char_count / 4.0

    return {
        "audio_url": f"/output/audio/{filename}",
        "local_path": str(filepath),
        "duration": round(estimated_duration, 1),
    }


async def list_voices(provider: str = "edge-tts", language: str = "zh") -> list[dict]:
    """获取可用音色列表"""
    if provider == "edge-tts":
        voices = await edge_tts.list_voices()
        filtered = []
        for v in voices:
            if language in v["Locale"].lower():
                filtered.append({
                    "id": v["ShortName"],
                    "name": v["FriendlyName"],
                    "gender": v["Gender"],
                    "locale": v["Locale"],
                })
        return filtered

    elif provider == "openai-tts":
        return [
            {"id": "alloy", "name": "Alloy", "gender": "Neutral", "locale": "en"},
            {"id": "echo", "name": "Echo", "gender": "Male", "locale": "en"},
            {"id": "fable", "name": "Fable", "gender": "Female", "locale": "en"},
            {"id": "onyx", "name": "Onyx", "gender": "Male", "locale": "en"},
            {"id": "nova", "name": "Nova", "gender": "Female", "locale": "en"},
            {"id": "shimmer", "name": "Shimmer", "gender": "Female", "locale": "en"},
        ]

    return []
