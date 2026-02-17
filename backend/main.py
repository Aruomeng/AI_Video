"""AI 视频生成后端 - FastAPI 主入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import CORS_ORIGINS, OUTPUT_DIR, BGM_DIR
from routers import script, image, voice, video, apikeys, analyze

app = FastAPI(
    title="AI Video Generator",
    description="轻量化 AI 视频生成引擎 API",
    version="0.1.0",
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件：输出视频和BGM
app.mount("/output", StaticFiles(directory=str(OUTPUT_DIR)), name="output")
app.mount("/bgm", StaticFiles(directory=str(BGM_DIR)), name="bgm")

# 注册路由
app.include_router(script.router, prefix="/api/script", tags=["脚本生成"])
app.include_router(image.router, prefix="/api/image", tags=["图像生成"])
app.include_router(voice.router, prefix="/api/voice", tags=["语音合成"])
app.include_router(video.router, prefix="/api/video", tags=["视频合成"])
app.include_router(apikeys.router, prefix="/api/keys", tags=["密钥管理"])
app.include_router(analyze.router, prefix="/api/analyze", tags=["竞品分析"])


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": "0.1.0"}


if __name__ == "__main__":
    import uvicorn
    from config import API_HOST, API_PORT
    uvicorn.run("main:app", host=API_HOST, port=API_PORT, reload=True)
