"""应用配置模块"""
import os
from pathlib import Path

# 基础路径
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
BGM_DIR = BASE_DIR / "bgm"
TEMPLATES_DIR = BASE_DIR / "templates"
TEMP_DIR = BASE_DIR / "temp"

# 确保目录存在
for d in [OUTPUT_DIR, BGM_DIR, TEMPLATES_DIR, TEMP_DIR]:
    d.mkdir(exist_ok=True)

# 服务配置
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# CORS 允许的来源
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
