"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import styles from "./settings.module.css";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface KeyConfig {
  provider: string;
  api_key: string;
  base_url: string;
  model: string;
}

interface ProviderInfo {
  id: string;
  name: string;
  base_url: string;
  models: string[];
}

interface ProviderGroup {
  llm: ProviderInfo[];
  image: ProviderInfo[];
  tts: ProviderInfo[];
}

const DEFAULT_KEYS: Record<string, KeyConfig> = {
  llm: { provider: "openai", api_key: "", base_url: "", model: "" },
  image: { provider: "dall-e", api_key: "", base_url: "", model: "" },
  tts: { provider: "edge-tts", api_key: "", base_url: "", model: "" },
};

export default function SettingsPage() {
  const router = useRouter();
  const [keys, setKeys] = useState<Record<string, KeyConfig>>(DEFAULT_KEYS);
  const [providers, setProviders] = useState<ProviderGroup | null>(null);
  const [testResults, setTestResults] = useState<Record<string, { success: boolean; message: string; latency: number } | null>>({});
  const [testing, setTesting] = useState<Record<string, boolean>>({});

  // Load from localStorage
  useEffect(() => {
    const saved = localStorage.getItem("ai_video_keys");
    if (saved) {
      try {
        setKeys({ ...DEFAULT_KEYS, ...JSON.parse(saved) });
      } catch {}
    }
    fetchProviders();
  }, []);

  const fetchProviders = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/keys/providers`);
      if (res.ok) {
        setProviders(await res.json());
      }
    } catch {
      // Backend might not be running
    }
  };

  const updateKey = (service: string, field: keyof KeyConfig, value: string) => {
    setKeys((prev) => ({
      ...prev,
      [service]: { ...prev[service], [field]: value },
    }));
  };

  const saveKeys = () => {
    localStorage.setItem("ai_video_keys", JSON.stringify(keys));
    alert("✅ 配置已保存");
  };

  const testConnection = async (service: string) => {
    const config = keys[service];
    if (!config.api_key && config.provider !== "edge-tts") {
      setTestResults((prev) => ({ ...prev, [service]: { success: false, message: "请先填写 API Key", latency: 0 } }));
      return;
    }

    setTesting((prev) => ({ ...prev, [service]: true }));
    setTestResults((prev) => ({ ...prev, [service]: null }));

    try {
      const res = await fetch(`${API_BASE}/api/keys/test`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config),
      });
      const data = await res.json();
      setTestResults((prev) => ({
        ...prev,
        [service]: { success: data.success, message: data.message, latency: data.latency_ms },
      }));
    } catch (e: any) {
      setTestResults((prev) => ({
        ...prev,
        [service]: { success: false, message: `连接失败: ${e.message}`, latency: 0 },
      }));
    } finally {
      setTesting((prev) => ({ ...prev, [service]: false }));
    }
  };

  const handleProviderChange = (service: string, providerId: string) => {
    const group = service === "llm" ? providers?.llm : service === "image" ? providers?.image : providers?.tts;
    const provider = group?.find((p) => p.id === providerId);
    if (provider) {
      updateKey(service, "provider", providerId);
      updateKey(service, "base_url", provider.base_url);
      if (provider.models.length > 0) {
        updateKey(service, "model", provider.models[0]);
      }
    }
  };

  const renderServiceCard = (
    service: string,
    icon: string,
    label: string,
    providerList: ProviderInfo[] | undefined,
  ) => {
    const config = keys[service];
    const result = testResults[service];
    const isTesting = testing[service];

    return (
      <div className={styles.serviceCard}>
        <div className={styles.serviceHeader}>
          <span className={styles.serviceIcon}>{icon}</span>
          <h3>{label}</h3>
        </div>

        <div className={styles.serviceBody}>
          {/* Provider selector */}
          <div className="input-group">
            <label>服务供应商</label>
            <select className="input" value={config.provider} onChange={(e) => handleProviderChange(service, e.target.value)}>
              {providerList?.map((p) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              )) || <option>{config.provider}</option>}
            </select>
          </div>

          {/* API Key */}
          {config.provider !== "edge-tts" && (
            <div className="input-group">
              <label>API Key</label>
              <input
                className="input"
                type="password"
                placeholder="sk-..."
                value={config.api_key}
                onChange={(e) => updateKey(service, "api_key", e.target.value)}
              />
            </div>
          )}

          {/* Base URL */}
          {config.provider !== "edge-tts" && (
            <div className="input-group">
              <label>Base URL <span className={styles.labelHint}>(可选，使用默认值)</span></label>
              <input
                className="input"
                placeholder={providerList?.find((p) => p.id === config.provider)?.base_url || ""}
                value={config.base_url}
                onChange={(e) => updateKey(service, "base_url", e.target.value)}
              />
            </div>
          )}

          {/* Model */}
          {config.provider !== "edge-tts" && (
            <div className="input-group">
              <label>模型</label>
              <select className="input" value={config.model} onChange={(e) => updateKey(service, "model", e.target.value)}>
                {providerList
                  ?.find((p) => p.id === config.provider)
                  ?.models.map((m) => (
                    <option key={m} value={m}>{m}</option>
                  )) || <option value="">默认</option>}
              </select>
            </div>
          )}

          {/* Test Button */}
          <div className={styles.testBar}>
            <button className="btn btn-secondary" onClick={() => testConnection(service)} disabled={isTesting}>
              {isTesting ? "测试中..." : "🔌 测试连接"}
            </button>
            {result && (
              <div className={`${styles.testResult} ${result.success ? styles.testSuccess : styles.testFail}`}>
                <span>{result.success ? "✅" : "❌"}</span>
                <span>{result.message}</span>
                {result.latency > 0 && <span className={styles.latency}> ({result.latency}ms)</span>}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className={styles.settings}>
      <header className={styles.header}>
        <button className={styles.backBtn} onClick={() => router.push("/")}>
          ← 返回首页
        </button>
        <h1>⚙️ API 密钥管理</h1>
        <button className="btn btn-primary" onClick={saveKeys}>
          💾 保存配置
        </button>
      </header>

      <div className={styles.content}>
        <p className={styles.desc}>
          配置 AI 服务的 API Key。密钥仅存储在您的浏览器本地，不会上传到任何服务器。
        </p>

        <div className={styles.serviceGrid}>
          {renderServiceCard("llm", "🧠", "大语言模型 (LLM)", providers?.llm)}
          {renderServiceCard("image", "🎨", "图像生成", providers?.image)}
          {renderServiceCard("tts", "🎤", "语音合成 (TTS)", providers?.tts)}
        </div>

        <div className={styles.bottomActions}>
          <button className="btn btn-primary btn-lg" onClick={saveKeys}>
            💾 保存所有配置
          </button>
        </div>
      </div>
    </div>
  );
}
