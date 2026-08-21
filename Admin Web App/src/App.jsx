import React, { useState, useRef, useEffect } from "react";
import {
  Palette,
  Type,
  Image as ImageIcon,
  Info,
  Phone,
  Save,
  Check,
  Upload,
  Loader2,
  Edit3,
  RefreshCw,
} from "lucide-react";

// In production, you would point this to the deployed backend URL (e.g. VITE_API_BASE=https://appex-adipec-concierge-backend.vercel.app)
const API_BASE = import.meta.env.VITE_API_BASE || "https://appex-adipec-concierge-backend.vercel.app";
const MINI_APP_URL = import.meta.env.VITE_MINI_APP_URL || "https://appex-adipec-concierge.vercel.app";

const DEFAULT_CONFIG = {
  brand_name: "APEX ASSET SUITE",
  event_name: "ADIPEC Concierge",
  tagline: "АО «НК «КазМунайГаз» · закрытый доступ делегатов",
  colors: {
    bg: "#141210",
    surface: "#1C1812",
    surface_hi: "#242017",
    border: "#39311F",
    border_hi: "#4E4327",
    gold: "#C9A227",
    gold_bright: "#E9CA73",
    text: "#F1EAD9",
    text_muted: "#9C9384",
    text_faint: "#6E6656",
    accent_danger: "#9C3F35",
    accent_success: "#748A6C",
  },
  fonts: {
    display: "'Fraunces', serif",
    body: "'Manrope', sans-serif",
    mono: "'IBM Plex Mono', monospace",
  },
  contact: {
    support_username: "@appex_support",
    support_phone: "+971500000000",
    support_hours: "10:00–20:00 (UTC+4)",
  },
  logo_url: null,
  banner_url: null,
};

// ── Shared Field Components ──
function ColorField({ label, value, onChange, cssVar }) {
  return (
    <div className="flex items-center justify-between py-2.5">
      <div className="flex items-center gap-2.5">
        <div
          className="w-7 h-7 rounded-lg border"
          style={{ background: value, borderColor: "var(--color-border)" }}
        />
        <div>
          <div style={{ fontFamily: "var(--font-body)", fontSize: 12.5, color: "var(--color-text)" }}>
            {label}
          </div>
          <div style={{ fontFamily: "var(--font-mono)", fontSize: 10, color: "var(--color-text-faint)" }}>
            {cssVar}
          </div>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-20 px-2 py-1 rounded text-center bg-transparent outline-none"
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: 11,
            color: "var(--color-text)",
            border: "1px solid var(--color-border)",
          }}
        />
        <input
          type="color"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-7 h-7 rounded cursor-pointer"
          style={{ border: "none", padding: 0 }}
        />
      </div>
    </div>
  );
}

function TextField({ label, value, onChange, placeholder }) {
  return (
    <div className="py-2">
      <label
        className="block mb-1.5"
        style={{ fontFamily: "var(--font-body)", fontSize: 12, color: "var(--color-text-muted)" }}
      >
        {label}
      </label>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full px-3 py-2 rounded-lg bg-transparent outline-none"
        style={{
          fontFamily: "var(--font-body)",
          fontSize: 13,
          color: "var(--color-text)",
          border: "1px solid var(--color-border)",
        }}
      />
    </div>
  );
}

function Section({ title, icon: Icon, children }) {
  return (
    <div
      className="rounded-2xl p-4 mb-4"
      style={{ background: "var(--color-surface)", border: "1px solid var(--color-border)" }}
    >
      <div className="flex items-center gap-2 mb-3 pb-2.5" style={{ borderBottom: "1px solid var(--color-border)" }}>
        <Icon size={15} color="var(--color-gold)" strokeWidth={1.6} />
        <span
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: 11,
            letterSpacing: 1.5,
            color: "var(--color-gold)",
            textTransform: "uppercase",
          }}
        >
          {title}
        </span>
      </div>
      {children}
    </div>
  );
}

function FileUploadField({ label, currentUrl, fieldName, adminToken, onUploaded }) {
  const [uploading, setUploading] = useState(false);
  const fileRef = useRef(null);

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("field", fieldName);
      formData.append("file", file);

      const res = await fetch(`${API_BASE}/api/tenant/default/upload`, {
        method: "POST",
        headers: { Authorization: `Bearer ${adminToken}` },
        body: formData,
      });

      if (res.ok) {
        const configRes = await fetch(`${API_BASE}/api/tenant/default`);
        if (configRes.ok) {
          const config = await configRes.json();
          onUploaded(config[fieldName]);
        }
      } else {
        const err = await res.json().catch(() => ({}));
        alert(`Ошибка загрузки: ${err.detail || res.status}`);
      }
    } catch (err) {
      alert(`Ошибка: ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="py-2">
      <label
        className="block mb-2"
        style={{ fontFamily: "var(--font-body)", fontSize: 12, color: "var(--color-text-muted)" }}
      >
        {label}
      </label>
      <div className="flex items-center gap-3">
        {currentUrl ? (
          <img
            src={currentUrl}
            alt={label}
            className="w-16 h-16 rounded-xl object-cover"
            style={{ border: "1px solid var(--color-border)" }}
          />
        ) : (
          <div
            className="w-16 h-16 rounded-xl flex items-center justify-center"
            style={{ background: "var(--color-surface-hi)", border: "1px dashed var(--color-border)" }}
          >
            <ImageIcon size={18} color="var(--color-text-faint)" />
          </div>
        )}
        <button
          onClick={() => fileRef.current?.click()}
          disabled={uploading}
          className="flex items-center gap-1.5 px-3 py-2 rounded-lg cursor-pointer"
          style={{
            background: "var(--color-surface-hi)",
            border: "1px solid var(--color-border)",
            fontFamily: "var(--font-body)",
            fontSize: 12,
            color: "var(--color-text)",
          }}
        >
          {uploading ? (
            <Loader2 size={13} className="animate-spin" color="var(--color-gold)" />
          ) : (
            <Upload size={13} color="var(--color-gold)" />
          )}
          {uploading ? "Загрузка…" : "Загрузить"}
        </button>
        <input ref={fileRef} type="file" accept="image/*" className="hidden" onChange={handleUpload} />
      </div>
    </div>
  );
}

// ── Main App ──
export default function App() {
  const [adminToken, setAdminToken] = useState("");
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [config, setConfig] = useState(DEFAULT_CONFIG);
  const [loading, setLoading] = useState(true);
  const iframeRef = useRef(null);

  // Fetch initial config
  useEffect(() => {
    fetch(`${API_BASE}/api/tenant/default`)
      .then(res => res.json())
      .then(data => {
        setConfig(prev => ({ ...prev, ...data }));
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load config:", err);
        setLoading(false);
      });
  }, []);

  const setColor = (key, value) => setConfig((prev) => ({ ...prev, colors: { ...prev.colors, [key]: value } }));
  const setField = (path, value) => {
    setConfig((prev) => {
      const parts = path.split(".");
      if (parts.length === 1) return { ...prev, [parts[0]]: value };
      const group = { ...prev[parts[0]], [parts[1]]: value };
      return { ...prev, [parts[0]]: group };
    });
  };

  const handleSave = async () => {
    if (!adminToken) return alert("Введите токен администратора");
    setSaving(true);
    setSaved(false);

    try {
      const res = await fetch(`${API_BASE}/api/tenant/default`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${adminToken}` },
        body: JSON.stringify({ tenant_id: "default", ...config }),
      });

      if (res.ok) {
        setIsAuthenticated(true);
        setSaved(true);
        // Clear sensitive fields after successful publish
        setAdminToken("");
        setConfig((prev) => ({ ...prev, logo_url: null, banner_url: null }));
        // Hide success badge after 6 seconds
        setTimeout(() => {
          setSaved(false);
          setIsAuthenticated(false);
        }, 6000);
        // Refresh iframe to load new settings from backend (timestamp forces a real reload)
        if (iframeRef.current) {
          iframeRef.current.src = `${MINI_APP_URL}?tenant=default&_t=${Date.now()}`;
        }
      } else {
        const err = await res.json().catch(() => ({}));
        alert(`Ошибка: ${err.detail || res.status}`);
        if (res.status === 401) setIsAuthenticated(false);
      }
    } catch (err) {
      alert(`Ошибка соединения: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="h-screen flex items-center justify-center">Загрузка...</div>;

  const COLOR_FIELDS = [
    { key: "bg", label: "Фон страницы", var: "--color-bg" },
    { key: "surface", label: "Фон карточек", var: "--color-surface" },
    { key: "surface_hi", label: "Выделенный фон", var: "--color-surface-hi" },
    { key: "border", label: "Граница", var: "--color-border" },
    { key: "border_hi", label: "Граница (яркая)", var: "--color-border-hi" },
    { key: "gold", label: "Акцент (золото)", var: "--color-gold" },
    { key: "gold_bright", label: "Акцент (светлое)", var: "--color-gold-bright" },
    { key: "text", label: "Основной текст", var: "--color-text" },
    { key: "text_muted", label: "Вторичный текст", var: "--color-text-muted" },
    { key: "text_faint", label: "Третичный текст", var: "--color-text-faint" },
    { key: "accent_danger", label: "SOS / Опасность", var: "--color-accent-danger" },
    { key: "accent_success", label: "Успех", var: "--color-accent-success" },
  ];

  return (
    <div className="h-screen flex flex-col md:flex-row overflow-hidden bg-neutral-900 text-white">
      {/* Sidebar / Form */}
      <div className="w-full md:w-[460px] h-full flex flex-col border-r border-neutral-800 bg-[#141210]">
        <div className="flex items-center justify-between px-6 py-5 border-b border-neutral-800 shrink-0">
          <div className="flex items-center gap-3">
            <Edit3 size={20} color="var(--color-gold)" />
            <span className="font-medium text-lg tracking-wide">White-Label Engine</span>
          </div>
          <button
            onClick={handleSave}
            disabled={saving}
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg cursor-pointer transition-colors"
            style={{
              background: saved ? "var(--color-accent-success)" : "var(--color-gold)",
              color: "#1A1508",
              fontWeight: 600,
              fontSize: 13
            }}
          >
            {saving ? <Loader2 size={15} className="animate-spin" /> : saved ? <Check size={15} /> : <Save size={15} />}
            {saving ? "Сохранение…" : saved ? "Сохранено" : "Опубликовать"}
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-6" style={{ scrollbarWidth: "thin", scrollbarColor: "var(--color-border) transparent" }}>
          <Section title="Авторизация" icon={Info}>
            <TextField
              label="Токен администратора (ADMIN_SECRET)"
              value={adminToken}
              onChange={setAdminToken}
              placeholder="Вставьте ADMIN_SECRET"
            />
            {isAuthenticated && (
              <div className="flex items-center gap-1.5 mt-2" style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--color-accent-success)" }}>
                <Check size={13} /> Успешно авторизован
              </div>
            )}
          </Section>

          <Section title="Идентичность бренда" icon={Info}>
            <TextField label="Название бренда" value={config.brand_name} onChange={(v) => setField("brand_name", v)} placeholder="APEX ASSET SUITE" />
            <TextField label="Название события" value={config.event_name} onChange={(v) => setField("event_name", v)} placeholder="ADIPEC Concierge" />
            <TextField label="Подзаголовок" value={config.tagline} onChange={(v) => setField("tagline", v)} placeholder="Описание для делегатов" />
          </Section>

          <Section title="Медиа" icon={ImageIcon}>
            <FileUploadField
              label="Логотип (Base64)"
              currentUrl={config.logo_url}
              fieldName="logo_url"
              adminToken={adminToken}
              onUploaded={(url) => setConfig((prev) => ({ ...prev, logo_url: url }))}
            />
            <FileUploadField
              label="Баннер (Base64)"
              currentUrl={config.banner_url}
              fieldName="banner_url"
              adminToken={adminToken}
              onUploaded={(url) => setConfig((prev) => ({ ...prev, banner_url: url }))}
            />
          </Section>

          <Section title="Палитра цветов" icon={Palette}>
            {COLOR_FIELDS.map((cf) => (
              <ColorField key={cf.key} label={cf.label} value={config.colors[cf.key]} onChange={(v) => setColor(cf.key, v)} cssVar={cf.var} />
            ))}
          </Section>

          <Section title="Типографика" icon={Type}>
            <TextField label="Шрифт заголовков" value={config.fonts.display} onChange={(v) => setField("fonts.display", v)} />
            <TextField label="Основной шрифт" value={config.fonts.body} onChange={(v) => setField("fonts.body", v)} />
            <TextField label="Моноширинный шрифт" value={config.fonts.mono} onChange={(v) => setField("fonts.mono", v)} />
          </Section>

          <Section title="Контакты поддержки" icon={Phone}>
            <TextField label="Telegram-аккаунт" value={config.contact.support_username} onChange={(v) => setField("contact.support_username", v)} />
            <TextField label="Телефон" value={config.contact.support_phone} onChange={(v) => setField("contact.support_phone", v)} />
            <TextField label="Часы работы" value={config.contact.support_hours} onChange={(v) => setField("contact.support_hours", v)} />
          </Section>

          <button
            onClick={() => { if (confirm("Сбросить все локальные изменения?")) window.location.reload(); }}
            className="w-full py-3 mt-2 mb-8 rounded-lg flex items-center justify-center gap-2 cursor-pointer transition-colors hover:bg-neutral-800"
            style={{ border: "1px solid var(--color-border)", fontSize: 13, color: "var(--color-text-muted)" }}
          >
            <RefreshCw size={14} /> Отменить изменения
          </button>
        </div>
      </div>

      {/* Preview Area */}
      <div className="hidden md:flex flex-1 flex-col items-center justify-center bg-[#0a0a0a] p-8 relative">
        <div className="absolute top-6 left-6 text-neutral-500 font-mono text-xs tracking-widest uppercase">
          Live Preview (Telegram Mini App)
        </div>

        {/* iPhone Mockup Frame */}
        <div
          className="relative rounded-[40px] border-[12px] border-neutral-800 shadow-2xl"
          style={{ width: 390, height: 780, overflow: "hidden", background: "#000" }}
        >
          {/* Status bar with Dynamic Island */}
          <div
            className="absolute top-0 left-0 right-0 z-10 flex items-center justify-center"
            style={{
              height: 54,
              background: "#000",
              paddingTop: 10,
            }}
          >
            {/* Dynamic Island pill */}
            <div
              style={{
                width: 126,
                height: 34,
                background: "#000",
                borderRadius: 20,
                border: "1.5px solid #1a1a1a",
                boxShadow: "0 0 0 1px #222, 0 2px 12px rgba(0,0,0,0.9)",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                paddingLeft: 10,
                paddingRight: 12,
              }}
            >
              {/* Camera dot */}
              <div style={{ width: 10, height: 10, borderRadius: "50%", background: "#1a1a1a", border: "1px solid #2a2a2a" }} />
              {/* Face ID sensors */}
              <div style={{ display: "flex", gap: 3, alignItems: "center" }}>
                <div style={{ width: 3, height: 14, borderRadius: 2, background: "#1c1c1c" }} />
                <div style={{ width: 10, height: 10, borderRadius: "50%", background: "#1a1a1a", border: "1px solid #2a2a2a" }} />
              </div>
            </div>
          </div>

          {/* iframe — starts below Dynamic Island status bar */}
          <iframe
            ref={iframeRef}
            src={`${MINI_APP_URL}?tenant=default`}
            title="Preview"
            style={{
              position: "absolute",
              top: 54,
              left: 0,
              right: 0,
              bottom: 0,
              width: "100%",
              height: "calc(100% - 54px)",
              border: "none",
              background: "#000",
            }}
          />
        </div>
        <div className="mt-8 text-neutral-500 text-sm max-w-sm text-center">
          Предпросмотр обновляется после нажатия кнопки «Опубликовать». Приложение загрузит новые стили по API.
        </div>
      </div>
    </div>
  );
}
