"""API 密钥管理路由"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.llm_service import test_llm_connection, PROVIDER_DEFAULTS
from services.image_service import test_image_connection

router = APIRouter()

# ── 所有 LLM 供应商 ID 集合 ──────────────────────────────
LLM_PROVIDERS = set(PROVIDER_DEFAULTS.keys())

# ── 所有图像供应商 ID 集合 ──────────────────────────────
IMAGE_PROVIDERS = {"dall-e", "gemini-image", "stability", "qwen-image", "zhipu-image", "siliconflow-image", "doubao-image"}


class APIKeyConfig(BaseModel):
    provider: str
    api_key: str
    base_url: str = ""
    model: str = ""


class TestResult(BaseModel):
    success: bool
    message: str
    latency_ms: float = 0


@router.post("/test", response_model=TestResult)
async def test_connection(config: APIKeyConfig):
    """测试 API Key 连接"""
    import time
    start = time.time()

    try:
        if config.provider in LLM_PROVIDERS:
            await test_llm_connection(
                provider=config.provider,
                api_key=config.api_key,
                base_url=config.base_url,
                model=config.model,
            )
        elif config.provider in IMAGE_PROVIDERS:
            await test_image_connection(
                provider=config.provider,
                api_key=config.api_key,
                base_url=config.base_url,
            )
        elif config.provider == "edge-tts":
            pass  # 免费服务，无需测试
        else:
            raise HTTPException(400, f"不支持的服务商: {config.provider}")

        latency = (time.time() - start) * 1000
        return TestResult(success=True, message="连接成功", latency_ms=round(latency, 1))

    except HTTPException:
        raise
    except Exception as e:
        latency = (time.time() - start) * 1000
        return TestResult(success=False, message=str(e), latency_ms=round(latency, 1))


@router.get("/providers")
async def get_providers():
    """获取支持的服务商列表"""
    return {
        "llm": [
            {"id": "openai", "name": "OpenAI", "base_url": "https://api.openai.com/v1",
             "models": ["gpt-4o", "gpt-4o-mini", "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "o3-mini"]},
            {"id": "gemini", "name": "Google Gemini", "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
             "models": ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash", "gemini-2.5-flash-image", "gemini-3-pro-preview"]},
            {"id": "claude", "name": "Anthropic Claude", "base_url": "https://api.anthropic.com/v1/",
             "models": ["claude-sonnet-4-20250514", "claude-3-5-haiku-20241022"]},
            {"id": "deepseek", "name": "DeepSeek", "base_url": "https://api.deepseek.com/v1",
             "models": ["deepseek-chat", "deepseek-reasoner"]},
            {"id": "qwen", "name": "通义千问", "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
             "models": ["qwen-plus", "qwen-turbo", "qwen-max", "qwen-long"]},
            {"id": "zhipu", "name": "智谱 AI (GLM)", "base_url": "https://open.bigmodel.cn/api/paas/v4/",
             "models": ["glm-4-flash", "glm-4-plus", "glm-4-air", "glm-4-long"]},
            {"id": "moonshot", "name": "月之暗面 (Kimi)", "base_url": "https://api.moonshot.cn/v1",
             "models": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"]},
            {"id": "doubao", "name": "豆包 (字节跳动)", "base_url": "https://ark.cn-beijing.volces.com/api/v3",
             "models": ["doubao-1-5-pro-32k-250115", "doubao-1-5-lite-32k-250115"]},
            {"id": "yi", "name": "零一万物 (Yi)", "base_url": "https://api.lingyiwanwu.com/v1",
             "models": ["yi-lightning", "yi-large", "yi-medium"]},
            {"id": "baichuan", "name": "百川智能", "base_url": "https://api.baichuan-ai.com/v1/",
             "models": ["Baichuan4-Air", "Baichuan4-Turbo", "Baichuan3-Turbo"]},
            {"id": "minimax", "name": "MiniMax (海螺)", "base_url": "https://api.minimax.chat/v1",
             "models": ["MiniMax-Text-01", "abab6.5s-chat"]},
            {"id": "siliconflow", "name": "SiliconFlow (硅基流动)", "base_url": "https://api.siliconflow.cn/v1",
             "models": ["Qwen/Qwen2.5-7B-Instruct", "deepseek-ai/DeepSeek-V3", "THUDM/glm-4-9b-chat"]},
            {"id": "groq", "name": "Groq (超快推理)", "base_url": "https://api.groq.com/openai/v1",
             "models": ["llama-3.3-70b-versatile", "gemma2-9b-it", "mixtral-8x7b-32768"]},
        ],
        "image": [
            {"id": "dall-e", "name": "DALL·E (OpenAI)", "base_url": "https://api.openai.com/v1",
             "models": ["dall-e-3", "dall-e-2"]},
            {"id": "gemini-image", "name": "Gemini Imagen", "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
             "models": ["imagen-4.0-generate-001", "imagen-3.0-generate-001"]},
            {"id": "stability", "name": "Stability AI", "base_url": "https://api.stability.ai",
             "models": ["stable-diffusion-xl", "sd3"]},
            {"id": "qwen-image", "name": "通义万相", "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
             "models": ["wanx-v1"]},
            {"id": "zhipu-image", "name": "智谱 CogView", "base_url": "https://open.bigmodel.cn/api/paas/v4/",
             "models": ["cogview-3-flash", "cogview-3-plus"]},
            {"id": "siliconflow-image", "name": "SiliconFlow 图像", "base_url": "https://api.siliconflow.cn/v1",
             "models": ["black-forest-labs/FLUX.1-schnell", "stabilityai/stable-diffusion-3-5-large"]},
            {"id": "doubao-image", "name": "豆包图像", "base_url": "https://ark.cn-beijing.volces.com/api/v3",
             "models": ["doubao-seedream-3-0-t2i-250415"]},
        ],
        "tts": [
            {"id": "edge-tts", "name": "Edge TTS (免费)", "base_url": "", "models": []},
            {"id": "openai-tts", "name": "OpenAI TTS", "base_url": "https://api.openai.com/v1",
             "models": ["tts-1", "tts-1-hd"]},
        ],
    }
