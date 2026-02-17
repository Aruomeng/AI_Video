"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import styles from "./copycat.module.css";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface AnalysisStyle {
  tags: string[];
  color_tone: string;
  composition: string;
  transition_style: string;
  subtitle_style: string;
}

interface AnalysisScene {
  index: number;
  description: string;
  narration: string;
  image_prompt: string;
  duration: number;
}

interface AnalysisReport {
  title: string;
  summary: string;
  style: AnalysisStyle;
  scenes: AnalysisScene[];
  recommended_template: string;
  recommended_voice: string;
  recommended_bgm: string;
  total_duration: number;
}

export default function CopycatPage() {
  const router = useRouter();
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<AnalysisReport | null>(null);

  const getConfig = (provider: string) => {
    if (typeof window === "undefined") return {};
    const keys = JSON.parse(localStorage.getItem("ai_video_keys") || "{}");
    return keys[provider] || {};
  };

  const analyzeVideo = async () => {
    const llmConfig = getConfig("llm");
    if (!llmConfig.api_key) {
      alert("请先在「API 设置」中配置 LLM API Key");
      router.push("/settings");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/analyze/video`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          video_url: url,
          llm_provider: llmConfig.provider || "openai",
          api_key: llmConfig.api_key,
          base_url: llmConfig.base_url || "",
          model: llmConfig.model || "",
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "分析失败");
      setReport(data);
    } catch (e: any) {
      alert(`分析失败: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  const applyToStudio = () => {
    if (!report) return;
    // Save analysis data to sessionStorage for studio page to read
    sessionStorage.setItem("copycat_data", JSON.stringify(report));
    router.push("/studio?from=copycat");
  };

  return (
    <div className={styles.copycat}>
      {/* Header */}
      <header className={styles.header}>
        <button className={styles.backBtn} onClick={() => router.push("/")}>
          ← 返回首页
        </button>
        <h1>🔍 一键模仿竞品视频</h1>
        <div />
      </header>

      {/* Input */}
      <div className={styles.inputSection}>
        <div className={styles.inputCard}>
          <h2>粘贴视频链接</h2>
          <p>支持抖音、B站、YouTube 等主流平台的视频链接</p>
          <div className={styles.urlInput}>
            <input
              className="input"
              placeholder="https://www.bilibili.com/video/BV..."
              value={url}
              onChange={(e) => setUrl(e.target.value)}
            />
            <button className="btn btn-primary" onClick={analyzeVideo} disabled={loading || !url.trim()}>
              {loading ? "分析中..." : "🔍 开始分析"}
            </button>
          </div>
          <div className={styles.platformTags}>
            <span>支持平台：</span>
            <span className={styles.platformTag}>📺 B站</span>
            <span className={styles.platformTag}>🎵 抖音</span>
            <span className={styles.platformTag}>▶️ YouTube</span>
            <span className={styles.platformTag}>📱 快手</span>
            <span className={styles.platformTag}>🔗 直链</span>
          </div>
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className={styles.loadingSection}>
          <div className={styles.loadingCard}>
            <div className={styles.spinner} />
            <h3>AI 正在分析视频...</h3>
            <div className={styles.loadingSteps}>
              <div className={styles.loadingStep}>📥 下载视频</div>
              <div className={styles.loadingStep}>🎞️ 提取关键帧</div>
              <div className={styles.loadingStep}>🤖 AI 智能分析</div>
              <div className={styles.loadingStep}>📊 生成报告</div>
            </div>
          </div>
        </div>
      )}

      {/* Report */}
      {report && !loading && (
        <div className={styles.reportSection}>
          <div className={styles.reportHeader}>
            <div>
              <h2>📊 分析报告</h2>
              <p className={styles.reportTitle}>{report.title}</p>
            </div>
            <button className="btn btn-primary btn-lg" onClick={applyToStudio}>
              ⚡ 应用到工作台
            </button>
          </div>

          {/* Summary */}
          <div className={styles.reportCard}>
            <h3>📝 内容概述</h3>
            <p>{report.summary}</p>
          </div>

          {/* Style */}
          <div className={styles.reportCard}>
            <h3>🎨 风格分析</h3>
            <div className={styles.styleGrid}>
              <div className={styles.styleItem}>
                <span className={styles.styleLabel}>风格标签</span>
                <div className={styles.tagGroup}>
                  {report.style.tags.map((tag, i) => (
                    <span key={i} className={styles.tag}>{tag}</span>
                  ))}
                </div>
              </div>
              <div className={styles.styleItem}>
                <span className={styles.styleLabel}>色调</span>
                <span>{report.style.color_tone}</span>
              </div>
              <div className={styles.styleItem}>
                <span className={styles.styleLabel}>构图</span>
                <span>{report.style.composition}</span>
              </div>
              <div className={styles.styleItem}>
                <span className={styles.styleLabel}>转场</span>
                <span>{report.style.transition_style}</span>
              </div>
              <div className={styles.styleItem}>
                <span className={styles.styleLabel}>字幕</span>
                <span>{report.style.subtitle_style}</span>
              </div>
            </div>
          </div>

          {/* Recommendations */}
          <div className={styles.recGrid}>
            <div className={styles.recCard}>
              <span className={styles.recIcon}>🎨</span>
              <span className={styles.recLabel}>推荐模板</span>
              <span className={styles.recValue}>{report.recommended_template}</span>
            </div>
            <div className={styles.recCard}>
              <span className={styles.recIcon}>🎤</span>
              <span className={styles.recLabel}>推荐音色</span>
              <span className={styles.recValue}>{report.recommended_voice}</span>
            </div>
            <div className={styles.recCard}>
              <span className={styles.recIcon}>🎵</span>
              <span className={styles.recLabel}>推荐BGM</span>
              <span className={styles.recValue}>{report.recommended_bgm}</span>
            </div>
            <div className={styles.recCard}>
              <span className={styles.recIcon}>⏱</span>
              <span className={styles.recLabel}>总时长</span>
              <span className={styles.recValue}>{report.total_duration}s</span>
            </div>
          </div>

          {/* Scenes */}
          <div className={styles.reportCard}>
            <h3>📋 分镜还原 ({report.scenes.length} 个场景)</h3>
            <div className={styles.sceneTimeline}>
              {report.scenes.map((s, i) => (
                <div key={i} className={styles.timelineItem}>
                  <div className={styles.timelineDot}>
                    <span>{s.index}</span>
                  </div>
                  <div className={styles.timelineContent}>
                    <div className={styles.timelineMeta}>
                      <span className="badge badge-primary">{s.duration}s</span>
                    </div>
                    <p className={styles.timelineDesc}>{s.description}</p>
                    <p className={styles.timelineNarration}>💬 {s.narration}</p>
                    <details>
                      <summary className={styles.promptToggle}>🎨 生图提示词</summary>
                      <p className={styles.promptText}>{s.image_prompt}</p>
                    </details>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Bottom CTA */}
          <div className={styles.bottomCTA}>
            <button className="btn btn-primary btn-lg" onClick={applyToStudio}>
              ⚡ 将分析结果应用到创作工作台，生成同款视频
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
