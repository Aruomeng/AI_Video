"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import styles from "./studio.module.css";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Scene {
  index: number;
  narration: string;
  image_prompt: string;
  image_url?: string;
  audio_url?: string;
  duration: number;
}

const STEPS = [
  { id: 1, label: "内容创作", icon: "📝" },
  { id: 2, label: "视觉风格", icon: "🎨" },
  { id: 3, label: "语音配置", icon: "🎤" },
  { id: 4, label: "预览合成", icon: "🎬" },
];

const STYLES = ["知识科普", "情感故事", "历史文化", "科学思辨", "个人成长", "产品介绍", "搞笑幽默", "新闻资讯"];

const DURATIONS: Record<string, string> = { short: "短 (30-60秒)", medium: "中 (1-2分钟)", long: "长 (2-3分钟)" };

export default function StudioPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState("");
  const [providers, setProviders] = useState<any>(null);

  // Fetch providers on mount
  useEffect(() => {
    fetch(`${API_BASE}/api/keys/providers`)
      .then((res) => res.json())
      .then((data) => setProviders(data))
      .catch((err) => console.error("Failed to fetch providers:", err));
  }, []);

  // Step 1: Content
  const [topic, setTopic] = useState("");
  const [style, setStyle] = useState("知识科普");
  const [styleMode, setStyleMode] = useState<"select" | "custom">("select");
  const [duration, setDuration] = useState(2);
  const [scenes, setScenes] = useState<Scene[]>([]);
  const [title, setTitle] = useState("");

  // Step 2: Visual
  const [stylePrefix, setStylePrefix] = useState("Minimalist hand-drawn stick figure style, clean black lines, simple flat colors, white background, expressive characters, humorous vibe, high quality");
  const [resolution, setResolution] = useState("1080x1920");
  const [imageProvider, setImageProvider] = useState("dall-e");

  // 当 providers 加载后，如果当前选择的 provider 不在列表中，默认选中第一个
  useEffect(() => {
    if (providers?.image && !providers.image.find((p: any) => p.id === imageProvider)) {
      setImageProvider(providers.image[0].id);
    }
  }, [providers, imageProvider]);

  // Step 3: Voice
  const [voice, setVoice] = useState("zh-CN-XiaoxiaoNeural");
  const [rate, setRate] = useState("+0%");
  const [ttsProvider, setTtsProvider] = useState("edge-tts");
  const [bgm, setBgm] = useState("");

  // Step 4: Result
  const [videoUrl, setVideoUrl] = useState("");

  // API Keys from localStorage
  const getKey = (provider: string) => {
    if (typeof window === "undefined") return "";
    const keys = JSON.parse(localStorage.getItem("ai_video_keys") || "{}");
    return keys[provider]?.api_key || "";
  };

  const getConfig = (provider: string) => {
    if (typeof window === "undefined") return {};
    const keys = JSON.parse(localStorage.getItem("ai_video_keys") || "{}");
    return keys[provider] || {};
  };

  // Step 1: Generate Script
  const generateScript = async () => {
    const llmConfig = getConfig("llm");
    if (!llmConfig.api_key) {
      alert("请先在「API 设置」中配置 LLM API Key");
      router.push("/settings");
      return;
    }

    setLoading(true);
    setProgress("正在生成文案...");
    try {
      const res = await fetch(`${API_BASE}/api/script/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic,
          style,
          duration: duration + "分钟",
          llm_provider: llmConfig.provider || "openai",
          api_key: llmConfig.api_key,
          base_url: llmConfig.base_url || "",
          model: llmConfig.model || "",
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "生成失败");
      setTitle(data.title);
      setScenes(data.scenes);
      setStep(2);
    } catch (e: any) {
      alert(`错误: ${e.message}`);
    } finally {
      setLoading(false);
      setProgress("");
    }
  };

  // Step 2: Generate Images
  const generateImages = async () => {
    const imgConfig = getConfig("image");
    if (!imgConfig.api_key) {
      alert("请先在「API 设置」中配置图像生成 API Key");
      router.push("/settings");
      return;
    }

    setLoading(true);
    const updatedScenes = [...scenes];
    const [w, h] = resolution.split("x").map(Number);
    let failCount = 0;

    for (let i = 0; i < updatedScenes.length; i++) {
      setProgress(`生成配图 ${i + 1}/${updatedScenes.length}...`);
      try {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 120000); // 2 分钟超时

        const res = await fetch(`${API_BASE}/api/image/generate`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          signal: controller.signal,
          body: JSON.stringify({
            prompt: updatedScenes[i].image_prompt,
            style_prefix: stylePrefix,
            width: w,
            height: h,
            provider: imgConfig.provider || "dall-e",
            api_key: imgConfig.api_key,
            base_url: imgConfig.base_url || "",
            model: imgConfig.model || "",
          }),
        });
        clearTimeout(timeout);
        const data = await res.json();
        if (res.ok) {
          updatedScenes[i].image_url = data.image_url;
        } else {
          failCount++;
          console.error(`图片 ${i + 1} 生成失败:`, data.detail || data);
        }
      } catch (e: any) {
        failCount++;
        console.error(`图片 ${i + 1} 生成失败:`, e);
      }
    }

    setScenes(updatedScenes);
    if (failCount > 0) {
      alert(`${failCount} 张图片生成失败，请检查 API 配置或稍后重试`);
    }
    setStep(3);
    setLoading(false);
    setProgress("");
  };

  // Step 3: Generate Audio
  const generateAudio = async () => {
    setLoading(true);
    const updatedScenes = [...scenes];
    let failCount = 0;

    for (let i = 0; i < updatedScenes.length; i++) {
      setProgress(`合成语音 ${i + 1}/${updatedScenes.length}...`);
      try {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 60000); // 1 分钟超时

        const ttsConfig = getConfig("tts");
        const res = await fetch(`${API_BASE}/api/voice/synthesize`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          signal: controller.signal,
          body: JSON.stringify({
            text: updatedScenes[i].narration,
            voice,
            rate,
            provider: ttsConfig.provider || ttsProvider,
            api_key: ttsConfig.api_key || "",
          }),
        });
        clearTimeout(timeout);
        const data = await res.json();
        if (res.ok) {
          updatedScenes[i].audio_url = data.local_path;
          updatedScenes[i].duration = data.duration;
        } else {
          failCount++;
          console.error(`语音 ${i + 1} 合成失败:`, data.detail || data);
        }
      } catch (e: any) {
        failCount++;
        console.error(`语音 ${i + 1} 合成失败:`, e);
      }
    }

    setScenes(updatedScenes);
    if (failCount > 0) {
      alert(`${failCount} 条语音合成失败，请检查配置或稍后重试`);
    }
    setStep(4);
    setStep(4);
    setLoading(false);
    setProgress("");
  };

  const [previewing, setPreviewing] = useState(false);

  const previewVoice = async () => {
    if (!voice) return;
    setPreviewing(true);
    try {
      const ttsConfig = getConfig("tts");
      const res = await fetch(`${API_BASE}/api/voice/synthesize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: "你好，我是智能创作助手，这是我的声音演示。",
          voice,
          rate,
          provider: ttsConfig.provider || ttsProvider,
          api_key: ttsConfig.api_key || "",
        }),
      });
      const data = await res.json();
      if (res.ok) {
        const audio = new Audio(data.audio_url.startsWith("http") ? data.audio_url : `${API_BASE}${data.audio_url}`);
        audio.play().catch(e => console.error("Play error:", e));
      } else {
        alert("试听失败: " + (data.detail || "未知错误"));
      }
    } catch (e: any) {
      alert("试听失败: " + e.message);
    } finally {
      setPreviewing(false);
    }
  };

  // Step 4: Compose Video
  const composeVideo = async () => {
    setLoading(true);
    setProgress("正在合成视频...");
    try {
      const projectId = Date.now().toString(36);
      const res = await fetch(`${API_BASE}/api/video/compose`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_id: projectId,
          scenes: scenes.map((s, i) => ({
            index: i,
            narration: s.narration,
            image_path: s.image_url || "",
            audio_path: s.audio_url || "",
            duration: s.duration,
          })),
          bgm_path: bgm,
          resolution,
        }),
      });
      const data = await res.json();
      if (res.ok) {
        setVideoUrl(`${API_BASE}${data.video_url}`);
      } else {
        throw new Error(data.detail || "合成失败");
      }
    } catch (e: any) {
      alert(`错误: ${e.message}`);
    } finally {
      setLoading(false);
      setProgress("");
    }
  };

  const updateScene = (idx: number, field: keyof Scene, value: string) => {
    const updated = [...scenes];
    (updated[idx] as any)[field] = value;
    setScenes(updated);
  };

  return (
    <div className={styles.studio}>
      {/* Header */}
      <header className={styles.studioHeader}>
        <button className={styles.backBtn} onClick={() => router.push("/")}>
          ← 返回首页
        </button>
        <h1>🎬 创作工作台</h1>
        <button className="btn btn-secondary" onClick={() => router.push("/settings")}>
          ⚙️ API 设置
        </button>
      </header>

      {/* Step Indicator */}
      <div className={styles.stepIndicator}>
        {STEPS.map((s) => (
          <div key={s.id} className={`${styles.stepDot} ${step === s.id ? styles.stepActive : ""} ${step > s.id ? styles.stepDone : ""}`}>
            <span className={styles.stepDotIcon}>{step > s.id ? "✓" : s.icon}</span>
            <span className={styles.stepDotLabel}>{s.label}</span>
          </div>
        ))}
      </div>

      {/* Loading overlay */}
      {loading && (
        <div className={styles.loadingOverlay}>
          <div className={styles.spinner} />
          <p>{progress}</p>
        </div>
      )}

      {/* Step Content */}
      <div className={styles.stepContent}>
        {/* Step 1: Content */}
        {step === 1 && (
          <div className={styles.stepPanel}>
            <h2>📝 内容创作</h2>
            <p className={styles.stepDesc}>输入一个主题，AI 帮你生成完整的视频脚本</p>

            <div className={styles.formGrid}>
              <div className="input-group">
                <label>视频主题 *</label>
                <input className="input" placeholder="例如：为什么要养成阅读习惯" value={topic} onChange={(e) => setTopic(e.target.value)} />
              </div>

              <div className={styles.formRow}>
                <div className="input-group">
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                    <label style={{ marginBottom: 0 }}>内容风格</label>
                    <button
                      onClick={() => setStyleMode(m => m === "select" ? "custom" : "select")}
                      style={{ fontSize: "12px", background: "none", border: "none", color: "var(--color-primary)", cursor: "pointer", padding: 0 }}
                    >
                      {styleMode === "select" ? "✏️ 自定义" : "📋 列表选择"}
                    </button>
                  </div>
                  {styleMode === "select" ? (
                    <select className="input" value={style} onChange={(e) => setStyle(e.target.value)}>
                      {STYLES.map((s) => (<option key={s} value={s}>{s}</option>))}
                    </select>
                  ) : (
                    <input className="input" value={style} onChange={(e) => setStyle(e.target.value)} placeholder="输入自定义风格..." autoFocus />
                  )}
                </div>
                <div className="input-group">
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                    <label style={{ marginBottom: 0 }}>视频时长: {duration} 分钟</label>
                  </div>
                  <input
                    type="range"
                    className="input"
                    min="2"
                    max="10"
                    step="2"
                    value={duration}
                    onChange={(e) => setDuration(Number(e.target.value))}
                    style={{ padding: 0 }}
                  />
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", color: "var(--color-text-secondary)", marginTop: "4px" }}>
                    <span>2分</span>
                    <span>4分</span>
                    <span>6分</span>
                    <span>8分</span>
                    <span>10分</span>
                  </div>
                </div>
              </div>
            </div>

            <div className={styles.stepActions}>
              <button className="btn btn-primary btn-lg" onClick={generateScript} disabled={!topic.trim()}>
                ✨ AI 生成脚本
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Visual */}
        {step === 2 && (
          <div className={styles.stepPanel}>
            <h2>🎨 视觉风格</h2>
            <p className={styles.stepDesc}>设置 AI 配图风格，为每个分镜生成精美插图</p>

            <div className={styles.formGrid}>
              <div className="input-group">
                <label>画面风格提示词（英文）</label>
                <textarea className="input" value={stylePrefix} onChange={(e) => setStylePrefix(e.target.value)} rows={2} />
              </div>

              <div className={styles.formRow}>
                <div className="input-group">
                  <label>画面比例</label>
                  <select className="input" value={resolution} onChange={(e) => setResolution(e.target.value)}>
                    <option value="1080x1920">竖屏 9:16 (1080×1920)</option>
                    <option value="1920x1080">横屏 16:9 (1920×1080)</option>
                    <option value="1024x1024">方形 1:1 (1024×1024)</option>
                  </select>
                </div>
                <div className="input-group">
                  <label>图像供应商</label>
                  <select className="input" value={imageProvider} onChange={(e) => setImageProvider(e.target.value)}>
                    {providers?.image?.map((p: any) => (
                      <option key={p.id} value={p.id}>{p.name}</option>
                    )) || <option value="dall-e">加载中...</option>}
                  </select>
                </div>
              </div>
            </div>

            {/* Script Preview */}
            <div className={styles.scriptPreview}>
              <h3>📜 脚本预览 - {title}</h3>
              <div className={styles.sceneList}>
                {scenes.map((s, i) => (
                  <div key={i} className={styles.sceneItem}>
                    <div className={styles.sceneNum}>#{s.index}</div>
                    <div className={styles.sceneContent}>
                      <textarea className="input" value={s.narration} onChange={(e) => updateScene(i, "narration", e.target.value)} rows={2} />
                      <details>
                        <summary className={styles.promptToggle}>🎨 图像提示词</summary>
                        <textarea className="input" value={s.image_prompt} onChange={(e) => updateScene(i, "image_prompt", e.target.value)} rows={2} />
                      </details>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className={styles.stepActions}>
              <button className="btn btn-secondary" onClick={() => setStep(1)}>← 上一步</button>
              <button className="btn btn-primary btn-lg" onClick={generateImages}>
                🎨 生成配图
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Voice */}
        {step === 3 && (
          <div className={styles.stepPanel}>
            <h2>🎤 语音配置</h2>
            <p className={styles.stepDesc}>选择语音音色和背景音乐</p>

            <div className={styles.formGrid}>
              <div className={styles.formRow}>
                <div className="input-group">
                  <label>TTS 引擎</label>
                  <select className="input" value={ttsProvider} onChange={(e) => setTtsProvider(e.target.value)}>
                    {providers?.tts?.map((p: any) => (
                      <option key={p.id} value={p.id}>{p.name}</option>
                    )) || <option value="edge-tts">加载中...</option>}
                  </select>
                </div>
                <div className="input-group">
                  <label>语音音色</label>
                  <div style={{ display: "flex", gap: "8px" }}>
                    <select className="input" value={voice} onChange={(e) => setVoice(e.target.value)} style={{ flex: 1 }}>
                      <optgroup label="中文女声">
                        <option value="zh-CN-XiaoxiaoNeural">晓晓（温柔）</option>
                        <option value="zh-CN-XiaohanNeural">晓涵（知性）</option>
                        <option value="zh-CN-XiaomoNeural">晓墨（活力）</option>
                        <option value="zh-CN-XiaoshuangNeural">晓双（童声）</option>
                      </optgroup>
                      <optgroup label="中文男声">
                        <option value="zh-CN-YunxiNeural">云希（青年）</option>
                        <option value="zh-CN-YunjianNeural">云健（沉稳）</option>
                        <option value="zh-CN-YunyangNeural">云扬（新闻）</option>
                      </optgroup>
                    </select>
                    <button
                      className="btn btn-secondary"
                      onClick={previewVoice}
                      disabled={previewing}
                      title="试听当前音色"
                      style={{ padding: "10px 12px", border: "1px solid var(--color-border)" }}
                    >
                      {previewing ? "⏳" : "🔊"}
                    </button>
                  </div>
                </div>
              </div>

              <div className={styles.formRow}>
                <div className="input-group">
                  <label>语速调节</label>
                  <select className="input" value={rate} onChange={(e) => setRate(e.target.value)}>
                    <option value="-20%">较慢</option>
                    <option value="-10%">稍慢</option>
                    <option value="+0%">正常</option>
                    <option value="+10%">稍快</option>
                    <option value="+20%">较快</option>
                  </select>
                </div>
                <div className="input-group">
                  <label>背景音乐</label>
                  <select className="input" value={bgm} onChange={(e) => setBgm(e.target.value)}>
                    <option value="">无 BGM</option>
                    <option value="default.mp3">默认轻音乐</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Scenes with images */}
            <div className={styles.scriptPreview}>
              <h3>📋 分镜预览</h3>
              <div className={styles.sceneGrid}>
                {scenes.map((s, i) => (
                  <div key={i} className={styles.sceneCard}>
                    {s.image_url && (
                      <div className={styles.sceneImage}>
                        <img src={s.image_url.startsWith("http") ? s.image_url : `${API_BASE}${s.image_url}`} alt={`分镜 ${s.index}`} />
                      </div>
                    )}
                    <div className={styles.sceneCardBody}>
                      <span className={styles.sceneCardNum}>#{s.index}</span>
                      <p>{s.narration}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className={styles.stepActions}>
              <button className="btn btn-secondary" onClick={() => setStep(2)}>← 上一步</button>
              <button className="btn btn-primary btn-lg" onClick={generateAudio}>
                🎤 合成语音
              </button>
            </div>
          </div>
        )}

        {/* Step 4: Preview & Compose */}
        {step === 4 && (
          <div className={styles.stepPanel}>
            <h2>🎬 预览合成</h2>
            <p className={styles.stepDesc}>检查各分镜效果，一键合成最终视频</p>

            <div className={styles.previewContainer}>
              {videoUrl ? (
                <div className={styles.videoResult}>
                  <video controls src={videoUrl} className={styles.videoPlayer} />
                  <div className={styles.videoActions}>
                    <a href={videoUrl} download className="btn btn-primary btn-lg">
                      ⬇️ 下载视频
                    </a>
                    <button className="btn btn-secondary" onClick={() => { setVideoUrl(""); setStep(1); setScenes([]); setTopic(""); }}>
                      🔄 创建新视频
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  <div className={styles.sceneGrid}>
                    {scenes.map((s, i) => (
                      <div key={i} className={styles.sceneCard}>
                        {s.image_url && (
                          <div className={styles.sceneImage}>
                            <img src={s.image_url.startsWith("http") ? s.image_url : `${API_BASE}${s.image_url}`} alt={`分镜 ${s.index}`} />
                          </div>
                        )}
                        <div className={styles.sceneCardBody}>
                          <span className={styles.sceneCardNum}>#{s.index}</span>
                          <p>{s.narration}</p>
                          {s.audio_url && <span className="badge badge-success">✓ 语音已合成</span>}
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className={styles.stepActions}>
                    <button className="btn btn-secondary" onClick={() => setStep(3)}>← 上一步</button>
                    <button className="btn btn-primary btn-lg" onClick={composeVideo}>
                      🎬 合成视频
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
