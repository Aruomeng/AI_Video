"""视频合成服务 - FFmpeg/moviepy"""
import uuid
import os
from pathlib import Path
from config import OUTPUT_DIR
import PIL.Image

# Monkey patch for Pillow 10.x compatibility (moviepy uses ANTIALIAS)
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS


async def compose_video(
    project_id: str,
    scenes: list[dict],
    bgm_path: str = "",
    bgm_volume: float = 0.15,
    resolution: str = "1080x1920",
    fps: int = 30,
    transition: str = "fade",
) -> dict:
    """合成视频"""
    from moviepy.editor import (
        ImageClip, AudioFileClip, CompositeAudioClip,
        concatenate_videoclips, TextClip, CompositeVideoClip,
    )

    width, height = map(int, resolution.split("x"))
    clips = []

    # 处理 BGM 路径
    if bgm_path and not os.path.exists(bgm_path):
        # 尝试从 BGM_DIR 查找
        from config import BGM_DIR
        candidate = BGM_DIR / bgm_path
        if candidate.exists():
            bgm_path = str(candidate)
        elif bgm_path.startswith("/bgm/"):  # 处理 URL 路径
            candidate = BGM_DIR / bgm_path.lstrip("/").replace("bgm/", "", 1)
            if candidate.exists():
                bgm_path = str(candidate)

    for scene in scenes:
        image_path = scene["image_path"]
        audio_path = scene["audio_path"]
        
        # 路径标准化：处理前端传来的 URL 路径 (/output/...)
        if image_path.startswith("/output/"):
            rel_path = image_path.lstrip("/").replace("output/", "", 1)
            candidate = OUTPUT_DIR / rel_path
            if candidate.exists():
                image_path = str(candidate)
        
        if audio_path.startswith("/output/"):
            rel_path = audio_path.lstrip("/").replace("output/", "", 1)
            candidate = OUTPUT_DIR / rel_path
            if candidate.exists():
                audio_path = str(candidate)
                
        # 再次检查文件是否存在
        if not os.path.exists(image_path):
             print(f"警告：找不到图片文件 {image_path}")
             continue
        if not os.path.exists(audio_path):
             print(f"警告：找不到音频文件 {audio_path}")
             continue

        narration = scene.get("narration", "")

        # 加载音频获取真实时长
        audio = AudioFileClip(audio_path)
        duration = audio.duration + 0.5  # 留一点间隔

        # 创建图片片段
        img_clip = (
            ImageClip(image_path)
            .set_duration(duration)
            .resize((width, height))
            .set_fps(fps)
        )

        # 添加字幕（底部居中）
        if narration:
            try:
                txt_clip = (
                    TextClip(
                        narration,
                        fontsize=36,
                        color="white",
                        font="Arial-Unicode-MS",
                        stroke_color="black",
                        stroke_width=1.5,
                        size=(width - 80, None),
                        method="caption",
                    )
                    .set_duration(duration)
                    .set_position(("center", height - 200))
                )
                img_clip = CompositeVideoClip([img_clip, txt_clip])
            except Exception:
                pass  # 字幕失败不阻塞视频生成

        img_clip = img_clip.set_audio(audio)
        clips.append(img_clip)

    if not clips:
        raise ValueError("没有有效的分镜片段")

    # 拼接
    if transition == "fade" and len(clips) > 1:
        # 交叉淡入淡出
        for i in range(len(clips)):
            if i > 0:
                clips[i] = clips[i].crossfadein(0.5)
        final = concatenate_videoclips(clips, method="compose", padding=-0.5)
    else:
        final = concatenate_videoclips(clips, method="compose")

    # 添加 BGM
    if bgm_path and os.path.exists(bgm_path):
        bgm = AudioFileClip(bgm_path).volumex(bgm_volume)
        if bgm.duration > final.duration:
            bgm = bgm.subclip(0, final.duration)
        bgm = bgm.audio_fadeout(2)

        if final.audio:
            final_audio = CompositeAudioClip([final.audio, bgm])
        else:
            final_audio = bgm
        final = final.set_audio(final_audio)

    # 输出
    output_filename = f"video_{project_id}_{uuid.uuid4().hex[:6]}.mp4"
    output_path = OUTPUT_DIR / "videos" / output_filename
    output_path.parent.mkdir(exist_ok=True)

    final.write_videofile(
        str(output_path),
        fps=fps,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        logger=None,
    )

    # 关闭资源
    final.close()
    for clip in clips:
        clip.close()

    file_size = output_path.stat().st_size

    return {
        "video_url": f"/output/videos/{output_filename}",
        "local_path": str(output_path),
        "duration": round(final.duration, 1),
        "file_size": file_size,
    }
