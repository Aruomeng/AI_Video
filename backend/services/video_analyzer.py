"""竞品视频分析引擎"""
import json
import uuid
import subprocess
from pathlib import Path
from config import TEMP_DIR
from services.llm_service import chat_completion


async def analyze_video(
    video_url: str,
    llm_provider: str = "openai",
    api_key: str = "",
    base_url: str = "",
    model: str = "",
) -> dict:
    """分析竞品视频"""
    # 1. 下载视频
    video_path = await _download_video(video_url)

    # 2. 提取视频信息
    video_info = await _extract_video_info(video_path)

    # 3. 提取关键帧
    frames = await _extract_keyframes(video_path)

    # 4. LLM 分析
    analysis = await _llm_analyze(
        video_info=video_info,
        frame_count=len(frames),
        llm_provider=llm_provider,
        api_key=api_key,
        base_url=base_url,
        model=model,
    )

    return analysis


async def _download_video(url: str) -> Path:
    """使用 yt-dlp 下载视频"""
    filename = f"analyze_{uuid.uuid4().hex[:8]}"
    output_path = TEMP_DIR / f"{filename}.mp4"

    cmd = [
        "yt-dlp",
        "-f", "best[height<=720]",
        "-o", str(output_path),
        "--no-playlist",
        "--quiet",
        url,
    ]

    process = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if process.returncode != 0:
        # 如果 yt-dlp 失败，尝试直接下载
        import httpx
        async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            output_path.write_bytes(resp.content)

    return output_path


async def _extract_video_info(video_path: Path) -> dict:
    """提取视频元信息"""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        str(video_path),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        info = json.loads(result.stdout)

        duration = float(info.get("format", {}).get("duration", 0))
        streams = info.get("streams", [])

        video_stream = next((s for s in streams if s["codec_type"] == "video"), {})
        audio_stream = next((s for s in streams if s["codec_type"] == "audio"), {})

        return {
            "duration": round(duration, 1),
            "width": int(video_stream.get("width", 0)),
            "height": int(video_stream.get("height", 0)),
            "fps": eval(video_stream.get("r_frame_rate", "30/1")),
            "has_audio": bool(audio_stream),
        }
    except Exception:
        return {"duration": 0, "width": 0, "height": 0, "fps": 30, "has_audio": False}


async def _extract_keyframes(video_path: Path, max_frames: int = 10) -> list[Path]:
    """提取关键帧"""
    frames_dir = TEMP_DIR / f"frames_{uuid.uuid4().hex[:8]}"
    frames_dir.mkdir(exist_ok=True)

    cmd = [
        "ffmpeg", "-i", str(video_path),
        "-vf", f"fps=1/{max(1, int(30 / max_frames))}",
        "-frames:v", str(max_frames),
        "-q:v", "2",
        str(frames_dir / "frame_%03d.jpg"),
        "-y", "-loglevel", "quiet",
    ]

    subprocess.run(cmd, timeout=60)
    return sorted(frames_dir.glob("*.jpg"))


ANALYZE_PROMPT = """你是一个专业的短视频分析师。根据以下视频信息，分析视频的风格、结构，并生成可复制的制作方案。

视频信息：
- 时长：{duration} 秒
- 分辨率：{width}x{height}
- 帧率：{fps}

请输出严格 JSON 格式：
{{
  "title": "视频标题/主题概括",
  "summary": "视频内容一句话总结",
  "style": {{
    "tags": ["风格标签1", "风格标签2", "风格标签3"],
    "color_tone": "色调描述（如：暖色调、赛博朋克、电影感等）",
    "composition": "构图特点",
    "transition_style": "转场风格",
    "subtitle_style": "字幕样式描述"
  }},
  "scenes": [
    {{
      "index": 1,
      "description": "场景画面描述",
      "narration": "推测的旁白/解说词",
      "image_prompt": "英文 AI 生图提示词",
      "duration": 5.0
    }}
  ],
  "recommended_template": "推荐的视频模板类型",
  "recommended_voice": "推荐的语音风格",
  "recommended_bgm": "推荐的背景音乐类型",
  "total_duration": {duration}
}}

根据视频的时长和帧数，合理推测场景数量和每个场景内容。风格分析要详细具体。"""


async def _llm_analyze(
    video_info: dict,
    frame_count: int,
    llm_provider: str,
    api_key: str,
    base_url: str,
    model: str,
) -> dict:
    """使用 LLM 进行分析"""
    prompt = ANALYZE_PROMPT.format(**video_info)

    result = await chat_completion(
        messages=[
            {"role": "system", "content": "你是一个专业的短视频分析师，精通视频制作和 AI 内容创作。"},
            {"role": "user", "content": prompt},
        ],
        provider=llm_provider,
        api_key=api_key,
        base_url=base_url,
        model=model,
        temperature=0.7,
        response_format={"type": "json_object"},
    )

    data = json.loads(result)

    # 标准化
    style = data.get("style", {})
    scenes = []
    for i, s in enumerate(data.get("scenes", [])):
        scenes.append({
            "index": s.get("index", i + 1),
            "description": s.get("description", ""),
            "narration": s.get("narration", ""),
            "image_prompt": s.get("image_prompt", ""),
            "duration": s.get("duration", 5.0),
        })

    return {
        "title": data.get("title", ""),
        "summary": data.get("summary", ""),
        "style": {
            "tags": style.get("tags", []),
            "color_tone": style.get("color_tone", ""),
            "composition": style.get("composition", ""),
            "transition_style": style.get("transition_style", ""),
            "subtitle_style": style.get("subtitle_style", ""),
        },
        "scenes": scenes,
        "recommended_template": data.get("recommended_template", ""),
        "recommended_voice": data.get("recommended_voice", ""),
        "recommended_bgm": data.get("recommended_bgm", ""),
        "total_duration": data.get("total_duration", video_info.get("duration", 0)),
    }
