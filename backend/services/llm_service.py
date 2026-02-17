"""LLM 调用服务 - 统一封装多个 LLM 供应商"""
import json
from openai import AsyncOpenAI


# 供应商默认配置（均兼容 OpenAI SDK）
PROVIDER_DEFAULTS = {
    "openai": {"base_url": "https://api.openai.com/v1", "model": "gpt-4o-mini"},
    "gemini": {"base_url": "https://generativelanguage.googleapis.com/v1beta/openai/", "model": "gemini-2.5-flash"},
    "claude": {"base_url": "https://api.anthropic.com/v1/", "model": "claude-sonnet-4-20250514"},
    "deepseek": {"base_url": "https://api.deepseek.com/v1", "model": "deepseek-chat"},
    "qwen": {"base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "model": "qwen-plus"},
    "zhipu": {"base_url": "https://open.bigmodel.cn/api/paas/v4/", "model": "glm-4-flash"},
    "moonshot": {"base_url": "https://api.moonshot.cn/v1", "model": "moonshot-v1-8k"},
    "doubao": {"base_url": "https://ark.cn-beijing.volces.com/api/v3", "model": "doubao-1-5-pro-32k-250115"},
    "yi": {"base_url": "https://api.lingyiwanwu.com/v1", "model": "yi-lightning"},
    "baichuan": {"base_url": "https://api.baichuan-ai.com/v1/", "model": "Baichuan4-Air"},
    "minimax": {"base_url": "https://api.minimax.chat/v1", "model": "MiniMax-Text-01"},
    "siliconflow": {"base_url": "https://api.siliconflow.cn/v1", "model": "Qwen/Qwen2.5-7B-Instruct"},
    "groq": {"base_url": "https://api.groq.com/openai/v1", "model": "llama-3.3-70b-versatile"},
}


def _get_client(provider: str, api_key: str, base_url: str = "") -> AsyncOpenAI:
    """获取 OpenAI 兼容客户端"""
    defaults = PROVIDER_DEFAULTS.get(provider, {})
    url = base_url or defaults.get("base_url", "https://api.openai.com/v1")
    return AsyncOpenAI(api_key=api_key, base_url=url)


def _get_model(provider: str, model: str = "") -> str:
    """获取模型名"""
    if model:
        return model
    return PROVIDER_DEFAULTS.get(provider, {}).get("model", "gpt-4o-mini")


SCRIPT_SYSTEM_PROMPT = """你是一个专业的短视频脚本策划师。根据用户提供的主题，生成一个连贯的短视频脚本。

输出格式要求（严格 JSON）：
{
  "title": "视频标题",
  "scenes": [
    {
      "index": 1,
      "narration": "旁白文字（一句话一个场景）",
      "image_prompt": "英文图像描述提示词，用于 AI 生图，要详细描述画面内容、风格、色调"
    }
  ]
}

规则：
1. **时长与分镜映射表**（严格执行）：
   - **2分钟**：25-35个场景，旁白内容约300-400字
   - **4分钟**：50-60个场景，旁白内容约600-800字
   - **6分钟**：75-90个场景，旁白内容约1000-1200字
   - **8分钟及以上**：100+个场景
2. **极简短句**：每个场景的旁白必须非常简短（15字以内），坚决避免长句，切忌啰嗦。
3. **多镜头叙事**：通过频繁切换画面来提升观看体验，画面描述要具体且丰富。
4. image_prompt 必须是英文，详细且具体
4. 整体内容逻辑连贯，有开头（引入）、中间（展开）、结尾（总结）
5. 只输出 JSON，不要其他内容"""


async def generate_script(
    topic: str,
    style: str = "知识科普",
    duration: str = "short",
    language: str = "zh",
    provider: str = "openai",
    api_key: str = "",
    base_url: str = "",
    model: str = "",
) -> dict:
    """生成视频脚本"""
    client = _get_client(provider, api_key, base_url)
    model_name = _get_model(provider, model)

    user_prompt = f"主题：{topic}\n风格：{style}\n时长：{duration}\n语言：{'中文' if language == 'zh' else 'English'}"

    response = await client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": SCRIPT_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.8,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    data = json.loads(content)

    # 标准化字段
    scenes = []
    for i, scene in enumerate(data.get("scenes", [])):
        scenes.append({
            "index": scene.get("index", i + 1),
            "narration": scene.get("narration", ""),
            "image_prompt": scene.get("image_prompt", ""),
            "duration": 0,
        })

    return {
        "title": data.get("title", topic),
        "scenes": scenes,
        "total_duration": 0,
    }


async def test_llm_connection(
    provider: str,
    api_key: str,
    base_url: str = "",
    model: str = "",
) -> bool:
    """测试 LLM 连接"""
    client = _get_client(provider, api_key, base_url)
    model_name = _get_model(provider, model)

    response = await client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": "Hi, reply with one word."}],
        max_tokens=10,
    )
    return bool(response.choices[0].message.content)


async def chat_completion(
    messages: list[dict],
    provider: str = "openai",
    api_key: str = "",
    base_url: str = "",
    model: str = "",
    temperature: float = 0.7,
    response_format: dict | None = None,
) -> str:
    """通用聊天补全"""
    client = _get_client(provider, api_key, base_url)
    model_name = _get_model(provider, model)

    kwargs = {
        "model": model_name,
        "messages": messages,
        "temperature": temperature,
    }
    if response_format:
        kwargs["response_format"] = response_format

    response = await client.chat.completions.create(**kwargs)
    return response.choices[0].message.content or ""
