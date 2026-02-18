<p align="center">
  <img src="https://img.shields.io/badge/Next.js-16-black?style=for-the-badge&logo=next.js" />
  <img src="https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react" />
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi" />
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-Neon-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/FFmpeg-007808?style=for-the-badge&logo=ffmpeg&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" />
</p>

<h1 align="center">AI Video Generator</h1>

<p align="center">
  <strong>轻量化全栈 AI 短视频生成引擎</strong><br/>
  零 ComfyUI · 零显卡依赖 · 多模型适配 · 云端 API 驱动
</p>

<p align="center">
  <a href="#-核心功能">核心功能</a> ·
  <a href="#-系统架构">系统架构</a> ·
  <a href="#-技术栈">技术栈</a> ·
  <a href="#-快速开始">快速开始</a> ·
  <a href="#-项目结构">项目结构</a>
</p>

---

## � 项目简介

AI Video Generator 是一个**全栈 AI 短视频自动化生产平台**，用户仅需输入一个主题，系统即可自动完成 **脚本生成 → AI 配图 → 语音合成 → 视频合成** 的完整工作流。

本项目采用**前后端分离架构**，前端使用 Next.js 16 + React 19 构建现代化 SPA，后端基于 FastAPI 提供高性能异步 API 服务，通过 **策略模式** 适配 OpenAI、Google Gemini、DeepSeek、通义千问、SiliconFlow 等多个 AI 供应商，实现 LLM 文案 / 图像生成 / TTS 语音的灵活切换。

> **设计理念**：去重型化 — 不依赖 ComfyUI、Stable Diffusion 本地部署或高端 GPU，完全通过云端 API 驱动，降低使用门槛的同时保证生产力。

---

## ✨ 核心功能

### 🎬 AI 视频全自动生成

| 步骤 | 功能 | 技术实现 |
|:---:|------|----------|
| **01** | 智能脚本生成 | 多 LLM 供应商适配（OpenAI / Gemini / DeepSeek / 智谱），Prompt 工程优化，支持自定义风格、时长 |
| **02** | AI 图像生成 | DALL·E 3 / Imagen 4.0 / SiliconFlow / CogView，并发池化生成，支持竖屏 9:16 / 横屏 16:9 / 方形 1:1 |
| **03** | 语音合成 | Edge-TTS（免费）/ OpenAI TTS，7+ 中文音色，可调语速，实时试听预览 |
| **04** | 视频合成 | FFmpeg + MoviePy 流水线，自动添加字幕、BGM、转场效果，一键导出 |

### � 竞品视频智能分析

- 粘贴抖音 / B站 / YouTube / 快手等平台视频链接
- AI 自动分析视频风格、色调、脚本结构、语音风格、BGM 类型
- 生成结构化分析报告，**一键应用到创作工作台**生成同款视频

### 🔐 用户系统与数据持久化

- JWT 无状态认证（注册 / 登录 / 路由守卫）
- 项目云端存储与管理（Neon PostgreSQL）
- API Key 浏览器本地加密存储，零服务端泄露风险

---

## 🏗 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js 16)                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐  │
│  │ Landing  │ │  Studio  │ │ Settings │ │  Copycat   │  │
│  │  Page    │ │ (4-Step) │ │ (API Mgr)│ │ (Analyzer) │  │
│  └──────────┘ └──────────┘ └──────────┘ └────────────┘  │
│  ┌──────────────────┐  ┌─────────────────────────────┐  │
│  │  AuthContext      │  │  SVG Icon System (35+ icons)│  │
│  │  (JWT State Mgmt) │  │  Design System (CSS Vars)   │  │
│  └──────────────────┘  └─────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────┘
                            │ RESTful API
┌───────────────────────────▼─────────────────────────────┐
│                   Backend (FastAPI)                       │
│  ┌─────────────────── Routers ──────────────────────┐   │
│  │ /api/script  │ /api/image │ /api/voice │ /api/video│  │
│  │ /api/keys    │ /api/analyze │ /api/auth           │  │
│  └──────────────────────────────────────────────────┘   │
│  ┌─────────────────── Services ─────────────────────┐   │
│  │ LLM Service     │ Image Service  │ TTS Service    │  │
│  │ (Strategy Pattern: OpenAI/Gemini/DeepSeek/ZhiPu) │  │
│  │ Video Service   │ Video Analyzer │ Auth Service   │  │
│  └──────────────────────────────────────────────────┘   │
│  ┌─── Data Layer ───┐  ┌─── Processing ────────────┐   │
│  │ SQLModel ORM     │  │ FFmpeg + MoviePy Pipeline  │   │
│  │ AsyncPG Driver   │  │ Concurrent Worker Pool     │   │
│  │ Neon PostgreSQL   │  │ yt-dlp Video Downloader   │   │
│  └──────────────────┘  └───────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠 技术栈

### Frontend

| 技术 | 版本 | 用途 |
|------|------|------|
| **Next.js** | 16.1.6 | React 全栈框架，Turbopack 构建 |
| **React** | 19.2.3 | UI 组件库，React Compiler 优化 |
| **TypeScript** | 5.x | 类型安全 |
| **CSS Modules** | — | 组件级样式隔离 |
| **Custom SVG Icon System** | — | 35+ 手写 Lucide 风格 SVG 图标 |

### Backend

| 技术 | 版本 | 用途 |
|------|------|------|
| **FastAPI** | 0.115 | 高性能异步 Web 框架 |
| **SQLModel** | latest | ORM（SQLAlchemy + Pydantic 融合） |
| **AsyncPG** | latest | PostgreSQL 异步驱动 |
| **Neon PostgreSQL** | — | Serverless 云数据库 |
| **JWT (python-jose)** | — | 无状态身份认证 |
| **OpenAI SDK** | 1.50 | LLM / DALL·E / TTS API 调用 |
| **Edge-TTS** | 6.1 | 微软免费 TTS 引擎 |
| **MoviePy** | 1.0.3 | Python 视频处理 |
| **FFmpeg** | — | 底层音视频编解码 |
| **yt-dlp** | — | 视频下载与分析 |
| **Pillow** | 10.4 | 图像处理与格式转换 |

### 设计模式与工程实践

- **策略模式**：AI 供应商（LLM / Image / TTS）通过统一接口抽象，运行时按用户配置动态切换
- **并发池化**：图片与语音生成采用可控并发（Concurrency = 5），显著提升批量生成速度
- **前后端分离**：RESTful API + CORS，前端通过 Context API 管理全局认证状态
- **渐进式降级**：数据库未配置时服务仍可正常启动（核心视频生成功能不依赖数据库）

---

## 🚀 快速开始

### 环境要求

- **Node.js** ≥ 18
- **Python** ≥ 3.10
- **FFmpeg**（系统级安装）
- 至少一个 AI API Key（OpenAI / DeepSeek / Gemini 等）

### 1. 克隆项目

```bash
git clone https://github.com/your-username/AiVideo.git
cd AiVideo
```

### 2. 启动后端

```bash
cd backend
pip install -r requirements.txt

# 配置环境变量（可选，用于数据库和认证功能）
cp .env.example .env
# 编辑 .env 填入 DATABASE_URL、SECRET_KEY 等

# 启动开发服务器（支持热重载）
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

### 4. 访问应用

- **前端**：http://localhost:3000
- **后端 API**：http://localhost:8000
- **API 文档**：http://localhost:8000/docs（Swagger UI）

### 5. 配置 API Key

打开浏览器访问 http://localhost:3000/settings，配置你的 AI 服务 API Key。所有密钥仅存储在浏览器本地，不会上传至服务器。

---

## 📂 项目结构

```
AiVideo/
├── frontend/                    # Next.js 16 前端
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx         # 首页（Landing Page）
│   │   │   ├── studio/          # 创作工作台（4 步向导）
│   │   │   ├── settings/        # API 密钥管理
│   │   │   ├── copycat/         # 竞品视频分析
│   │   │   ├── login/           # 登录页
│   │   │   ├── register/        # 注册页
│   │   │   └── globals.css      # 全局设计系统
│   │   ├── components/
│   │   │   └── Icon.tsx         # 集中式 SVG 图标组件
│   │   └── context/
│   │       └── AuthContext.tsx   # 全局认证状态管理
│   └── package.json
│
├── backend/                     # FastAPI 后端
│   ├── main.py                  # 应用入口 & 路由注册
│   ├── database.py              # 数据库连接（Neon PostgreSQL）
│   ├── routers/
│   │   ├── script.py            # 脚本生成 API
│   │   ├── image.py             # 图像生成 API
│   │   ├── voice.py             # 语音合成 API
│   │   ├── video.py             # 视频合成 & 项目存储 API
│   │   ├── apikeys.py           # API Key 管理 & 供应商查询
│   │   ├── analyze.py           # 竞品视频分析 API
│   │   └── auth.py              # 认证 API（JWT）
│   ├── services/
│   │   ├── llm_service.py       # LLM 服务（多供应商策略）
│   │   ├── image_service.py     # 图像生成服务
│   │   ├── tts_service.py       # TTS 语音服务
│   │   ├── video_service.py     # FFmpeg 视频合成
│   │   ├── video_analyzer.py    # 视频下载与 AI 分析
│   │   └── auth.py              # 密码哈希 & JWT 工具
│   ├── models/
│   │   ├── user.py              # 用户模型
│   │   └── project.py           # 项目模型
│   └── requirements.txt
│
└── README.md
```

---

## 📸 功能截图

> 启动项目后访问 http://localhost:3000 即可体验完整功能

| 首页 | 创作工作台 | 竞品分析 |
|:---:|:---:|:---:|
| 科技感 Landing Page | 4 步向导式创作流程 | 一键分析 & 模仿 |

---

## � License

[MIT License](LICENSE) — 自由使用、修改和分发。
