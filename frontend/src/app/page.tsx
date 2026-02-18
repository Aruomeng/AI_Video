"use client";
import { useRouter } from "next/navigation";
import Icon from "@/components/Icon";
import styles from "./page.module.css";

const FEATURES = [
  {
    iconName: "edit",
    title: "AI 智能文案",
    desc: "输入主题，AI 自动创作分镜脚本，故事逻辑连贯",
    gradient: "linear-gradient(135deg, #6c5ce7, #a29bfe)",
  },
  {
    iconName: "palette",
    title: "AI 生成配图",
    desc: "每个分镜自动生成精美 AI 插图，支持多种风格",
    gradient: "linear-gradient(135deg, #00cec9, #55efc4)",
  },
  {
    iconName: "microphone",
    title: "智能语音合成",
    desc: "多种音色可选，免费 Edge-TTS 或高品质 OpenAI TTS",
    gradient: "linear-gradient(135deg, #fd79a8, #e84393)",
  },
  {
    iconName: "film",
    title: "一键合成视频",
    desc: "自动添加字幕、BGM、转场，输出专业短视频",
    gradient: "linear-gradient(135deg, #e17055, #fdcb6e)",
  },
];

const STEPS = [
  { num: "01", title: "输入主题", desc: "一句话描述你的视频主题", iconName: "lightbulb" },
  { num: "02", title: "AI 创作", desc: "自动生成文案、配图、语音", iconName: "cpu" },
  { num: "03", title: "个性定制", desc: "调整风格、音色、模板", iconName: "palette" },
  { num: "04", title: "导出视频", desc: "一键合成专业短视频", iconName: "film" },
];

export default function LandingPage() {
  const router = useRouter();

  return (
    <div className={styles.landing}>
      {/* Header */}
      <header className={styles.header}>
        <div className={styles.headerInner}>
          <div className={styles.logo}>
            <span className={styles.logoIcon}><Icon name="film" size={24} /></span>
            <span className={styles.logoText}>AI Video</span>
          </div>
          <nav className={styles.nav}>
            <a href="#features">功能</a>
            <a href="#workflow">流程</a>
            <a href="#copycat">竞品模仿</a>
            <button className="btn btn-secondary" onClick={() => router.push("/settings")}>
              <Icon name="settings" size={16} /> API 设置
            </button>
            <button className="btn btn-primary" onClick={() => router.push("/studio")}>
              开始创作
            </button>
          </nav>
          <button
            className={styles.mobileMenuBtn}
            onClick={() => {
              document.querySelector(`.${styles.nav}`)?.classList.toggle(styles.navOpen);
            }}
          >
            <Icon name="menu" size={22} />
          </button>
        </div>
      </header>

      {/* Hero */}
      <section className={styles.hero}>
        <div className={styles.heroGlow} />
        <div className={styles.heroContent}>
          <div className={styles.heroBadge}>
            <span className={styles.heroBadgeDot} />
            <Icon name="rocket" size={14} /> 轻量化 · 零 ComfyUI · 云端驱动
          </div>
          <h1 className={styles.heroTitle}>
            <span className={styles.heroTitleGradient}>AI 全自动</span>
            <br />
            短视频生成引擎
          </h1>
          <p className={styles.heroSubtitle}>
            输入一个主题，3 分钟生成一个专业短视频。支持 OpenAI / DeepSeek / 通义千问 等多种 AI 模型，高度个性化定制。
          </p>
          <div className={styles.heroCTA}>
            <button className="btn btn-primary btn-lg" onClick={() => router.push("/studio")}>
              <Icon name="sparkles" size={18} /> 立即创作
            </button>
            <button className="btn btn-secondary btn-lg" onClick={() => router.push("/copycat")}>
              <Icon name="search" size={18} /> 模仿竞品视频
            </button>
          </div>
          <div className={styles.heroStats}>
            <div className={styles.statItem}>
              <span className={styles.statValue}>3+</span>
              <span className={styles.statLabel}>AI 供应商</span>
            </div>
            <div className={styles.statDivider} />
            <div className={styles.statItem}>
              <span className={styles.statValue}>免费</span>
              <span className={styles.statLabel}>Edge-TTS 语音</span>
            </div>
            <div className={styles.statDivider} />
            <div className={styles.statItem}>
              <span className={styles.statValue}>0</span>
              <span className={styles.statLabel}>本地依赖</span>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className={styles.features}>
        <div className="container">
          <h2 className={styles.sectionTitle}>
            <span className={styles.sectionIcon}><Icon name="sparkles" size={22} /></span>
            核心功能
          </h2>
          <p className={styles.sectionSubtitle}>
            无需视频剪辑经验，AI 帮你搞定一切
          </p>
          <div className={styles.featuresGrid}>
            {FEATURES.map((f, i) => (
              <div key={i} className={`${styles.featureCard} card`}>
                <div className={styles.featureIcon} style={{ background: f.gradient }}>
                  <Icon name={f.iconName} size={26} />
                </div>
                <h3>{f.title}</h3>
                <p>{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Workflow */}
      <section id="workflow" className={styles.workflow}>
        <div className="container">
          <h2 className={styles.sectionTitle}>
            <span className={styles.sectionIcon}><Icon name="bar-chart" size={22} /></span>
            创作流程
          </h2>
          <p className={styles.sectionSubtitle}>
            四步完成视频创作，简单到难以置信
          </p>
          <div className={styles.stepsContainer}>
            {STEPS.map((s, i) => (
              <div key={i} className={styles.stepItem}>
                <div className={styles.stepNum}>{s.num}</div>
                <div className={styles.stepIcon}><Icon name={s.iconName} size={24} /></div>
                <h3>{s.title}</h3>
                <p>{s.desc}</p>
                {i < STEPS.length - 1 && <div className={styles.stepConnector} />}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Copycat Feature */}
      <section id="copycat" className={styles.copycatSection}>
        <div className="container">
          <div className={styles.copycatInner}>
            <div className={styles.copycatContent}>
              <div className="badge badge-primary" style={{ marginBottom: 12 }}>
                <Icon name="star" size={12} /> 独有功能
              </div>
              <h2>一键模仿竞品视频</h2>
              <p>
                粘贴任意短视频链接，AI 自动分析视频风格、色调、脚本结构、语音风格和 BGM，
                生成完整的分析报告，一键应用到创作工作台即可做出同款视频。
              </p>
              <ul className={styles.copycatList}>
                <li><Icon name="target" size={16} /> AI 智能识别画面风格与色调</li>
                <li><Icon name="file-text" size={16} /> 自动还原分镜脚本</li>
                <li><Icon name="microphone" size={16} /> 分析语音风格和 BGM 类型</li>
                <li><Icon name="zap" size={16} /> 一键应用到工作台生成同款</li>
              </ul>
              <button className="btn btn-primary btn-lg" onClick={() => router.push("/copycat")}>
                <Icon name="search" size={18} /> 试试看
              </button>
            </div>
            <div className={styles.copycatVisual}>
              <div className={styles.copycatCard}>
                <div className={styles.copycatCardHeader}>
                  <span><Icon name="search" size={16} /> 分析报告</span>
                  <span className="badge badge-success">完成</span>
                </div>
                <div className={styles.copycatCardBody}>
                  <div className={styles.tagGroup}>
                    <span className={styles.tag}>科技感</span>
                    <span className={styles.tag}>暗色调</span>
                    <span className={styles.tag}>快节奏</span>
                  </div>
                  <div className={styles.miniTimeline}>
                    <div className={styles.miniScene} style={{ width: "25%" }} />
                    <div className={styles.miniScene} style={{ width: "35%" }} />
                    <div className={styles.miniScene} style={{ width: "20%" }} />
                    <div className={styles.miniScene} style={{ width: "20%" }} />
                  </div>
                  <div className={styles.copycatMeta}>
                    <span><Icon name="ruler" size={14} /> 1080×1920</span>
                    <span><Icon name="clock" size={14} /> 45s</span>
                    <span><Icon name="microphone" size={14} /> 活力女声</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className={styles.cta}>
        <div className="container">
          <div className={styles.ctaInner}>
            <h2>准备好开始创作了吗？</h2>
            <p>配置好 API Key，即可免费生成你的第一个 AI 视频</p>
            <div className={styles.ctaButtons}>
              <button className="btn btn-primary btn-lg" onClick={() => router.push("/studio")}>
                <Icon name="sparkles" size={18} /> 开始创作
              </button>
              <button className="btn btn-secondary btn-lg" onClick={() => router.push("/settings")}>
                <Icon name="settings" size={18} /> 配置 API
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className={styles.footer}>
        <div className="container">
          <div className={styles.footerInner}>
            <div className={styles.footerBrand}>
              <span className={styles.logoIcon}><Icon name="film" size={20} /></span>
              <span>AI Video Generator</span>
            </div>
            <p className={styles.footerCopy}>
              轻量化 AI 视频生成引擎 · 不使用 ComfyUI · 云端 API 驱动
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
