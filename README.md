# 🎬 AI Video Generator

轻量化 AI 视频生成引擎 —— 零门槛、零 ComfyUI、一键生成短视频

## ✨ 特性

- 🚀 **全自动视频生成** - 输入主题，一键生成完整短视频
- 🎨 **多 AI 模型支持** - OpenAI / DeepSeek / 通义千问 / Stability AI
- 🔍 **竞品模仿** - 粘贴视频链接，AI 分析风格并一键复制
- 🎤 **智能语音** - Edge-TTS（免费）/ OpenAI TTS
- 📱 **响应式设计** - 支持桌面端和移动端
- ⚡ **轻量化** - 无需 ComfyUI，无需显卡，云端 API 驱动

## 🏗️ 技术栈

| 模块 | 技术 |
|------|------|
| 前端 | Next.js 14 + TypeScript |
| 后端 | FastAPI (Python) |
| 视频处理 | FFmpeg + moviepy |
| AI 服务 | OpenAI / DeepSeek / 通义 / Stability AI |

## 🚀 快速开始

### 前端
```bash
cd frontend
npm install
npm run dev
```

### 后端
```bash
cd backend
pip install -r requirements.txt
python main.py
```

## 📜 License

MIT
